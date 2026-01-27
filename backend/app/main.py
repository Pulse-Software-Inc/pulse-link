from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import logging
from dotenv import load_dotenv

from app.routers import auth, users, biomarkers, providers
from app.core.mock_db import mock_db

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="PulseLink API",
    description="Virtual Health Companion bckend API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None
use_mock = True

if not firebase_admin._apps:
    try:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            use_mock = False
            logger.info("Firebase initialized")
        else:
            logger.warning(f"Firebase service account not found at {cred_path}")
            logger.warning("Using mock database for development")
    except Exception as e:
        logger.warning(f"Firebase initialization failed: {e}")
        logger.warning("Using mock database for development")

app.state.db = db if db else mock_db
app.state.use_mock = use_mock

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
        "database": "mock" if app.state.use_mock else "firebase",
        "version": "0.1.0"
    }