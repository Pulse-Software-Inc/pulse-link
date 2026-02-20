from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging
from dotenv import load_dotenv

from app.routers import auth, users, biomarkers, providers

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PulseLink API",
    description="Virtual Health Companion bckend API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# check for mock mode (for CI/testing)
use_mock = os.getenv("USE_MOCK", "false").lower() == "true"

if use_mock:
    logger.info("Using mock database mode")
    from app.core.mock_db import mock_db
    app.state.db = mock_db
    app.state.use_mock = True
elif not firebase_admin._apps:
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
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
