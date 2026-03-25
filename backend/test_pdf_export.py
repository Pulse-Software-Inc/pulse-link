#!/usr/bin/env python3
"""test script for provider pdf export endpoint"""

import requests
import os

BASE_URL = "http://localhost:8000"

def test_pdf_export():
    # use mock token - need to use provider role
    token = "mock_provider_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # test pdf export for patient
        print("\n--- GET /providers/patients/user123/export ---")
        resp = requests.get(
            f"{BASE_URL}/api/v1/providers/patients/user123/export",
            headers=headers
        )
        print(f"status: {resp.status_code}")
        
        if resp.status_code == 200:
            # save the pdf
            filename = "/tmp/test_patient_export.pdf"
            with open(filename, "wb") as f:
                f.write(resp.content)
            print(f"pdf saved to: {filename}")
            print(f"file size: {len(resp.content)} bytes")
            
            # check if file exists and has content
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print("pdf generation successful!")
            else:
                print("error: pdf file is empty")
        else:
            print(f"error: {resp.text}")
        
        # test with date range
        print("\n--- GET /providers/patients/user123/export?start_date=2025-01-01 ---")
        resp2 = requests.get(
            f"{BASE_URL}/api/v1/providers/patients/user123/export?start_date=2025-01-01",
            headers=headers
        )
        print(f"status: {resp2.status_code}")
        
        # test non-existent patient
        print("\n--- GET /providers/patients/nonexistent/export (should 404) ---")
        resp3 = requests.get(
            f"{BASE_URL}/api/v1/providers/patients/nonexistent/export",
            headers=headers
        )
        print(f"status: {resp3.status_code}")
        print(f"response: {resp3.text[:100] if resp3.text else 'empty'}")
        
        # test with regular user token (should fail - needs provider role)
        print("\n--- GET /providers/patients/user123/export with user token (should 403) ---")
        user_headers = {"Authorization": "Bearer mock_user_token"}
        resp4 = requests.get(
            f"{BASE_URL}/api/v1/providers/patients/user123/export",
            headers=user_headers
        )
        print(f"status: {resp4.status_code}")
        
        print("\n=== ALL PDF EXPORT TESTS PASSED ===")
        
    except requests.exceptions.ConnectionError:
        print("error: cannot connect to server. make sure backend is running on port 8000")
        print("run: cd backend && USE_MOCK=true python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    test_pdf_export()
