#!/usr/bin/env python3
# test with real firebase token
# get token from http://localhost:3000/firebase-test

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"

def run_tests(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Testing with token: {token[:20]}...")
    print()
    
    passed = 0
    failed = 0
    
    # health check (no auth needed)
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        if r.status_code == 200:
            print("Health: PASS")
            passed += 1
        else:
            print(f"Health: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"Health: ERROR - {e}")
        failed += 1
    
    # user profile
    try:
        r = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"User Profile: PASS ({data.get('email', 'unknown')})")
            passed += 1
        else:
            print(f"User Profile: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"User Profile: ERROR - {e}")
        failed += 1
    
    # devices
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/devices", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Devices: PASS ({data.get('count', 0)} devices)")
            passed += 1
        else:
            print(f"Devices: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"Devices: ERROR - {e}")
        failed += 1
    
    # add manual entry
    try:
        entry = {
            "biomarker_type": "blood_pressure",
            "value": {"systolic": 120, "diastolic": 80},
            "notes": "test"
        }
        r = requests.post(f"{BASE_URL}/api/v1/biomarkers/manual", 
                         headers=headers, json=entry, timeout=5)
        if r.status_code == 200:
            print(f"Add Entry: PASS")
            passed += 1
        else:
            print(f"Add Entry: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"Add Entry: ERROR - {e}")
        failed += 1
    
    # get manual entries
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/manual", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"Get Entries: PASS ({data.get('count', 0)} entries)")
            passed += 1
        else:
            print(f"Get Entries: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"Get Entries: ERROR - {e}")
        failed += 1
    
    # realtime data
    try:
        r = requests.get(f"{BASE_URL}/api/v1/biomarkers/real-time", headers=headers, timeout=5)
        if r.status_code == 200:
            print(f"Real-time: PASS")
            passed += 1
        else:
            print(f"Real-time: FAIL ({r.status_code})")
            failed += 1
    except Exception as e:
        print(f"Real-time: ERROR - {e}")
        failed += 1
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0

def main():
    print("Firebase Token Test")
    print("=" * 40)
    print()
    print("Get token from: http://localhost:3000/firebase-test")
    print()
    
    # check if token passed as arg
    if len(sys.argv) > 1:
        token = sys.argv[1]
        print("Using token from command line")
    else:
        token = input("Enter Firebase token: ").strip()
    
    if not token:
        print("No token provided")
        sys.exit(1)
    
    # check if its a mock token
    if "mock" in token.lower():
        print("Error: This looks like a mock token!")
        print("Use a real token from the test page")
        sys.exit(1)
    
    success = run_tests(token)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
