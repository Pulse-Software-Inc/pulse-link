# PulseLink Backend

FastAPI + Firebase backend

# Run

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

# API

Base URL: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

# Auth

Needs Firebase token in header:

Authorization: Bearer <firebase_token>


Get token from: `http://localhost:3000/firebase-test`

# Endpoints

# Public:
- `GET /health`

# Protected:
- `GET /api/v1/users/me`
- `PUT /api/v1/users/me`
- `GET /api/v1/biomarkers/devices`
- `GET /api/v1/biomarkers/real-time`
- `POST /api/v1/biomarkers/manual`
- `GET /api/v1/biomarkers/manual`

I think its in `/docs` for full spec? 

# Test

bash
python3 quick_test.py


## Config

Service account: `firebase-service-account.json` (from firebase Console)