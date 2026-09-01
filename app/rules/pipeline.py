from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import Dispute, OrderRecord, ShipmentRecord, DisputeEvidence, CustomerCommunicationLog
from app.rules.contradiction import (
    check_address_mismatch,
    check_date_impossibility,
    check_amount_mismatch,
    check_comms_shipment_nlp,
)
from app.rules.completeness import score_evidence_completeness
from app.rules.verdict import determine_verdict
from app.rules.ce3 import check_ce3_eligibility
from app.rules.constants import REASON_CODE_FRAUD_CARD_ABSENT


def run_verification(dispute_id: str, db: Session = None) -> Dict[str, Any]:
    close_session = False
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
        close_session = True

    try:
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()
        if not dispute:
            return {
                "dispute_id": dispute_id,
                "verdict": "NEEDS REVIEW",
                "summary": "Dispute record not found in database.",
                "merchant_guidance": "Verify dispute ID and database seeding.",
                "critical_count": 0,
                "high_count": 1,
                "low_count": 0,
                "findings": [],
                "ce3_result": {"applicable": False, "eligible": False},
            }

        order = db.query(OrderRecord).filter(OrderRecord.payment_id == dispute.payment_id).first()
        shipment = db.query(ShipmentRecord).filter(ShipmentRecord.order_id == order.order_id).first() if order else None
        evidence = db.query(DisputeEvidence).filter(DisputeEvidence.dispute_id == dispute.id).first()
        comms = db.query(CustomerCommunicationLog).filter(CustomerCommunicationLog.order_id == order.order_id).first() if order else None

        contradiction_findings = []

        if order and shipment:
            addr_check = check_address_mismatch(order.shipping_address, shipment.delivery_address)
            if addr_check["status"] == "FOUND_CONFLICTING":
                contradiction_findings.append(addr_check)

            date_check = check_date_impossibility(order.order_date, shipment.shipped_date, shipment.delivery_date)
            if date_check["status"] == "FOUND_CONFLICTING":
                contradiction_findings.append(date_check)

        if order:
            amt_check = check_amount_mismatch(dispute.amount, order.amount)
            if amt_check["status"] == "FOUND_CONFLICTING":
                contradiction_findings.append(amt_check)

        if comms and shipment:
            comms_check = check_comms_shipment_nlp(comms.log_text, shipment.carrier_status)
            if comms_check["status"] == "FOUND_CONFLICTING":
                contradiction_findings.append(comms_check)

        ce3_res = {"applicable": False, "eligible": False}
        if dispute.reason_code == REASON_CODE_FRAUD_CARD_ABSENT and order:
            prior_orders = (
                db.query(OrderRecord)
                .filter(
                    OrderRecord.customer_id == order.customer_id,
                    OrderRecord.order_id != order.order_id,
                )
                .all()
            )
            dispute_created_date = dispute.respond_by - (7 * 86400)
            ce3_res = check_ce3_eligibility(
                disputed_txn={
                    "reason_code": dispute.reason_code,
                    "customer_id": order.customer_id,
                    "user_id": order.user_id,
                    "ip_address": order.ip_address,
                    "device_id": order.device_id,
                    "shipping_address": order.shipping_address,
                },
                prior_txns=prior_orders,
                dispute_date=dispute_created_date,
            )

        all_findings = score_evidence_completeness(
            reason_code=dispute.reason_code,
            evidence_obj=evidence,
            contradiction_findings=contradiction_findings,
        )

        verdict_res = determine_verdict(all_findings)

        from app.rules.explanation_llm import generate_merchant_explanation_llm

        llm_exp = generate_merchant_explanation_llm(
            dispute_id=dispute.id,
            reason_code=dispute.reason_code,
            verdict=verdict_res["verdict"],
            findings=all_findings,
            fallback_summary=verdict_res["summary"],
            fallback_guidance=verdict_res["summary"],
        )

        return {
            "dispute_id": dispute.id,
            "payment_id": dispute.payment_id,
            "reason_code": dispute.reason_code,
            "respond_by": dispute.respond_by,
            "verdict": verdict_res["verdict"],
            "summary": llm_exp["merchant_summary"],
            "merchant_guidance": llm_exp["merchant_guidance"],
            "critical_count": verdict_res["critical_count"],
            "high_count": verdict_res["high_count"],
            "low_count": verdict_res["low_count"],
            "findings": all_findings,
            "ce3_result": ce3_res,
        }

    finally:
        if close_session:
            db.close()
