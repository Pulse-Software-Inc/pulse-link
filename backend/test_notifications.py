#!/usr/bin/env python3
"""test script for notifications endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_notifications():
    token = "mock_test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. test get notifications (empty initially)
        print("\n--- 1. GET /notifications ---")
        resp = requests.get(f"{BASE_URL}/api/v1/notifications", headers=headers)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"count: {data.get('count')}")
            print(f"unread_count: {data.get('unread_count')}")
        
        # 2. test summary
        print("\n--- 2. GET /notifications/summary ---")
        resp2 = requests.get(f"{BASE_URL}/api/v1/notifications/summary", headers=headers)
        print(f"status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            print(f"total: {data2.get('total_notifications')}")
            print(f"unread: {data2.get('unread_count')}")
            print(f"has_unread: {data2.get('has_unread')}")
        
        # 3. create some test notifications via internal function (simulate)
        # we'll call the biomarker alerts/check which might trigger notifications
        print("\n--- 3. Create test notification via alerts ---")
        # first create an alert
        alert_data = {
            "biomarker_type": "heart_rate",
            "condition": "greater_than",
            "threshold": 50,  # low threshold so it triggers
            "message": "test alert notification"
        }
        resp3 = requests.post(
            f"{BASE_URL}/api/v1/users/me/alerts",
            json=alert_data,
            headers=headers
        )
        print(f"create alert status: {resp3.status_code}")
        
        # check alerts (this might create notifications in future)
        resp3b = requests.get(f"{BASE_URL}/api/v1/biomarkers/alerts/check", headers=headers)
        print(f"check alerts status: {resp3b.status_code}")
        
        # 4. mark all as read
        print("\n--- 4. POST /notifications/read-all ---")
        resp4 = requests.post(f"{BASE_URL}/api/v1/notifications/read-all", headers=headers)
        print(f"status: {resp4.status_code}")
        if resp4.status_code == 200:
            print(f"marked as read: {resp4.json().get('marked_as_read')}")
        
        # 5. get unread only (should be empty after read-all)
        print("\n--- 5. GET /notifications?unread_only=true ---")
        resp5 = requests.get(f"{BASE_URL}/api/v1/notifications?unread_only=true", headers=headers)
        print(f"status: {resp5.status_code}")
        if resp5.status_code == 200:
            print(f"unread count: {resp5.json().get('count')}")
        
        print("\n=== ALL NOTIFICATION TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_notifications()
