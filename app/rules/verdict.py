from typing import List, Dict, Any


def determine_verdict(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    critical_count = 0
    high_count = 0
    low_count = 0

    for f in findings:
        sev = f.get("severity")
        status = f.get("status")

        if sev == "CRITICAL" and status == "FOUND_CONFLICTING":
            critical_count += 1
        elif sev == "HIGH" and (status == "MISSING_REQUIRED" or status == "FOUND_CONFLICTING"):
            high_count += 1
        elif sev == "LOW" and status == "MISSING_OPTIONAL":
            low_count += 1

    if critical_count > 0:
        verdict = "DO NOT SUBMIT — CONFLICT"
        summary = f"DO NOT SUBMIT — Detected {critical_count} CRITICAL data contradiction(s). Submitting as-is will likely trigger immediate issuer rejection."
    elif high_count > 0:
        verdict = "NEEDS REVIEW"
        summary = f"NEEDS REVIEW — Found {high_count} HIGH severity finding(s) (missing required evidence). Human review required prior to submission."
    else:
        verdict = "READY"
        summary = "READY — Evidence is internally consistent and complete for the specified reason code."

    return {
        "verdict": verdict,
        "summary": summary,
        "critical_count": critical_count,
        "high_count": high_count,
        "low_count": low_count,
    }
