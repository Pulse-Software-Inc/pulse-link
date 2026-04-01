from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
import time
import uuid
from logging.handlers import RotatingFileHandler

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return None

from app.routers import auth, users, biomarkers, providers, environmental, companion, notifications, emergency, social, appointments, support

load_dotenv()

log_dir = os.getenv(
    "PULSELINK_LOG_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "pulselink.log")

logger = logging.getLogger("pulselink")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(log_file, maxBytes=500000, backupCount=3)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

app = FastAPI(
    title="PulseLink API",
    description="Virtual Health Companion bckend API",
    version="0.1.0",
)

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
allowed_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    start = time.time()

    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"{request_id} {request.method} {request.url.path} failed: {e}")
        raise

    duration_ms = int((time.time() - start) * 1000)
    logger.info(f"{request_id} {request.method} {request.url.path} {response.status_code} {duration_ms}ms")
    response.headers["X-Request-ID"] = request_id
    return response

# check for mock mode (for CI/testing)
use_mock = os.getenv("USE_MOCK", "false").lower() == "true"

if use_mock:
    logger.info("Using mock database mode")
    from app.core.mock_db import mock_db
    app.state.db = mock_db
    app.state.use_mock = True
elif not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
    if cred_path:
        cred_path = os.path.expanduser(cred_path)
    else:
        home_key = os.path.expanduser("~/.config/pulselink/firebase-service-account.json")
        if os.path.exists(home_key):
            cred_path = home_key
        else:
            cred_path = "firebase-service-account.json"
    if not os.path.exists(cred_path):
        raise RuntimeError(f"Firebase service account not found at {cred_path}")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    logger.info("Firebase initialized")
    app.state.db = firestore.client()
    app.state.use_mock = False

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(biomarkers.router, prefix="/api/v1")
app.include_router(providers.router, prefix="/api/v1")
app.include_router(environmental.router, prefix="/api/v1")
app.include_router(companion.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(emergency.router, prefix="/api/v1")
app.include_router(social.router, prefix="/api/v1")
app.include_router(appointments.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "PulseLink API is running!"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "firebase",
        "version": "0.1.0",
    }
