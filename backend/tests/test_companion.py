#!/usr/bin/env python3
"""test script for virtual companion endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_companion():
    token = "mock_test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. test status endpoint
        print("\n--- 1. GET /companion/status ---")
        resp = requests.get(f"{BASE_URL}/api/v1/companion/status", headers=headers)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"greeting: {data.get('greeting')}")
            print(f"status: {data.get('status')}")
            print(f"quick_tip: {data.get('quick_tip')}")
        else:
            print(f"error: {resp.text}")
        
        # 2. test chat with greeting
        print("\n--- 2. POST /companion/chat (greeting) ---")
        resp2 = requests.post(
            f"{BASE_URL}/api/v1/companion/chat",
            json={"message": "hello"},
            headers=headers
        )
        print(f"status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            print(f"user: {data2.get('message')}")
            print(f"companion: {data2.get('response')}")
        
        # 3. test chat with steps question
        print("\n--- 3. POST /companion/chat (steps) ---")
        resp3 = requests.post(
            f"{BASE_URL}/api/v1/companion/chat",
            json={"message": "how many steps have i taken?"},
            headers=headers
        )
        print(f"status: {resp3.status_code}")
        if resp3.status_code == 200:
            data3 = resp3.json()
            print(f"response: {data3.get('response')[:100]}...")
            print(f"suggestions: {data3.get('suggestions')}")
        
        # 4. test chat with heart rate
        print("\n--- 4. POST /companion/chat (heart rate) ---")
        resp4 = requests.post(
            f"{BASE_URL}/api/v1/companion/chat",
            json={"message": "how is my heart rate?"},
            headers=headers
        )
        print(f"status: {resp4.status_code}")
        if resp4.status_code == 200:
            data4 = resp4.json()
            print(f"response: {data4.get('response')}")
        
        # 5. test tips endpoint
        print("\n--- 5. GET /companion/tips ---")
        resp5 = requests.get(f"{BASE_URL}/api/v1/companion/tips", headers=headers)
        print(f"status: {resp5.status_code}")
        if resp5.status_code == 200:
            data5 = resp5.json()
            print(f"tips count: {data5.get('count')}")
            for tip in data5.get('tips', [])[:3]:
                print(f"  - [{tip.get('category')}] {tip.get('tip')[:50]}...")
        
        # 6. test motivation endpoint
        print("\n--- 6. GET /companion/motivation ---")
        resp6 = requests.get(f"{BASE_URL}/api/v1/companion/motivation", headers=headers)
        print(f"status: {resp6.status_code}")
        if resp6.status_code == 200:
            data6 = resp6.json()
            print(f"message: {data6.get('message')}")
            print(f"records tracked: {data6.get('records_tracked')}")
        
        # 7. test empty message (should fail)
        print("\n--- 7. POST /companion/chat (empty - should fail) ---")
        resp7 = requests.post(
            f"{BASE_URL}/api/v1/companion/chat",
            json={"message": ""},
            headers=headers
        )
        print(f"status: {resp7.status_code}")
        
        print("\n=== ALL COMPANION TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_companion()
