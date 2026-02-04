#!/usr/bin/env python3
# test password reset endpoints

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(__file__))

BASE_URL = "http://localhost:8000"


def test_forgot_password():
    print("Testing Forgot Password")
    print("-" * 30)
    
    # test with some email
    data = {"email": "test@example.com"}
    
    try:
        r = requests.post(f"{BASE_URL}/api/v1/auth/forgot-password", json=data, timeout=10)
        if r.status_code == 200:
            print(f"Forgot password: OK")
            print(f"Response: {r.json()}")
            return True
        else:
            print(f"Forgot password: FAIL ({r.status_code})")
            print(f"Error: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"Forgot password: ERROR - {e}")
        return False


def test_change_password():
    print("\nTesting Change Password (requires auth token)")
    print("-" * 30)
    print("Skipped - needs Firebase token")
    return True


if __name__ == "__main__":
    print("Password Reset Tests")
    print("=" * 40)
    print()
    
    # check if server is running
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        if r.status_code != 200:
            print("Server not running!")
            sys.exit(1)
    except:
        print("Server not running! Start with:")
        print("python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    test_forgot_password()
    test_change_password()
    
    print("\nDone.")
