#!/usr/bin/env python3
"""environmental data router - weather and air quality"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user

router = APIRouter(prefix="/environmental", tags=["environmental"])

# free open-meteo api (no api key needed)
# could use openweathermap with api key for production

@router.get("/weather")
async def get_weather(
    lat: float = 25.2048,  # default to dubai
    lon: float = 55.2708,
    current_user: dict = Depends(get_current_user)
):
    """
    get weather data for a location.
    defaults to dubai coordinates.
    uses open-meteo api (free, no key needed).
    """
    try:
        # open-meteo api
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min,uv_index_max&timezone=auto"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"].get("message", "weather api error"))
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        # map weather code to description
        weather_codes = {
            0: "clear sky",
            1: "mainly clear", 2: "partly cloudy", 3: "overcast",
            45: "fog", 48: "depositing rime fog",
            51: "light drizzle", 53: "moderate drizzle", 55: "dense drizzle",
            61: "slight rain", 63: "moderate rain", 65: "heavy rain",
            71: "slight snow", 73: "moderate snow", 75: "heavy snow",
            95: "thunderstorm", 96: "thunderstorm with hail",
        }
        
        code = current.get("weather_code", 0)
        weather_desc = weather_codes.get(code, "unknown")
        
        # health recommendations based on weather
        recommendations = []
        temp = current.get("temperature_2m", 20)
        uv = daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0
        
        if temp > 35:
            recommendations.append("extreme heat - stay hydrated and avoid outdoor exercise")
        elif temp > 30:
            recommendations.append("high temperature - drink plenty of water")
        elif temp < 10:
            recommendations.append("cold weather - dress warmly")
        
        if uv > 8:
            recommendations.append("very high uv - avoid sun exposure, use sunscreen")
        elif uv > 5:
            recommendations.append("moderate uv - wear sunscreen if going outside")
        
        # check for rain
        if code in [61, 63, 65, 95, 96]:
            recommendations.append("rain expected - consider indoor activities")
        
        result = {
            "user_id": current_user["uid"],
            "location": {"latitude": lat, "longitude": lon},
            "current": {
                "temperature_c": current.get("temperature_2m"),
                "feels_like_c": current.get("apparent_temperature"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "weather_code": code,
                "weather_description": weather_desc
            },
            "daily_forecast": {
                "max_temp_c": daily.get("temperature_2m_max", [None])[0],
                "min_temp_c": daily.get("temperature_2m_min", [None])[0],
                "uv_index_max": uv
            },
            "health_recommendations": recommendations,
            "fetched_at": data.get("current", {}).get("time")
        }
        
        print(f"DEBUG: weather fetched for user {current_user['uid']}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: weather api request failed: {e}")
        raise HTTPException(status_code=503, detail="weather service unavailable")
    except Exception as e:
        print(f"DEBUG: weather error: {e}")
        raise HTTPException(status_code=500, detail=f"failed to fetch weather: {e}")


@router.get("/air-quality")
async def get_air_quality(
    lat: float = 25.2048,
    lon: float = 55.2708,
    current_user: dict = Depends(get_current_user)
):
    """
    get air quality data for a location.
    includes pm2.5, pm10, ozone, and health recommendations.
    """
    try:
        # open-meteo air quality api
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone&timezone=auto"
        
        resp = requests.get(url, timeout=10)
        data = resp.json()
        
        if "error" in data:
            raise HTTPException(status_code=400, detail=data["error"].get("message", "air quality api error"))
        
        current = data.get("current", {})
        aqi = current.get("us_aqi", 0)
        
        # aqi categories and recommendations
        if aqi <= 50:
            category = "good"
            color = "green"
            rec = "air quality is satisfactory"
        elif aqi <= 100:
            category = "moderate"
            color = "yellow"
            rec = "sensitive individuals should limit prolonged outdoor exertion"
        elif aqi <= 150:
            category = "unhealthy for sensitive groups"
            color = "orange"
            rec = "people with heart/lung disease should reduce outdoor activity"
        elif aqi <= 200:
            category = "unhealthy"
            color = "red"
            rec = "everyone should reduce outdoor activities"
        elif aqi <= 300:
            category = "very unhealthy"
            color = "purple"
            rec = "avoid outdoor activities, wear mask if going outside"
        else:
            category = "hazardous"
            color = "maroon"
            rec = "health emergency - stay indoors and use air purifier"
        
        result = {
            "user_id": current_user["uid"],
            "location": {"latitude": lat, "longitude": lon},
            "air_quality": {
                "aqi_us": aqi,
                "category": category,
                "color": color,
                "pm2_5": current.get("pm2_5"),
                "pm10": current.get("pm10"),
                "ozone": current.get("ozone"),
                "nitrogen_dioxide": current.get("nitrogen_dioxide"),
                "carbon_monoxide": current.get("carbon_monoxide")
            },
            "health_recommendations": [rec],
            "fetched_at": current.get("time")
        }
        
        print(f"DEBUG: air quality fetched for user {current_user['uid']}, aqi={aqi}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: air quality api request failed: {e}")
        raise HTTPException(status_code=503, detail="air quality service unavailable")
    except Exception as e:
        print(f"DEBUG: air quality error: {e}")
        raise HTTPException(status_code=500, detail=f"failed to fetch air quality: {e}")


@router.get("/combined")
async def get_combined_environmental(
    lat: float = 25.2048,
    lon: float = 55.2708,
    current_user: dict = Depends(get_current_user)
):
    """
    get both weather and air quality in one call.
    useful for dashboard display.
    """
    try:
        # fetch both sequentially for now
        
        # weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=uv_index_max&timezone=auto"
        weather_resp = requests.get(weather_url, timeout=10)
        weather_data = weather_resp.json()
        
        # air quality
        aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi,pm2_5,pm10,ozone&timezone=auto"
        aqi_resp = requests.get(aqi_url, timeout=10)
        aqi_data = aqi_resp.json()
        
        # combine results
        current_weather = weather_data.get("current", {})
        current_aqi = aqi_data.get("current", {})
        
        aqi = current_aqi.get("us_aqi", 0)
        temp = current_weather.get("temperature_2m", 20)
        
        # combined health recommendations
        recommendations = []
        
        # temperature based
        if temp > 35:
            recommendations.append("extreme heat warning - limit outdoor activity")
        elif temp < 10:
            recommendations.append("cold weather - dress warmly for outdoor exercise")
        
        # air quality based
        if aqi > 150:
            recommendations.append("poor air quality - avoid outdoor exercise")
        elif aqi > 100:
            recommendations.append("moderate air quality - sensitive individuals limit outdoor activity")
        
        # uv based
        daily = weather_data.get("daily", {})
        uv = daily.get("uv_index_max", [0])[0] if daily.get("uv_index_max") else 0
        if uv > 8:
            recommendations.append("very high uv - use sunscreen and seek shade")
        
        result = {
            "user_id": current_user["uid"],
            "location": {"latitude": lat, "longitude": lon},
            "weather": {
                "temperature_c": temp,
                "feels_like_c": current_weather.get("apparent_temperature"),
                "humidity_percent": current_weather.get("relative_humidity_2m"),
                "weather_code": current_weather.get("weather_code"),
                "wind_speed_kmh": current_weather.get("wind_speed_10m")
            },
            "air_quality": {
                "aqi_us": aqi,
                "pm2_5": current_aqi.get("pm2_5"),
                "pm10": current_aqi.get("pm10"),
                "ozone": current_aqi.get("ozone")
            },
            "health_recommendations": recommendations,
            "overall_outdoor_safety": "safe" if aqi <= 100 and 10 <= temp <= 35 else "caution"
        }
        
        print(f"DEBUG: combined environmental data fetched for user {current_user['uid']}")
        return result
        
    except Exception as e:
        print(f"DEBUG: combined environmental error: {e}")
        raise HTTPException(status_code=500, detail=f"failed to fetch environmental data: {e}")
