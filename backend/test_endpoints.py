#!/usr/bin/env python3
# quick test script for backend endpoints
# run this after starting the server

import sys
import os
import requests

# add backend to path
sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"
TOKEN = "mock_token"  # change to real token when testing with firebase

headers = {"Authorization": f"Bearer {TOKEN}"}

def main():
    print("Testing PulseLink Backend")
    print("-" * 40)
    
    # check if server is running
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print(f"Health: OK ({r.json().get('database', 'unknown')})")
        else:
            print(f"Health check failed: {r.status_code}")
            return
    except Exception as e:
        print(f"Server not running? Error: {e}")
        print("Start with: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    print()
    
    # test user profile
    try:
        r = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"User: {data.get('email', 'no email')}")
        else:
            print(f"User profile failed: {r.status_code}")
    except Exception as e:
        print(f"Error getting user: {e}")
    
    # test devices
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/devices", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Devices: {data.get('count', 0)} found")
        else:
            print(f"Devices failed: {r.status_code}")
    except Exception as e:
        print(f"Error getting devices: {e}")
    
    # test manual entries
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/manual", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Manual entries: {data.get('count', 0)} found")
        else:
            print(f"Manual entries failed: {r.status_code}")
    except Exception as e:
        print(f"Error getting entries: {e}")
    
    # test adding a manual entry
    try:
        entry = {
            "biomarker_type": "weight",
            "value": 70.5,
            "notes": "test entry"
        }
        r = requests.post(f"{BASE_URL}/api/v1/biomarkers/manual", 
                         headers=headers, json=entry, timeout=5)
        if r.status_code == 200:
            print(f"Added entry: {r.json().get('entry_id', 'ok')}")
        else:
            print(f"Add entry failed: {r.status_code}")
    except Exception as e:
        print(f"Error adding entry: {e}")
    
    # test realtime data
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/real-time", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Real-time data: {len(data.get('data', []))} items")
        else:
            print(f"Real-time failed: {r.status_code}")
    except Exception as e:
        print(f"Error getting real-time: {e}")
    
    # test summary endpoint
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/summary?period=daily", 
                         headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Summary: {len(data.get('dashboard_data', []))} cards")
        else:
            print(f"Summary failed: {r.status_code}")
    except Exception as e:
        print(f"Error getting summary: {e}")
    
    print()
    print("Done. Check output above for any FAILs.")

if __name__ == "__main__":
    main()
