#!/usr/bin/env python3
# quick test with firebase token
# set FIREBASE_ID_TOKEN env var first

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = os.getenv("FIREBASE_API_BASE", "http://localhost:8000")
TOKEN = os.getenv("FIREBASE_ID_TOKEN")

if not TOKEN:
    print("Error: FIREBASE_ID_TOKEN not set")
    print("Get token from http://localhost:3000/firebase-test")
    sys.exit(1)

def test():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    print("Quick Backend Test")
    print("-" * 40)
    print()
    
    # check server running
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        if r.status_code == 200:
            print("Server: running")
        else:
            print(f"Server: error {r.status_code}")
            return False
    except:
        print("Server: not running")
        print("Start with: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    tests = [
        ("User Profile", "GET", "/api/v1/users/me", None),
        ("Devices", "GET", "/api/v1/biomarkers/devices", None),
        ("Add Entry", "POST", "/api/v1/biomarkers/manual", 
         {"biomarker_type": "weight", "value": 72.5}),
        ("Get Entries", "GET", "/api/v1/biomarkers/manual", None),
        ("Real-time", "GET", "/api/v1/biomarkers/real-time", None),
    ]
    
    passed = 0
    failed = 0
    
    for name, method, endpoint, data in tests:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=5)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=data, timeout=5)
            else:
                print(f"{name}: unknown method {method}")
                failed += 1
                continue
            
            if r.status_code == 200:
                print(f"{name}: OK")
                passed += 1
            else:
                print(f"{name}: FAIL ({r.status_code})")
                failed += 1
                
        except Exception as e:
            print(f"{name}: ERROR ({e})")
            failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
