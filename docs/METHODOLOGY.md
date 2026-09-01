# TRUSTMARK Verification Methodology & VAPT Severity Standards

## Core Principles
1. **Deterministic Rule Engine Priority**: AI never influences, overrides, or alters dispute verdicts or severity classifications.
2. **Zero False-Positive Target**: Clean disputes must never be falsely blocked or delayed.
3. **Strict Scoping**: Evidence validation operates on authoritative structured data records.

## Severity Tag Classifications
- `CRITICAL`: Immediate blocking issue (e.g. shipping address mismatch or date sequence impossibility). Submitting as-is will trigger issuer rejection.
- `HIGH`: Missing required evidence document for the specified reason code (e.g. missing Shipping Proof for Reason Code 13.1).
- `LOW`: Optional evidence document absent (e.g. cancellation policy not attached).
- `INFO`: Evidence document present and verified.
