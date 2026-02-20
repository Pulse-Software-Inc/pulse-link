from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from typing import Optional
import sys
import os
import csv
import io
from datetime import datetime

# fix path so we can import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user
from app.models.biomarker import ManualDataEntry

router = APIRouter(prefix="/biomarkers", tags=["biomarkers"])


@router.get("/real-time")
async def get_real_time_data(
    request: Request, current_user: dict = Depends(get_current_user)
):
    # import here to avoid circular imports
    from app.core import firestore
    
    try:
        data = firestore.get_recent_biomarkers(current_user["uid"], limit=5)
        return {"user_id": current_user["uid"], "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def get_connected_devices(
    request: Request, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        devices = firestore.get_user_devices(current_user["uid"])
        return {"user_id": current_user["uid"], "devices": devices, "count": len(devices)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {e}")


@router.post("/manual")
async def add_manual_data(
    request: Request, data: ManualDataEntry, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        entry_dict = data.dict()
        entry_id = firestore.add_manual_entry(current_user["uid"], entry_dict)
        
        # fetch the entry we just created
        entries = firestore.get_manual_entries(current_user["uid"])
        new_entry = None
        for e in entries:
            if e.get("entry_id") == entry_id:
                new_entry = e
                break
        
        if not new_entry:
            new_entry = entry_dict
        
        return {
            "message": "Entry created",
            "user_id": current_user["uid"],
            "entry_id": entry_id,
            "data": new_entry,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add entry: {e}")


@router.get("/manual")
async def get_manual_entries(
    request: Request, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        entries = firestore.get_manual_entries(current_user["uid"])
        return {"user_id": current_user["uid"], "entries": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/manual/{entry_id}")
async def delete_manual_entry(
    request: Request, entry_id: str, current_user: dict = Depends(get_current_user)
):
    from app.core import firestore
    
    try:
        success = firestore.delete_manual_entry(entry_id)
        if success:
            return {"message": "Entry deleted", "entry_id": entry_id}
        else:
            raise HTTPException(status_code=500, detail="Delete failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical")
async def get_historical_data(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    # TODO: implement this properly
    return {
        "user_id": current_user["uid"],
        "message": "Historical data not implemented yet",
        "date_range": {"start": start_date, "end": end_date},
    }


@router.get("/summary")
async def get_dashboard_summary(
    request: Request,
    period: Optional[str] = "daily",
    current_user: dict = Depends(get_current_user),
):
    """
    get dashboard summary data for the specified period.
    supports: daily, weekly, monthly
    """
    from app.core import firestore
    from datetime import datetime, timedelta
    
    try:
        uid = current_user["uid"]
        
        # validate period
        if period not in ["daily", "weekly", "monthly"]:
            period = "daily"
        
        # calculate date range based on period
        now = datetime.now()
        if period == "daily":
            days_back = 1
            steps_goal = 10000
            calories_goal = 500
            period_label = "today"
        elif period == "weekly":
            days_back = 7
            steps_goal = 70000  # 10k * 7
            calories_goal = 3500  # 500 * 7
            period_label = "this week"
        else:  # monthly
            days_back = 30
            steps_goal = 300000  # 10k * 30
            calories_goal = 15000  # 500 * 30
            period_label = "this month"
        
        # get all biomarkers and filter by date range
        all_biomarkers = firestore.get_all_biomarkers(uid)
        cutoff_date = now - timedelta(days=days_back)
        
        # filter records within the period
        filtered_records = []
        for record in all_biomarkers:
            timestamp = record.get("timestamp", "")
            if timestamp:
                try:
                    # parse timestamp
                    record_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if record_date >= cutoff_date:
                        filtered_records.append(record)
                except:
                    # skip records with bad timestamps
                    pass
        
        # if no records in period, fall back to recent data for demo
        if not filtered_records:
            filtered_records = firestore.get_recent_biomarkers(uid, limit=50)
        
        # fetch user devices
        devices = firestore.get_user_devices(uid)
        
        # calculate totals - sum for weekly/monthly, max for daily
        total_steps = 0
        total_calories = 0
        heart_rates = []
        last_sync = "never"
        
        for record in filtered_records:
            if "steps" in record and record["steps"]:
                if period == "daily":
                    total_steps = max(total_steps, record["steps"])
                else:
                    total_steps += record["steps"]
            if "calories" in record and record["calories"]:
                if period == "daily":
                    total_calories = max(total_calories, record["calories"])
                else:
                    total_calories += record["calories"]
            if "heart_rate" in record and record["heart_rate"]:
                heart_rates.append(record["heart_rate"])
            if "timestamp" in record:
                last_sync = record["timestamp"]
        
        # use defaults if no data
        if not heart_rates:
            heart_rates = [72]
        
        avg_heart_rate = sum(heart_rates) // len(heart_rates)
        resting_hr = min(heart_rates) if heart_rates else 68
        
        # format last sync time
        if last_sync != "never":
            last_sync = "2 mins ago"  # simplified for now
        
        # adjust labels based on period
        if period == "daily":
            steps_sub = "/10,000"
            steps_footer = "goal: 10,000 steps daily"
            cal_sub = "/500"
        elif period == "weekly":
            steps_sub = "/70,000"
            steps_footer = "goal: 70,000 steps weekly"
            cal_sub = "/3,500"
        else:  # monthly
            steps_sub = "/300,000"
            steps_footer = "goal: 300,000 steps monthly"
            cal_sub = "/15,000"
        
        # build dashboard card data format
        dashboard_data = [
            {
                "id": "Steps",
                "title": "Steps",
                "iconSrc": "/Steps_Icon.svg",
                "main": f"{total_steps:,}",
                "sub": steps_sub,
                "footer": steps_footer,
                "progress": {"value": total_steps, "max": steps_goal}
            },
            {
                "id": "Kcal",
                "title": "Calories Burned",
                "iconSrc": "/Calories_Icon.svg",
                "main": str(int(total_calories)),
                "sub": cal_sub,
                "footer": None,
                "progress": {"value": int(total_calories), "max": calories_goal}
            },
            {
                "id": "Heart",
                "title": "Heart Rate",
                "iconSrc": "/HeartRate_Icon.svg",
                "main": str(avg_heart_rate),
                "sub": "BPM",
                "footer": f"Resting: {resting_hr} BPM | Synced: {last_sync}",
                "progress": None
            }
        ]
        
        # return structured summary
        summary = {
            f"{period}_steps": {
                "current": total_steps,
                "goal": steps_goal,
                "percentage": min(100, int((total_steps / steps_goal) * 100)) if steps_goal > 0 else 0
            },
            f"{period}_calories": {
                "current": int(total_calories),
                "goal": calories_goal,
                "percentage": min(100, int((total_calories / calories_goal) * 100)) if calories_goal > 0 else 0
            },
            "heart_rate": {
                "current": avg_heart_rate,
                "resting": resting_hr,
                "last_sync": last_sync
            },
            "devices_connected": len(devices),
            "period": period,
            "days_in_period": days_back,
            "records_found": len(filtered_records)
        }
        
        print(f"DEBUG: {period} summary generated for user {uid}, {len(filtered_records)} records")
        
        return {
            "user_id": uid,
            "period": period,
            "date": now.isoformat(),
            "dashboard_data": dashboard_data,
            "summary": summary
        }
        
    except Exception as e:
        print(f"DEBUG: error in summary: {e}")
        raise HTTPException(status_code=500, detail=f"failed to get summary: {e}")


@router.get("/export")
async def export_biomarkers(
    request: Request,
    format: str = "csv",
    current_user: dict = Depends(get_current_user),
):
    # export biomarker data to csv (pdf coming later)
    from app.core import firestore
    
    try:
        uid = current_user["uid"]
        
        # get all biomarker data for this user
        biomarkers = firestore.get_all_biomarkers(uid)
        
        if format.lower() == "csv":
            # create csv in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # write header row
            writer.writerow([
                "timestamp", "device_id", "heart_rate", "steps", 
                "calories", "blood_pressure_systolic", "blood_pressure_diastolic",
                "sleep_hours", "mood"
            ])
            
            # write data rows
            for record in biomarkers:
                writer.writerow([
                    record.get("timestamp", ""),
                    record.get("device_id", ""),
                    record.get("heart_rate", ""),
                    record.get("steps", ""),
                    record.get("calories", ""),
                    record.get("blood_pressure_systolic", ""),
                    record.get("blood_pressure_diastolic", ""),
                    record.get("sleep_hours", ""),
                    record.get("mood", "")
                ])
            
            # get the csv content
            csv_content = output.getvalue()
            output.close()
            
            print(f"DEBUG: exported {len(biomarkers)} records for user {uid}")
            
            # return as downloadable file
            filename = f"biomarkers_{uid}_{datetime.now().strftime('%Y%m%d')}.csv"
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail=f"unsupported format: {format}")
            
    except Exception as e:
        print(f"DEBUG: export error: {e}")
        raise HTTPException(status_code=500, detail=f"export failed: {e}")
