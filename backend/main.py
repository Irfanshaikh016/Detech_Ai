import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from contextlib import asynccontextmanager
from database.db import init_db
from routes.cases import router as cases_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[DetectAI Backend] Initializing SQLite database...")
    init_db()
    print("[DetectAI Backend] Database initialized successfully.")
    yield

app = FastAPI(
    title="DetectAI - AI Crime Investigation Game API",
    description="FastAPI backend powering dynamic crime generation, suspect interrogation, prompt engineering, and AI Judge evaluation.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit / React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Register API router
app.include_router(cases_router)

# Mount frontend directory for static assets (Noir HTML/JS UI)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
INDEX_HTML = os.path.join(FRONTEND_DIR, "index.html")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {
        "app": "DetectAI - AI Crime Investigation Game",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
