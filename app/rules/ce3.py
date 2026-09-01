from typing import List, Dict, Any
from app.rules.constants import REASON_CODE_FRAUD_CARD_ABSENT

LOOKBACK_DAYS = 120
REQUIRED_MIN_PRIOR_TRANSACTIONS = 2


def check_ce3_eligibility(
    disputed_txn: Dict[str, Any],
    prior_txns: List[Any],
    dispute_date: int
) -> Dict[str, Any]:
    reason_code = disputed_txn.get("reason_code")
    if str(reason_code) != REASON_CODE_FRAUD_CARD_ABSENT:
        return {
            "applicable": False,
            "eligible": False,
            "reason": f"CE3 rules only apply to Fraud / Card-Not-Present disputes (Reason Code {REASON_CODE_FRAUD_CARD_ABSENT}). Current code is {reason_code}.",
            "matching_prior_transactions_count": 0,
            "requirements_met": {
                "reason_code_10_4": False,
                "undisputed_prior_txns": False,
                "data_elements_matched": False
            }
        }

    disputed_customer_id = disputed_txn.get("customer_id")
    disputed_user_id = disputed_txn.get("user_id")
    disputed_ip = disputed_txn.get("ip_address")
    disputed_device_id = disputed_txn.get("device_id")
    disputed_address = disputed_txn.get("shipping_address")

    min_timestamp = dispute_date - (LOOKBACK_DAYS * 86400)
    valid_prior_txns = []

    for txn in prior_txns:
        txn_date = getattr(txn, "order_date", 0)
        if min_timestamp <= txn_date < dispute_date:
            valid_prior_txns.append(txn)

    matching_txns = []
    for txn in valid_prior_txns:
        matched_elements = []
        if disputed_ip and getattr(txn, "ip_address", None) == disputed_ip:
            matched_elements.append("ip_address")
        if disputed_device_id and getattr(txn, "device_id", None) == disputed_device_id:
            matched_elements.append("device_id")
        if disputed_address and getattr(txn, "shipping_address", None) == disputed_address:
            matched_elements.append("shipping_address")

        if len(matched_elements) >= 2:
            matching_txns.append({
                "order_id": getattr(txn, "order_id", None),
                "order_date": getattr(txn, "order_date", None),
                "matched_elements": matched_elements
            })

    eligible = len(matching_txns) >= REQUIRED_MIN_PRIOR_TRANSACTIONS

    return {
        "applicable": True,
        "eligible": eligible,
        "reason": (
            f"Qualifies under Visa CE3 remedy rules: found {len(matching_txns)} undisputed prior transactions matching 2+ core data elements within 120 days."
            if eligible else
            f"Ineligible for CE3 remedy: found {len(matching_txns)} matching prior transactions (minimum {REQUIRED_MIN_PRIOR_TRANSACTIONS} required)."
        ),
        "matching_prior_transactions_count": len(matching_txns),
        "matching_prior_transactions": matching_txns,
        "requirements_met": {
            "reason_code_10_4": True,
            "undisputed_prior_txns": len(valid_prior_txns) >= REQUIRED_MIN_PRIOR_TRANSACTIONS,
            "data_elements_matched": eligible
        }
    }
