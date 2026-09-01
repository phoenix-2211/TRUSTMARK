import os
import json
import urllib.request
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"

_LLM_CACHE = {}

SYSTEM_PROMPT = """You are an expert merchant risk auditor for MerchantGuard.
Your task is to convert deterministic dispute verification findings into a clear, helpful merchant explanation.

HARD CONSTRAINTS:
1. PURELY ADVISORY: You must NEVER change, override, or disagree with the engine's verdict (READY, NEEDS REVIEW, DO NOT SUBMIT) or finding severity tags (CRITICAL, HIGH, LOW).
2. STRICT FACTUAL ACCURACY: Do NOT invent any facts, evidence documents, or addresses not explicitly provided in the findings input.
3. ETHICAL GUIDANCE: Never suggest the merchant fabricate, alter, or falsify evidence to "pass" checks. Only advise verifying carrier records or rectifying genuine data entry errors.
4. CONCISE OUTPUT: Output ONLY a valid JSON object matching this exact schema (no markdown, no code fences):
{
  "merchant_summary": "Short 8-15 word plain-language summary for top banner",
  "merchant_guidance": "2-4 sentence explanation referencing findings and recommended next steps"
}"""


def generate_merchant_explanation_llm(
    dispute_id: str,
    reason_code: str,
    verdict: str,
    findings: list,
    fallback_summary: str,
    fallback_guidance: str,
    force_refresh: bool = False,
) -> dict:
    if not force_refresh and dispute_id in _LLM_CACHE:
        return _LLM_CACHE[dispute_id]

    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if os.getenv("DISABLE_LLM") == "true" or not api_key or "your_" in api_key or api_key == "your_openrouter_api_key_here":
        res = {"merchant_summary": fallback_summary, "merchant_guidance": fallback_guidance}
        _LLM_CACHE[dispute_id] = res
        return res

    simplified_findings = []
    for f in findings:
        simplified_findings.append({
            "check": f.get("check_name") or f.get("field"),
            "status": f.get("status"),
            "severity": f.get("severity"),
            "finding_detail": f.get("explanation"),
        })

    user_prompt = f"""Dispute ID: {dispute_id}
Reason Code: {reason_code}
Engine Verdict: {verdict}

Engine Verification Findings:
{json.dumps(simplified_findings, indent=2)}

Please generate the merchant summary (8-15 words) and merchant guidance (2-4 sentences). Output JSON ONLY."""

    candidate_models = [DEFAULT_MODEL, "nvidia/nemotron-3.5-lightning:free", "inclusionai/ling-3.0-flash-fin:free"]

    for model_name in candidate_models:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 250,
        }

        raw_body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            OPENROUTER_API_URL,
            data=raw_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://merchantguard.local",
                "X-Title": "Trustmark",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                resp_bytes = response.read()
                resp_data = json.loads(resp_bytes.decode("utf-8"))

                msg = resp_data["choices"][0]["message"]
                content = msg.get("content") or ""
                if not content and "reasoning_details" in msg and isinstance(msg["reasoning_details"], list) and len(msg["reasoning_details"]) > 0:
                    content = msg["reasoning_details"][0].get("text") or ""
                if not content and "reasoning" in msg and isinstance(msg["reasoning"], str):
                    content = msg["reasoning"]

                content = content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                parsed = {}
                try:
                    parsed = json.loads(content.strip())
                except Exception:
                    import re
                    s_match = re.search(r'"merchant_summary":\s*"([^"]+)"', content)
                    g_match = re.search(r'"merchant_guidance":\s*"([^"]+)"', content)
                    if s_match:
                        parsed["merchant_summary"] = s_match.group(1)
                    if g_match:
                        parsed["merchant_guidance"] = g_match.group(1)

                merchant_summary = parsed.get("merchant_summary") or fallback_summary
                merchant_guidance = parsed.get("merchant_guidance") or fallback_guidance

                result = {
                    "merchant_summary": merchant_summary,
                    "merchant_guidance": merchant_guidance,
                    "model_used": model_name,
                    "raw_response": resp_data
                }
                _LLM_CACHE[dispute_id] = result
                return result

        except Exception as e:
            print(f"[!] OpenRouter model '{model_name}' failed for {dispute_id}: {e}. Trying next candidate...")
            continue

    res = {"merchant_summary": fallback_summary, "merchant_guidance": fallback_guidance, "model_used": "static_fallback", "raw_response": None}
    _LLM_CACHE[dispute_id] = res
    return res
