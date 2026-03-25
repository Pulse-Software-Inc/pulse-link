#!/usr/bin/env python3
"""virtual companion chatbot router - health assistant"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/companion", tags=["virtual companion"])

# simple rule-based responses (no external ml services)
# this keeps costs down and works offline

@router.get("/status")
async def companion_status(current_user: dict = Depends(get_current_user)):
    """get companion status and quick health tip"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get recent data for personalized greeting
        recent = firestore.get_recent_biomarkers(uid, limit=5)
        
        # generate greeting based on time
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "good morning"
        elif 12 <= hour < 17:
            greeting = "good afternoon"
        elif 17 <= hour < 22:
            greeting = "good evening"
        else:
            greeting = "hello"
        
        # quick tip based on recent activity
        tip = "remember to drink water regularly"
        
        if recent:
            steps = sum(r.get("steps", 0) or 0 for r in recent)
            if steps < 3000:
                tip = "you've been sitting a lot - try a short walk"
            elif steps > 10000:
                tip = "great activity today! keep it up"
            
            heart_rates = [r.get("heart_rate") for r in recent if r.get("heart_rate")]
            if heart_rates:
                avg_hr = sum(heart_rates) / len(heart_rates)
                if avg_hr > 100:
                    tip = "your heart rate seems elevated - consider relaxing"
        
        return {
            "user_id": uid,
            "greeting": f"{greeting}, {current_user.get('email', 'friend')}!",
            "status": "online",
            "quick_tip": tip,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"DEBUG: companion status error: {e}")
        raise HTTPException(status_code=500, detail="failed to get companion status")


