# For Frontend Team: How to Connect to Backend

1. **Start the backend** (Terminal 1):
```bash
cd backend
USE_MOCK=true python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Important**: `USE_MOCK=true` enables mock tokens for testing. Without this, you need real Firebase tokens.

2. **Backend is now running at**: `http://localhost:8000`

3. **API Documentation**: Open `http://localhost:8000/docs` in browser

---

## How to Make API Calls

### Step 1: Get a Token

**For testing (when backend runs with USE_MOCK=true):**
```javascript
// Regular user
const token = "mock_token";

// Healthcare provider
const providerToken = "mock_provider_token";
```

**For production (real Firebase):**
You need to get a Firebase ID token from the Firebase Auth SDK after user login.

### Step 2: Make Requests

```javascript
// Example: Get user's dashboard summary
const response = await fetch('http://localhost:8000/api/v1/biomarkers/summary?period=daily', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer mock_token'
  }
});

const data = await response.json();
console.log(data);
```

---

## Important Endpoints You Need

| What You Need | Endpoint | Method | (The | seperates each section)

| User login/verify | `/api/v1/auth/me` | GET |
| Dashboard cards data | `/api/v1/biomarkers/summary?period=daily` | GET |
| Weekly comparison chart | `/api/v1/biomarkers/historical` | GET |
| Export CSV | `/api/v1/biomarkers/export?format=csv` | GET |
| Weather for dashboard | `/api/v1/environmental/weather` | GET |
| Chat with companion | `/api/v1/companion/chat` | POST |
| Notifications | `/api/v1/notifications` | GET |

--

## Response Format Example

```javascript
// GET /api/v1/biomarkers/summary?period=daily
{
  "user_id": "user123",
  "period": "daily",
  "dashboard_data": [
    {
      "id": "Steps",
      "title": "Steps",
      "iconSrc": "/Steps_Icon.svg",
      "main": "8432",
      "sub": "/10,000",
      "footer": "goal: 10,000 steps daily",
      "progress": {"value": 8432, "max": 10000}
    },
    {
      "id": "Kcal",
      "title": "Calories Burned",
      "iconSrc": "/Calories_Icon.svg",
      "main": "512",
      "sub": "/500",
      "footer": null,
      "progress": {"value": 512, "max": 500}
    },
    {
      "id": "Heart",
      "title": "Heart Rate",
      "iconSrc": "/HeartRate_Icon.svg",
      "main": "72",
      "sub": "BPM",
      "footer": "Resting: 68 BPM | Synced: 2 mins ago"
    }
  ],
  "summary": {
    "daily_steps": {"current": 8432, "goal": 10000, "percentage": 84},
    "daily_calories": {"current": 512, "goal": 500, "percentage": 102},
    "heart_rate": {"current": 72, "resting": 68}
  }
}
```

---

## Current vs New Data Flow

### Before (Current):
```
Frontend -> /userdata.json (local file)
```

### After (With Backend):
```
Frontend -> http://localhost:8000/api/v1/... -> Backend -> Firebase
```

---

## What Needs to Change in Your Code

**Current code** (in `src/components/DB_cardsData.js`):
```javascript
const res = await fetch('/userdata.json', { cache: 'no-store' });
const json = await res.json();
// ... process json
```

**New code**:
```javascript
const token = "mock_token"; // Replace with real Firebase token in production
const res = await fetch('http://localhost:8000/api/v1/biomarkers/summary?period=daily', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const json = await res.json();
// json.dashboard_data has the card data
```

---

## Stage 1 Endpoints Added
- `GET/POST/DELETE /api/v1/users/me/providers` — link or list third-party accounts (google/apple/facebook); OAuth happens on the client.
- `POST /api/v1/social/share` and `GET /api/v1/social/shares` — log when a user shares stats/achievements.
- `GET /api/v1/appointments` — list appointments for current user (patient/provider).
- `POST /api/v1/appointments` and `PUT /api/v1/appointments/{id}` — providers schedule/update appointment reminders (in-app notifications; email not implemented).
- `POST /api/v1/support/tickets` and `GET /api/v1/support/tickets` — simple help desk for users to reach support.
