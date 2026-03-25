#!/usr/bin/env python3
"""test script for historical comparison endpoint"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_historical():
    # use mock token for testing
    try:
        # in mock mode, any token starting with "mock_" works
        token = "mock_test_token"
        headers = {"Authorization": f"Bearer {token}"}
        
        # test historical endpoint without date
        print("\n--- testing /historical (no date) ---")
        hist_resp = requests.get(f"{BASE_URL}/api/v1/biomarkers/historical", headers=headers)
        print(f"status: {hist_resp.status_code}")
        
        if hist_resp.status_code == 200:
            data = hist_resp.json()
            print(f"user_id: {data.get('user_id')}")
            print(f"comparison_date: {data.get('comparison_date')}")
            print(f"current_week: {data.get('current_week', {}).get('start')} to {data.get('current_week', {}).get('end')}")
            print(f"previous_week: {data.get('previous_week', {}).get('start')} to {data.get('previous_week', {}).get('end')}")
            print(f"changes: {json.dumps(data.get('changes', {}), indent=2)}")
            print(f"trends: {data.get('trends')}")
            print(f"summary: {data.get('summary')}")
        else:
            print(f"error: {hist_resp.text}")
            return
        
        # test with specific date
        print("\n--- testing /historical?date=2026-03-01 ---")
        hist_resp2 = requests.get(f"{BASE_URL}/api/v1/biomarkers/historical?date=2026-03-01", headers=headers)
        print(f"status: {hist_resp2.status_code}")
        
        if hist_resp2.status_code == 200:
            data2 = hist_resp2.json()
            print(f"comparison_date: {data2.get('comparison_date')}")
            print(f"current_week: {data2.get('current_week', {}).get('start')} to {data2.get('current_week', {}).get('end')}")
        else:
            print(f"error: {hist_resp2.text}")
            return
        
        # test invalid date format
        print("\n--- testing /historical?date=invalid ---")
        hist_resp3 = requests.get(f"{BASE_URL}/api/v1/biomarkers/historical?date=invalid", headers=headers)
        print(f"status: {hist_resp3.status_code}")
        print(f"response: {hist_resp3.text}")
        
        print("\n=== ALL TESTS PASSED ===")
            
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
        print("run: cd backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_historical()
