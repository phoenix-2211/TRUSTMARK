from typing import List, Dict, Any
from app.rules.constants import REQUIRED_DOCS_BY_REASON

VAPT_FINDING_TEMPLATES = {
    "MISSING_REQUIRED": "CRITICAL — Required evidence document '{doc_name}' is missing for reason code {reason_code}.",
    "MISSING_OPTIONAL": "LOW — Optional evidence document '{doc_name}' is absent.",
    "PRESENT_VALID": "INFO — Evidence document '{doc_name}' is present and verified.",
}


def score_evidence_completeness(
    reason_code: str,
    evidence_obj: Any,
    contradiction_findings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    findings = list(contradiction_findings) if contradiction_findings else []
    required_docs = REQUIRED_DOCS_BY_REASON.get(reason_code, [])

    all_possible_docs = [
        "shipping_proof", "billing_proof", "cancellation_proof",
        "customer_communication", "proof_of_service", "explanation_letter",
        "refund_confirmation", "access_activity_log",
        "refund_cancellation_policy", "term_and_conditions"
    ]

    for doc in all_possible_docs:
        has_doc = False
        if evidence_obj:
            val = getattr(evidence_obj, doc, None)
            if val is not None and val != {} and val != "":
                has_doc = True

        if doc in required_docs:
            if not has_doc:
                findings.append({
                    "check_name": f"doc_{doc}",
                    "status": "MISSING_REQUIRED",
                    "severity": "HIGH",
                    "field": doc,
                    "explanation": f"HIGH — Required evidence document '{doc}' is missing for Reason Code {reason_code}."
                })
            else:
                findings.append({
                    "check_name": f"doc_{doc}",
                    "status": "PRESENT_VALID",
                    "severity": "INFO",
                    "field": doc,
                    "explanation": f"INFO — Required evidence document '{doc}' is present."
                })
        else:
            if not has_doc:
                findings.append({
                    "check_name": f"doc_{doc}",
                    "status": "MISSING_OPTIONAL",
                    "severity": "LOW",
                    "field": doc,
                    "explanation": f"LOW — Optional evidence document '{doc}' is absent."
                })

    return findings
