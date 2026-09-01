from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import router as api_router
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TRUSTMARK Engine API",
    description="Pre-Submission Chargeback Evidence Verification Engine API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "name": "TRUSTMARK API",
        "status": "online",
        "documentation": "/docs"
    }
