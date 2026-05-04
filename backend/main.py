"""FastAPI entry point for Campaign Readiness Copilot."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Load .env from project root before anything else
_root = Path(__file__).resolve().parent.parent
_env_file = _root / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)

# Allow importing parent project tools
sys.path.insert(0, str(_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router

app = FastAPI(
    title="Campaign Readiness Copilot API",
    description="AI-powered campaign planning workflow backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    key = os.getenv("AZURE_OPENAI_API_KEY", "")
    placeholder = "your-azure-openai-api-key-here"
    live = bool(key and key != placeholder)
    return {
        "status": "ok",
        "service": "Campaign Readiness Copilot API",
        "llm_mode": "live" if live else "mock",
        "provider": "azure",
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT", "(not set)"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "(not set)"),
    }
