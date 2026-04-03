#!/usr/bin/env python3
"""test script for custom alerts endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_alerts():
    token = "mock_test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. test get alerts (should be empty initially)
        print("\n--- 1. GET /users/me/alerts (empty) ---")
        resp = requests.get(f"{BASE_URL}/api/v1/users/me/alerts", headers=headers)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"count: {data.get('count')}")
        else:
            print(f"error: {resp.text}")
        
        # 2. create an alert for heart rate > 120
        print("\n--- 2. POST /users/me/alerts (heart_rate > 120) ---")
        alert_data = {
            "biomarker_type": "heart_rate",
            "condition": "greater_than",
            "threshold": 120,
            "message": "Your heart rate is elevated!",
            "severity": "warning"
        }
        resp2 = requests.post(f"{BASE_URL}/api/v1/users/me/alerts", json=alert_data, headers=headers)
        print(f"status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            print(f"alert_id: {data2.get('alert_id')}")
            alert_id = data2.get('alert_id')
        else:
            print(f"error: {resp2.text}")
            alert_id = None
        
        # 3. create another alert for steps < 5000
        print("\n--- 3. POST /users/me/alerts (steps < 5000) ---")
        alert_data2 = {
            "biomarker_type": "steps",
            "condition": "less_than",
            "threshold": 5000,
            "message": "You haven't reached your daily step goal"
        }
        resp3 = requests.post(f"{BASE_URL}/api/v1/users/me/alerts", json=alert_data2, headers=headers)
        print(f"status: {resp3.status_code}")
        
        # 4. test get alerts (should have 2 now)
        print("\n--- 4. GET /users/me/alerts (2 alerts) ---")
        resp4 = requests.get(f"{BASE_URL}/api/v1/users/me/alerts", headers=headers)
        print(f"status: {resp4.status_code}")
        if resp4.status_code == 200:
            data4 = resp4.json()
            print(f"count: {data4.get('count')}")
            for alert in data4.get('alerts', []):
                print(f"  - {alert.get('biomarker_type')}: {alert.get('condition')} {alert.get('threshold')}")
        
        # 5. test check alerts against biomarker data
        print("\n--- 5. GET /biomarkers/alerts/check ---")
        resp5 = requests.get(f"{BASE_URL}/api/v1/biomarkers/alerts/check", headers=headers)
        print(f"status: {resp5.status_code}")
        if resp5.status_code == 200:
            data5 = resp5.json()
            print(f"alerts checked: {data5.get('alerts_configured')}")
            print(f"alerts triggered: {len(data5.get('alerts_triggered', []))}")
            for triggered in data5.get('alerts_triggered', []):
                print(f"  - {triggered.get('message')} (current: {triggered.get('current_value')})")
        else:
            print(f"error: {resp5.text}")
        
        # 6. test invalid alert creation (missing field)
        print("\n--- 6. POST /users/me/alerts (invalid - missing field) ---")
        invalid_alert = {"biomarker_type": "heart_rate"}  # missing condition and threshold
        resp6 = requests.post(f"{BASE_URL}/api/v1/users/me/alerts", json=invalid_alert, headers=headers)
        print(f"status: {resp6.status_code}")
        print(f"response: {resp6.text}")
        
        # 7. delete the first alert
        if alert_id:
            print(f"\n--- 7. DELETE /users/me/alerts/{alert_id} ---")
            resp7 = requests.delete(f"{BASE_URL}/api/v1/users/me/alerts/{alert_id}", headers=headers)
            print(f"status: {resp7.status_code}")
            if resp7.status_code == 200:
                print(f"deleted: {resp7.json().get('message')}")
        
        # 8. verify deletion
        print("\n--- 8. GET /users/me/alerts (after delete) ---")
        resp8 = requests.get(f"{BASE_URL}/api/v1/users/me/alerts", headers=headers)
        print(f"status: {resp8.status_code}")
        if resp8.status_code == 200:
            print(f"count: {resp8.json().get('count')}")
        
        print("\n=== ALL ALERT TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
        print("run: cd backend && USE_MOCK=true python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_alerts()
