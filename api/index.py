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

from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

# Include API routes
if cases_router:
    app.include_router(cases_router)

# Mount frontend directory for static assets if present
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    favicon_path = os.path.join(FRONTEND_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    svg_icon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🔍</text></svg>'
    return Response(content=svg_icon, media_type="image/svg+xml")

@app.get("/api/scenarios")
def scenarios():
    try:
        from backend.services.mock_cases import list_scenarios
    except ImportError:
        from services.mock_cases import list_scenarios
    return {"status": "success", "scenarios": list_scenarios()}

@app.get("/api/health")
def api_health_check():
    """API health check endpoint"""
    return {"status": "ok"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DetectAI Backend"}

@app.get("/")
def root():
    """Root endpoint"""
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {
        "app": "DetectAI - AI Crime Investigation Game",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# Mangum handler for Vercel
handler = Mangum(app)

