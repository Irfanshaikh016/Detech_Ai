"""Vercel serverless function for FastAPI backend"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from backend.database.db import init_db
    from backend.routes.cases import router as cases_router
except ImportError:
    try:
        from database.db import init_db
        from routes.cases import router as cases_router
    except ImportError as e:
        print(f"[DetectAI] Import error: {e}")
        init_db = lambda: None
        cases_router = None

app = FastAPI(
    title="DetectAI - AI Crime Investigation Game API",
    description="FastAPI backend for DetectAI - Vercel deployment",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
try:
    init_db()
    print("[DetectAI] Database initialized successfully")
except Exception as e:
    print(f"[DetectAI] Database init warning: {e}")

# Include API routes
if cases_router:
    app.include_router(cases_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "DetectAI Backend"}

@app.get("/")
def root():
    return {
        "app": "DetectAI - AI Crime Investigation Game",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }
