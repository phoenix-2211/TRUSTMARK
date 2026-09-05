"""
FastAPI Main Application Entry Point for MerchantGuard.
Configures CORS middleware, mounts API routers under /api and root prefixes, and initializes database on startup.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Default to fast local mode (0.005s responses) unless explicitly overridden
os.environ.setdefault("DISABLE_LLM", "true")

from app.api.router import api_router
from app.db.database import init_db

app = FastAPI(
    title="MerchantGuard API",
    description="Dispute Evidence Readiness & Contradiction Verifier API for Razorpay AI Buildathon",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount evidence static files for document modal inspection
BASE_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = BASE_DIR / "frontend" / "public" / "evidence"
if EVIDENCE_DIR.exists():
    app.mount("/evidence", StaticFiles(directory=str(EVIDENCE_DIR)), name="evidence")

# Include router under both /api prefix and root prefix for maximum compatibility
app.include_router(api_router, prefix="/api")
app.include_router(api_router)


@app.on_event("startup")
def on_startup():
    """Ensure database tables exist on startup and auto-seed if empty."""
    init_db()
    try:
        from app.db.database import SessionLocal
        from app.db.models import Dispute
        from app.db.seed import seed_demo_data_if_empty

        db = SessionLocal()
        count = db.query(Dispute).count()
        if count == 0:
            print("[+] Database empty on cold-start boot. Auto-seeding 5 demo disputes...")
            seed_demo_data_if_empty(db)
        db.close()
    except Exception as e:
        print(f"[!] Auto-seed on boot check: {e}")


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "MerchantGuard API"}