@router.post("/chat")
async def chat_with_companion(
    message: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    chat with the virtual companion.
    send a message and get health advice based on your data.
    """
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        user_message = message.get("message", "").lower().strip()
        
        if not user_message:
            raise HTTPException(status_code=400, detail="message cannot be empty")
        
        # get user data for context
        recent = firestore.get_recent_biomarkers(uid, limit=10)
        user = firestore.get_user(uid)
        
        # calculate stats
        total_steps = sum(r.get("steps", 0) or 0 for r in recent)
        heart_rates = [r.get("heart_rate") for r in recent if r.get("heart_rate")]
        avg_hr = int(sum(heart_rates) / len(heart_rates)) if heart_rates else 0
        max_hr = max(heart_rates) if heart_rates else 0
        
        # simple rule-based responses
        response = ""
        suggestions = []
        
        # greetings
        if any(word in user_message for word in ["hello", "hi", "hey"]):
            response = "hello! how are you feeling today? i can help with health tips or analyze your recent data."
        
        # steps / activity
        elif any(word in user_message for word in ["steps", "walking", "activity", "exercise"]):
            if total_steps < 5000:
                response = f"you've taken {total_steps} steps recently. that's a good start, but try to reach 10,000 for better health."
                suggestions = ["take a 10-minute walk", "use stairs instead of elevator", "park farther away"]
            elif total_steps < 10000:
                response = f"great job! you've taken {total_steps} steps. you're close to the 10,000 step goal."
                suggestions = ["take an evening walk", "do some light stretching"]
            else:
                response = f"excellent! you've taken {total_steps} steps. you're very active today!"
                suggestions = ["keep up the good work", "remember to stay hydrated"]
        
        # heart rate
        elif any(word in user_message for word in ["heart", "pulse", "bpm", "heart rate"]):
            if avg_hr == 0:
                response = "i don't have recent heart rate data. make sure your wearable device is connected."
            elif avg_hr < 60:
                response = f"your average heart rate is {avg_hr} bpm, which is on the lower side. this could be normal if you're fit, or you might be resting."
            elif avg_hr < 100:
                response = f"your average heart rate is {avg_hr} bpm, which is in the normal range."
            else:
                response = f"your average heart rate is {avg_hr} bpm with a max of {max_hr}. this seems elevated - consider relaxing or checking with a doctor if persistent."
                suggestions = ["practice deep breathing", "take a break and rest", "avoid caffeine"]
        
        # sleep
        elif any(word in user_message for word in ["sleep", "tired", "rest", "energy"]):
            response = "sleep is crucial for health. adults should aim for 7-9 hours per night."
            suggestions = ["maintain a consistent sleep schedule", "avoid screens 1 hour before bed", "keep your room cool and dark"]
        
        # diet / water
        elif any(word in user_message for word in ["water", "drink", "food", "eat", "diet", "calories"]):
            response = "staying hydrated and eating well is important. aim for 8 glasses of water daily."
            suggestions = ["drink a glass of water now", "eat more vegetables", "avoid sugary drinks"]
        
        # stress / mood
        elif any(word in user_message for word in ["stress", "anxious", "worried", "sad", "mood"]):
            response = "mental health is just as important as physical health. take time to care for yourself."
            suggestions = ["try meditation or deep breathing", "go for a walk outside", "talk to a friend or professional"]
        
        # help / what can you do
        elif any(word in user_message for word in ["help", "what can you do", "commands", "options"]):
            response = "i can help you with: tracking your steps, heart rate analysis, sleep tips, hydration reminders, and general health advice. just ask!"
        
        # data summary
        elif any(word in user_message for word in ["summary", "stats", "data", "how am i doing"]):
            response = f"here's your recent summary: {total_steps} steps recorded, average heart rate {avg_hr} bpm. keep tracking for more insights!"
        
        # default fallback
        else:
            responses = [
                "i'm here to help with your health. you can ask about your steps, heart rate, sleep, or general wellness tips.",
                "i'm your health companion. try asking about your activity levels or how to improve your health.",
                "i can analyze your biomarker data and give personalized suggestions. what would you like to know?"
            ]
            import random
            response = random.choice(responses)
        
        return {
            "user_id": uid,
            "message": user_message,
            "response": response,
            "suggestions": suggestions,
            "context": {
                "recent_steps": total_steps,
                "avg_heart_rate": avg_hr,
                "records_analyzed": len(recent)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: chat error: {e}")
        raise HTTPException(status_code=500, detail="chat processing failed")


@router.get("/tips")
async def get_daily_tips(
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """get personalized health tips based on user's data"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        recent = firestore.get_recent_biomarkers(uid, limit=20)
        
        tips = []
        
        # analyze data and generate tips
        if recent:
            total_steps = sum(r.get("steps", 0) or 0 for r in recent)
            avg_steps = total_steps / len(recent) if recent else 0
            
            heart_rates = [r.get("heart_rate") for r in recent if r.get("heart_rate")]
            avg_hr = sum(heart_rates) / len(heart_rates) if heart_rates else 0
            
            # step-based tips
            if avg_steps < 5000:
                tips.append({
                    "category": "activity",
                    "tip": "try to increase your daily steps. aim for at least 7,500 per day.",
                    "priority": "high"
                })
            elif avg_steps > 10000:
                tips.append({
                    "category": "activity",
                    "tip": "great activity levels! you're exceeding the recommended 10,000 steps.",
                    "priority": "low"
                })
            
            # heart rate tips
            if avg_hr > 90:
                tips.append({
                    "category": "heart_health",
                    "tip": "your resting heart rate seems elevated. consider stress reduction techniques.",
                    "priority": "medium"
                })
            
            # general tips
            tips.append({
                "category": "hydration",
                "tip": "drink at least 8 glasses of water today.",
                "priority": "medium"
            })
            
            tips.append({
                "category": "sleep",
                "tip": "aim for 7-9 hours of quality sleep tonight.",
                "priority": "medium"
            })
        else:
            # no data yet
            tips = [
                {"category": "general", "tip": "connect a wearable device to start tracking your health", "priority": "high"},
                {"category": "general", "tip": "regular health tracking helps identify patterns over time", "priority": "low"}
            ]
        
        # filter by category if provided
        if category:
            tips = [t for t in tips if t["category"] == category]
        
        return {
            "user_id": uid,
            "tips": tips,
            "count": len(tips),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"DEBUG: tips error: {e}")
        raise HTTPException(status_code=500, detail="failed to generate tips")


@router.get("/motivation")
async def get_motivation(current_user: dict = Depends(get_current_user)):
    """get a motivational message based on recent progress"""
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get all data for comparison
        all_data = firestore.get_all_biomarkers(uid)
        
        if len(all_data) < 5:
            return {
                "user_id": uid,
                "message": "every journey starts with a single step. keep tracking your health!",
                "streak_days": 0,
                "achievement": "getting started"
            }
        
        # simple streak calculation
        messages = [
            "you're doing great! consistency is key to better health.",
            "small steps every day lead to big changes. keep it up!",
            "your health journey is progressing well. proud of you!",
            "remember: progress, not perfection. you're on the right track!",
            "staying active helps both body and mind. great work!"
        ]
        
        import random
        
        return {
            "user_id": uid,
            "message": random.choice(messages),
            "records_tracked": len(all_data),
            "encouragement": "keep going! you're building healthy habits."
        }
        
    except Exception as e:
        print(f"DEBUG: motivation error: {e}")
        raise HTTPException(status_code=500, detail="failed to get motivation")
