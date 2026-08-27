import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database.db import init_db
from routes.cases import router as cases_router

app = FastAPI(
    title="DetectAI - AI Crime Investigation Game API",
    description="FastAPI backend powering dynamic crime generation, suspect interrogation, prompt engineering, and AI Judge evaluation.",
    version="1.0.0"
)

# Enable CORS for Streamlit / React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(cases_router)

@app.on_event("startup")
def startup_event():
    print("[DetectAI Backend] Initializing SQLite database...")
    init_db()
    print("[DetectAI Backend] Database initialized successfully.")

@app.get("/")
def root():
    return {
        "app": "DetectAI - AI Crime Investigation Game",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
