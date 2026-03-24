# Frontend Integration Guide

## Overview
This document outlines potential issues and requirements for integrating the frontend with the backend API.

## Base URL
- Local development: `http://localhost:8000`
- Production: TBD

## Authentication
All protected endpoints require a Firebase ID token in the Authorization header:
```
Authorization: Bearer <firebase_id_token>
```

For development, mock tokens work:
- `Bearer mock_token` - regular user (user123)
- `Bearer mock_provider_token` - healthcare provider (provider456)

## CORS
CORS is enabled for `http://localhost:3000` (Next.js dev server).

## Response Format
All API responses are JSON. Error responses follow this format:
```json
{"detail": "error message"}
```

## Potential Issues

### 1. Dashboard Data Format Mismatch
**Current Frontend:** Reads from `/userdata.json` with format:
```json
{
  "summary": {
    "total_steps": 10000,
    "total_calories": 500,
    "avg_heart_rate": 72,
    "data_points": 5
  },
  "biomarkers": [...],
  "devices": [...]
}
```

**Backend API** (`/api/v1/biomarkers/summary`) returns:
```json
{
  "user_id": "xxx",
  "period": "daily",
  "dashboard_data": [...],
  "summary": {...}
}
```

**Action Required:** Frontend needs to update to use the API response format.

### 2. Date Format
All timestamps are ISO 8601 format: `2026-03-14T15:30:00` or `2026-03-14T15:30:00+00:00`

### 3. API Endpoints Summary

#### Must-Have Features (Completed)
| Feature | Endpoint | Status |
|---------|----------|--------|
| CSV Export | `GET /api/v1/biomarkers/export?format=csv` | ✅ Ready |
| Health Summaries | `GET /api/v1/biomarkers/summary?period=daily/weekly/monthly` | ✅ Ready |
| Historical Comparison | `GET /api/v1/biomarkers/historical?date=YYYY-MM-DD` | ✅ Ready |
| Custom Alerts | `GET/POST/DELETE /api/v1/users/me/alerts` | ✅ Ready |
| Provider PDF Export | `GET /api/v1/providers/patients/{id}/export` | ✅ Ready |

#### Should-Have Features (Completed)
| Feature | Endpoint | Status |
|---------|----------|--------|
| Weather | `GET /api/v1/environmental/weather?lat=xx&lon=xx` | ✅ Ready |
| Air Quality | `GET /api/v1/environmental/air-quality` | ✅ Ready |
| Companion Chat | `POST /api/v1/companion/chat` | ✅ Ready |
| Notifications | `GET /api/v1/notifications` | ✅ Ready |
| Emergency Contacts | `GET /api/v1/emergency/contacts` | ✅ Ready |

### 4. Data Availability
The mock database contains limited sample data:
- User: `user123`
- Provider: `provider456`
- Biomarkers: 2 sample records (dated 2025-01-26)

For testing with more data, use the manual entry endpoints or populate Firestore.

### 5. Required Environment Variables (Production)
```
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
USE_MOCK=false  # Set to true only for testing without Firebase
```

### 6. External API Dependencies
The environmental endpoints call external APIs:
- Open-Meteo (free, no key needed)
- These may have rate limits

### 7. PDF Export Requirements
PDF export requires `reportlab` Python package (already installed).

## Testing
Run all tests with:
```bash
cd backend
USE_MOCK=true python3 -m pytest tests/ -v
python3 test_historical.py
python3 test_alerts.py
python3 test_pdf_export.py
python3 test_environmental.py
python3 test_companion.py
python3 test_notifications.py
python3 test_emergency.py
```

## Known Limitations
1. Notification system stores in-app notifications only (no push notifications yet)
2. Emergency alerts are logged; email sending is not implemented (would need SMTP/provider)
3. Environmental data uses free APIs with rate limits
4. Virtual companion is rule-based
5. Appointment reminders are in-app notifications; email reminders not implemented

## New Endpoints (Stage 1 compliance)
- `GET /api/v1/users/me/providers` — list linked third-party accounts (google/apple/facebook)
- `POST /api/v1/users/me/providers` — link a third-party account (client handles OAuth; backend stores metadata)
- `DELETE /api/v1/users/me/providers/{link_id}` — unlink
- `POST /api/v1/social/share` — log a share action (platform, metric, message)
- `GET /api/v1/social/shares` — list past share logs
- `GET /api/v1/appointments` — list appointments for current user (patient or provider)
- `POST /api/v1/appointments` — provider creates appointment/reminder for patient
- `PUT /api/v1/appointments/{id}` — update status/time
- `POST /api/v1/support/tickets` — create a support/help ticket
- `GET /api/v1/support/tickets` — list support/help tickets

## Contact
For backend issues, contact: Amin Afara (Backend Engineer)
