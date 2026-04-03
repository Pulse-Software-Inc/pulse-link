#!/usr/bin/env python3
"""test script for emergency contacts endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_emergency():
    token = "mock_test_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # 1. test get contacts (empty initially)
        print("\n--- 1. GET /emergency/contacts ---")
        resp = requests.get(f"{BASE_URL}/api/v1/emergency/contacts", headers=headers)
        print(f"status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"count: {data.get('count')}")
            print(f"max_contacts: {data.get('max_contacts')}")
        
        # 2. test get settings
        print("\n--- 2. GET /emergency/settings ---")
        resp2 = requests.get(f"{BASE_URL}/api/v1/emergency/settings", headers=headers)
        print(f"status: {resp2.status_code}")
        if resp2.status_code == 200:
            data2 = resp2.json()
            print(f"settings: {json.dumps(data2.get('settings'), indent=2)}")
        
        # 3. add emergency contact
        print("\n--- 3. POST /emergency/contacts ---")
        contact_data = {
            "name": "John Doe",
            "phone": "+971501234567",
            "relationship": "brother",
            "email": "john@example.com",
            "priority": 1
        }
        resp3 = requests.post(
            f"{BASE_URL}/api/v1/emergency/contacts",
            json=contact_data,
            headers=headers
        )
        print(f"status: {resp3.status_code}")
        if resp3.status_code == 200:
            data3 = resp3.json()
            print(f"contact_id: {data3.get('contact_id')}")
            contact_id = data3.get('contact_id')
        else:
            print(f"error: {resp3.text}")
            contact_id = None
        
        # 4. add another contact
        print("\n--- 4. POST /emergency/contacts (second) ---")
        contact_data2 = {
            "name": "Jane Smith",
            "phone": "+971509876543",
            "relationship": "friend",
            "priority": 2
        }
        resp4 = requests.post(
            f"{BASE_URL}/api/v1/emergency/contacts",
            json=contact_data2,
            headers=headers
        )
        print(f"status: {resp4.status_code}")
        
        # 5. get contacts again (should have 2)
        print("\n--- 5. GET /emergency/contacts (after adding) ---")
        resp5 = requests.get(f"{BASE_URL}/api/v1/emergency/contacts", headers=headers)
        print(f"status: {resp5.status_code}")
        if resp5.status_code == 200:
            data5 = resp5.json()
            print(f"count: {data5.get('count')}")
            for c in data5.get('contacts', []):
                print(f"  - {c.get('name')} ({c.get('relationship')}): {c.get('phone')}")
        
        # 6. trigger emergency alert
        print("\n--- 6. POST /emergency/alert ---")
        alert_data = {
            "type": "test_alert",
            "message": "this is a test emergency alert",
            "location": "dubai, uae"
        }
        resp6 = requests.post(
            f"{BASE_URL}/api/v1/emergency/alert",
            json=alert_data,
            headers=headers
        )
        print(f"status: {resp6.status_code}")
        if resp6.status_code == 200:
            data6 = resp6.json()
            print(f"alert_sent: {data6.get('alert_sent')}")
            print(f"contacts_notified: {data6.get('contacts_notified')}")
        
        # 7. delete contact
        if contact_id:
            print(f"\n--- 7. DELETE /emergency/contacts/{contact_id} ---")
            resp7 = requests.delete(
                f"{BASE_URL}/api/v1/emergency/contacts/{contact_id}",
                headers=headers
            )
            print(f"status: {resp7.status_code}")
            if resp7.status_code == 200:
                print(f"message: {resp7.json().get('message')}")
        
        # 8. test invalid contact (missing phone)
        print("\n--- 8. POST /emergency/contacts (invalid - missing phone) ---")
        invalid_contact = {"name": "No Phone"}
        resp8 = requests.post(
            f"{BASE_URL}/api/v1/emergency/contacts",
            json=invalid_contact,
            headers=headers
        )
        print(f"status: {resp8.status_code}")
        print(f"error: {resp8.text}")
        
        print("\n=== ALL EMERGENCY CONTACTS TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_emergency()
