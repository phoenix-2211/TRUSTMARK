import os
import json
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Dispute
from app.rules.pipeline import run_verification
from app.eval.evaluator import load_persisted_eval_report

router = APIRouter()

WEBHOOK_SECRET_ENV_VAR = "RAZORPAY_WEBHOOK_SECRET"


def verify_razorpay_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    if not secret or not signature:
        return False
    expected_sig = hmac.new(
        secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature)


@router.post("/webhooks/razorpay/dispute")
async def handle_razorpay_dispute_webhook(request: Request, db: Session = Depends(get_db)):
    raw_body = await request.body()
    x_razorpay_signature = request.headers.get("X-Razorpay-Signature")
    webhook_secret = os.getenv(WEBHOOK_SECRET_ENV_VAR, "test_webhook_secret")

    if not x_razorpay_signature or not verify_razorpay_signature(raw_body, x_razorpay_signature, webhook_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing HMAC-SHA256 signature.",
        )

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    dispute_entity = payload.get("payload", {}).get("dispute", {}).get("entity", {})
    if not dispute_entity:
        dispute_entity = payload.get("dispute", {})

    dispute_id = dispute_entity.get("id")
    if not dispute_id:
        raise HTTPException(status_code=400, detail="Dispute entity missing required 'id' field.")

    existing = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not existing:
        new_dispute = Dispute(
            id=dispute_id,
            payment_id=dispute_entity.get("payment_id", f"pay_{dispute_id[-8:]}"),
            amount=dispute_entity.get("amount", 150000),
            currency=dispute_entity.get("currency", "INR"),
            reason_code=str(dispute_entity.get("reason_code", "13.1")),
            respond_by=int(dispute_entity.get("respond_by", 1788872451)),
            status=dispute_entity.get("status", "open"),
            phase=dispute_entity.get("phase", "chargeback"),
        )
        db.add(new_dispute)
        db.commit()

    verification_result = run_verification(dispute_id, db=db)

    return {
        "status": "success",
        "dispute_id": dispute_id,
        "verdict": verification_result["verdict"],
        "summary": verification_result["summary"],
    }


@router.get("/disputes")
def get_all_disputes(db: Session = Depends(get_db)):
    disputes = db.query(Dispute).all()
    results = []
    for d in disputes:
        v = run_verification(d.id, db=db)
        results.append(v)
    return {"disputes": results}


@router.get("/disputes/{dispute_id}")
def get_dispute_detail(dispute_id: str, db: Session = Depends(get_db)):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found.")
    return run_verification(dispute_id, db=db)


@router.get("/eval/report")
def get_eval_report():
    return load_persisted_eval_report()
