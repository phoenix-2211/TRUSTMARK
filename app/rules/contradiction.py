import Levenshtein
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer, util
from app.data_gen.phrasings import CUSTOMER_NOT_RECEIVED_PHRASINGS

SIMILARITY_THRESHOLD = 0.85
_EMBEDDING_MODEL = None
_PHRASING_EMBEDDINGS = None
_COMMS_CACHE = {}


def get_embedding_model():
    global _EMBEDDING_MODEL, _PHRASING_EMBEDDINGS
    if _EMBEDDING_MODEL is None:
        _EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        _PHRASING_EMBEDDINGS = _EMBEDDING_MODEL.encode(
            CUSTOMER_NOT_RECEIVED_PHRASINGS,
            convert_to_tensor=True
        )
    return _EMBEDDING_MODEL, _PHRASING_EMBEDDINGS


def format_vapt_finding(severity: str, detail: str) -> str:
    if severity == "CRITICAL":
        return f"CRITICAL — {detail}"
    elif severity == "HIGH":
        return f"HIGH — {detail}"
    elif severity == "LOW":
        return f"LOW — {detail}"
    return f"INFO — {detail}"


def normalize_address(addr: str) -> str:
    if not addr:
        return ""
    addr = addr.lower().strip()
    replacements = {
        "street": "st", "road": "rd", "avenue": "ave",
        "boulevard": "blvd", "apartment": "apt", "suite": "ste",
        "north": "n", "south": "s", "east": "e", "west": "w",
        ",": " ", ".": " "
    }
    for orig, rep in replacements.items():
        addr = addr.replace(orig, rep)
    return " ".join(addr.split())


def check_address_mismatch(shipping_address: str, delivery_address: str) -> Dict[str, Any]:
    norm_ship = normalize_address(shipping_address)
    norm_del = normalize_address(delivery_address)

    if not norm_ship or not norm_del:
        return {
            "check_name": "address_mismatch",
            "status": "MISSING_DATA",
            "severity": "LOW",
            "explanation": format_vapt_finding("LOW", "Shipping or delivery address data missing for verification.")
        }

    distance = Levenshtein.distance(norm_ship, norm_del)
    max_len = max(len(norm_ship), len(norm_del))
    ratio = 1.0 - (distance / max_len) if max_len > 0 else 1.0

    if ratio < SIMILARITY_THRESHOLD:
        return {
            "check_name": "address_mismatch",
            "status": "FOUND_CONFLICTING",
            "severity": "CRITICAL",
            "explanation": format_vapt_finding(
                "CRITICAL",
                f"shipping address on order ('{shipping_address}') does not match shipment record ('{delivery_address}'). This mismatch alone is likely to trigger issuer rejection."
            )
        }

    return {
        "check_name": "address_mismatch",
        "status": "VERIFIED_MATCH",
        "severity": "INFO",
        "explanation": format_vapt_finding(None, "Shipping and delivery addresses match within similarity threshold.")
    }


def check_date_impossibility(order_date: int, shipped_date: int, delivery_date: int = None) -> Dict[str, Any]:
    if order_date and shipped_date and shipped_date < order_date:
        return {
            "check_name": "date_impossibility",
            "status": "FOUND_CONFLICTING",
            "severity": "CRITICAL",
            "explanation": format_vapt_finding(
                "CRITICAL",
                f"Shipment date ({shipped_date}) occurs BEFORE order placement date ({order_date}). Logical impossibility."
            )
        }

    if shipped_date and delivery_date and delivery_date < shipped_date:
        return {
            "check_name": "date_impossibility",
            "status": "FOUND_CONFLICTING",
            "severity": "CRITICAL",
            "explanation": format_vapt_finding(
                "CRITICAL",
                f"Delivery date ({delivery_date}) occurs BEFORE shipment date ({shipped_date}). Logical impossibility."
            )
        }

    return {
        "check_name": "date_impossibility",
        "status": "VERIFIED_MATCH",
        "severity": "INFO",
        "explanation": format_vapt_finding(None, "Order, shipment, and delivery timeline sequence is chronologically valid.")
    }


def check_amount_mismatch(dispute_amount: int, order_amount: int) -> Dict[str, Any]:
    if dispute_amount and order_amount and dispute_amount != order_amount:
        return {
            "check_name": "amount_mismatch",
            "status": "FOUND_CONFLICTING",
            "severity": "CRITICAL",
            "explanation": format_vapt_finding(
                "CRITICAL",
                f"Dispute amount ({dispute_amount} paise) does not match original order amount ({order_amount} paise)."
            )
        }

    return {
        "check_name": "amount_mismatch",
        "status": "VERIFIED_MATCH",
        "severity": "INFO",
        "explanation": format_vapt_finding(None, "Dispute amount exactly matches original order amount.")
    }


def check_comms_shipment_nlp(comms_text: str, carrier_status: str) -> Dict[str, Any]:
    if not comms_text or not carrier_status:
        return {
            "check_name": "comms_shipment_nlp",
            "status": "MISSING_DATA",
            "severity": "LOW",
            "explanation": format_vapt_finding("LOW", "Customer communication log or carrier status is absent.")
        }

    carrier_delivered = carrier_status.lower() in ["delivered", "delivered_signed"]

    if not carrier_delivered:
        return {
            "check_name": "comms_shipment_nlp",
            "status": "VERIFIED_MATCH",
            "severity": "INFO",
            "explanation": format_vapt_finding(None, "Carrier status is not marked delivered; no contradiction.")
        }

    global _COMMS_CACHE
    if comms_text in _COMMS_CACHE:
        max_sim = _COMMS_CACHE[comms_text]
    else:
        try:
            model, phrasing_embeddings = get_embedding_model()
            comms_embedding = model.encode(comms_text, convert_to_tensor=True)
            cosine_scores = util.cos_sim(comms_embedding, phrasing_embeddings)[0]
            max_sim = float(max(cosine_scores))
            _COMMS_CACHE[comms_text] = max_sim
        except Exception:
            max_sim = 0.9 if ("not received" in comms_text.lower() or "missing" in comms_text.lower()) else 0.0

    if max_sim >= 0.65:
        return {
            "check_name": "comms_shipment_nlp",
            "status": "FOUND_CONFLICTING",
            "severity": "HIGH",
            "explanation": format_vapt_finding(
                "HIGH",
                f"Customer chat log claims non-receipt ('{comms_text}') but shipping carrier status confirms 'Delivered'. Contradiction score: {max_sim:.2f}."
            )
        }

    return {
        "check_name": "comms_shipment_nlp",
        "status": "VERIFIED_MATCH",
        "severity": "INFO",
        "explanation": format_vapt_finding(None, f"Customer communication is consistent with carrier delivery status (Score: {max_sim:.2f}).")
    }
