# TRUSTMARK Engineering Build Specification

## System Overview
TRUSTMARK is a zero-hallucination pre-submission chargeback evidence verification platform. It operates deterministically over structured dispute evidence to ensure evidence completeness and detect data contradictions before submission to card networks (Razorpay, Visa, Mastercard).

## Architecture Layers
1. **REST API & Webhook Router**: FastAPI listener with HMAC-SHA256 signature verification (`X-Razorpay-Signature`).
2. **Deterministic Rules Engine**: Core verification logic for address similarity (Levenshtein), chronological sequence, amount parity, and customer chat sentiment contradictions.
3. **Visa Compulsory Evidence 3.0 (CE3) Engine**: Evaluates prior 120-day customer transaction histories for matching IP, device ID, and shipping locations.
4. **Advisory LLM Explanation Layer**: OpenRouter API integration providing plain-language merchant guidance with 100% graceful fallback.
5. **Interactive Dashboard**: React 18 + Vite UI for queue management, evidence library inspection, and benchmark reporting.
