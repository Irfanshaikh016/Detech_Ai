"""
Vercel serverless handler for DetectAI FastAPI backend
Uses Mangum to adapt FastAPI (ASGI) to AWS Lambda
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules
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
    description="FastAPI backend for DetectAI - Vercel serverless deployment",
    version="1.0.0"
)

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    init_db()
    print("[DetectAI] Database initialized successfully")
except Exception as e:
    print(f"[DetectAI] Database init warning: {e}")

# Include API routes
if cases_router:
    app.include_router(cases_router, prefix="/api")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DetectAI Backend"}

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "app": "DetectAI - AI Crime Investigation Game",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Mangum handler for Vercel
handler = Mangum(app)
