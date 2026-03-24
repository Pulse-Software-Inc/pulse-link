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

## Auth
| Method | Endpoint | Auth |
|--------|----------|------|
| GET | `/health` | No |
| GET | `/api/v1/auth/me` | Yes |
| GET | `/api/v1/auth/verify` | Yes |
| POST | `/api/v1/auth/forgot-password` | No |
| POST | `/api/v1/auth/reset-password` | No |
| POST | `/api/v1/auth/change-password` | Yes |

## Users
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/users/me` | Yes | Get profile |
| PUT | `/api/v1/users/me` | Yes | Update profile |
| GET | `/api/v1/users/me/consent` | Yes | Get consent settings |
| PUT | `/api/v1/users/me/consent` | Yes | Update consent |
| GET | `/api/v1/users/me/alerts` | Yes | List custom alerts |
| POST | `/api/v1/users/me/alerts` | Yes | Create alert threshold |
| DELETE | `/api/v1/users/me/alerts/{id}` | Yes | Delete alert |

## Biomarkers
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/biomarkers/real-time` | Yes | Recent data |
| GET | `/api/v1/biomarkers/devices` | Yes | Connected devices |
| GET | `/api/v1/biomarkers/summary` | Yes | Dashboard summary (daily/weekly/monthly) |
| GET | `/api/v1/biomarkers/historical` | Yes | Week vs week comparison |
| GET | `/api/v1/biomarkers/export` | Yes | CSV export |
| GET | `/api/v1/biomarkers/alerts/check` | Yes | Check alerts against current data |
| POST | `/api/v1/biomarkers/manual` | Yes | Add manual entry |
| GET | `/api/v1/biomarkers/manual` | Yes | List manual entries |
| DELETE | `/api/v1/biomarkers/manual/{id}` | Yes | Delete manual entry |

## Healthcare Providers
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/providers/patients` | Yes | List patients |
| GET | `/api/v1/providers/patients/{id}/data` | Yes | Patient data |
| GET | `/api/v1/providers/patients/{id}/export` | Yes | PDF export |

## Environmental Data (Should-Have)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/environmental/weather` | Yes | Weather data |
| GET | `/api/v1/environmental/air-quality` | Yes | Air quality |
| GET | `/api/v1/environmental/combined` | Yes | Weather + Air quality |

## Virtual Companion (Should-Have)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/companion/status` | Yes | Companion status |
| POST | `/api/v1/companion/chat` | Yes | Chat with companion |
| GET | `/api/v1/companion/tips` | Yes | Health tips |
| GET | `/api/v1/companion/motivation` | Yes | Motivational message |

## Notifications (Should-Have)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/notifications` | Yes | List notifications |
| GET | `/api/v1/notifications/summary` | Yes | Unread count |
| POST | `/api/v1/notifications/{id}/read` | Yes | Mark as read |
| POST | `/api/v1/notifications/read-all` | Yes | Mark all read |
| DELETE | `/api/v1/notifications/{id}` | Yes | Delete notification |

## Emergency Contacts (Should-Have)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/emergency/contacts` | Yes | List contacts |
| POST | `/api/v1/emergency/contacts` | Yes | Add contact |
| PUT | `/api/v1/emergency/contacts/{id}` | Yes | Update contact |
| DELETE | `/api/v1/emergency/contacts/{id}` | Yes | Delete contact |
| POST | `/api/v1/emergency/alert` | Yes | Trigger emergency alert |
| GET | `/api/v1/emergency/settings` | Yes | Get settings |
| PUT | `/api/v1/emergency/settings` | Yes | Update settings | 
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
