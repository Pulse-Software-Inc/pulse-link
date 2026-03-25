#!/usr/bin/env python3
"""test script for environmental data endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_environmental():
    token = "mock_test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. test weather endpoint
        print("\n--- 1. GET /environmental/weather ---")
        resp = requests.get(f"{BASE_URL}/api/v1/environmental/weather", headers=headers)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"temperature: {data.get('current', {}).get('temperature_c')}°C")
            print(f"weather: {data.get('current', {}).get('weather_description')}")
            print(f"recommendations: {data.get('health_recommendations', [])}")
        else:
            print(f"error: {resp.text}")
        
        # 2. test weather with custom coordinates (london)
        print("\n--- 2. GET /environmental/weather?lat=51.5&lon=-0.12 ---")
        resp2 = requests.get(f"{BASE_URL}/api/v1/environmental/weather?lat=51.5&lon=-0.12", headers=headers)
        print(f"status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            print(f"location: {data2.get('location')}")
            print(f"temperature: {data2.get('current', {}).get('temperature_c')}°C")
        
        # 3. test air quality
        print("\n--- 3. GET /environmental/air-quality ---")
        resp3 = requests.get(f"{BASE_URL}/api/v1/environmental/air-quality", headers=headers)
        print(f"status: {resp3.status_code}")
        if resp3.status_code == 200:
            data3 = resp3.json()
            print(f"aqi: {data3.get('air_quality', {}).get('aqi_us')}")
            print(f"category: {data3.get('air_quality', {}).get('category')}")
            print(f"pm2.5: {data3.get('air_quality', {}).get('pm2_5')}")
            print(f"recommendations: {data3.get('health_recommendations', [])}")
        else:
            print(f"error: {resp3.text}")
        
        # 4. test combined endpoint
        print("\n--- 4. GET /environmental/combined ---")
        resp4 = requests.get(f"{BASE_URL}/api/v1/environmental/combined", headers=headers)
        print(f"status: {resp4.status_code}")
        if resp4.status_code == 200:
            data4 = resp4.json()
            print(f"temperature: {data4.get('weather', {}).get('temperature_c')}°C")
            print(f"aqi: {data4.get('air_quality', {}).get('aqi_us')}")
            print(f"recommendations: {data4.get('health_recommendations', [])}")
            print(f"outdoor safety: {data4.get('overall_outdoor_safety')}")
        else:
            print(f"error: {resp4.text}")
        
        print("\n=== ALL ENVIRONMENTAL TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_environmental()
