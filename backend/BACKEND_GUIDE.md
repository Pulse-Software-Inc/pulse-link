# PulseLink Backend

FastAPI backend with Firebase Firestore.

# Quick Start

* bash
cd /home/aminafara123/aiPorjects/pulse/pulse-link/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000


API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

# Auth

All protected endpoints need a Firebase token:

* bash
# Get token from http://localhost:3000/firebase-test
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/users/me


Add the javascript instructions when you google it


# API Endpoints

 Method  Endpoint  Auth 

 GET  `/health`  No 
 GET  `/api/v1/users/me`  Yes 
 PUT  `/api/v1/users/me` Yes 
 GET  `/api/v1/biomarkers/devices`  Yes 
 GET  `/api/v1/biomarkers/real-time` Yes 
 GET  `/api/v1/biomarkers/summary` Yes  # Dashboard summary
 GET  `/api/v1/biomarkers/export` Yes    # CSV export
 POST  `/api/v1/biomarkers/manual`  Yes 
 GET  `/api/v1/biomarkers/manual`  Yes 
 DELETE  `/api/v1/biomarkers/manual/{id}`  Yes 
 GET  `/api/v1/providers/patients`  Yes 
# Testing

bash
python3 quick_test.py  # Uses mock_token for dev testing


# Firebase Setup

1) Download service account from Firebase Console > Project Settings > Service Accounts
2) Save as `backend/firebase-service-account.json`
3) Done backend should auto-detect it

# Notes

- Uses Firebase Firestore (data persists)
- mock tokens work for dev: `Bearer mock_token` remove
- Real Firebase tokens required for production
- CORS enabled for localhost:3000
