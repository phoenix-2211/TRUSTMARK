REASON_CODE_FRAUD_CARD_ABSENT = "10.4"
REASON_CODE_MERCHANDISE_SERVICES_NOT_RECEIVED = "13.1"

REQUIRED_DOCS_BY_REASON = {
    "10.4": ["access_activity_log", "proof_of_service", "billing_proof"],
    "13.1": ["shipping_proof", "customer_communication", "term_and_conditions"]
}
