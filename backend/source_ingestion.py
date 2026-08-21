import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import models

def compute_content_hash(payload: Dict[str, Any]) -> str:
    """
    Computes deterministic MD5 hash of standardized information fields
    to detect changes across title, benefits, deadlines, fees, and rules.
    """
    normalized_string = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.md5(normalized_string.encode("utf-8")).hexdigest()

def normalize_scraped_record(
    raw_title: str,
    raw_desc: str,
    benefit_amount: Optional[str],
    deadline: Optional[str],
    fee: float,
    eligibility_list: list,
    documents_list: list,
    source_url: str
) -> Dict[str, Any]:
    """
    Standardizes scraped/fetched payload into canonical structure for diff comparisons.
    """
    return {
        "title": raw_title.strip(),
        "description": raw_desc.strip(),
        "benefit_amount_str": benefit_amount.strip() if benefit_amount else None,
        "application_deadline": deadline.strip() if deadline else None,
        "official_statutory_fee": float(fee),
        "eligibility_criteria": [e.strip() for e in eligibility_list if e],
        "required_documents": documents_list,
        "source_url": source_url.strip()
    }
