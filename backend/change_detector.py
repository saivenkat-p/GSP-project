from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import models
from source_ingestion import compute_content_hash

def detect_record_changes(
    record_id: str,
    incoming_data: Dict[str, Any],
    db: Session
) -> Optional[models.SourceChangeQueue]:
    """
    Compares incoming source payload with existing InformationRecord.
    If differences are detected, creates a pending change review queue entry.
    """
    rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == record_id).first()
    if not rec:
        return None

    current_snapshot = {
        "title": rec.title,
        "description": rec.description,
        "benefit_amount_str": rec.benefit_amount_str,
        "application_deadline": rec.application_deadline,
        "official_statutory_fee": rec.official_statutory_fee,
        "eligibility_criteria": rec.eligibility_criteria,
        "required_documents": rec.required_documents,
        "source_url": rec.source_url
    }

    new_hash = compute_content_hash(incoming_data)
    old_hash = rec.content_hash or compute_content_hash(current_snapshot)

    if new_hash == old_hash:
        # No change detected
        return None

    # Calculate field diffs
    diffs = {}
    change_summaries = []
    
    if rec.title != incoming_data.get("title"):
        diffs["title"] = {"old": rec.title, "new": incoming_data.get("title")}
        change_summaries.append(f"Title changed from '{rec.title}' to '{incoming_data.get('title')}'")

    if rec.benefit_amount_str != incoming_data.get("benefit_amount_str"):
        diffs["benefit_amount_str"] = {"old": rec.benefit_amount_str, "new": incoming_data.get("benefit_amount_str")}
        change_summaries.append(f"Benefit amount updated from '{rec.benefit_amount_str}' to '{incoming_data.get('benefit_amount_str')}'")

    if rec.application_deadline != incoming_data.get("application_deadline"):
        diffs["application_deadline"] = {"old": rec.application_deadline, "new": incoming_data.get("application_deadline")}
        change_summaries.append(f"Application deadline changed to '{incoming_data.get('application_deadline')}'")

    if rec.official_statutory_fee != incoming_data.get("official_statutory_fee"):
        diffs["official_statutory_fee"] = {"old": rec.official_statutory_fee, "new": incoming_data.get("official_statutory_fee")}
        change_summaries.append(f"Official statutory fee changed from ₹{rec.official_statutory_fee} to ₹{incoming_data.get('official_statutory_fee')}")

    if rec.eligibility_criteria != incoming_data.get("eligibility_criteria"):
        diffs["eligibility_criteria"] = {"old": rec.eligibility_criteria, "new": incoming_data.get("eligibility_criteria")}
        change_summaries.append("Eligibility criteria modified")

    summary_text = " | ".join(change_summaries) if change_summaries else "General content update detected"

    # Flag into change queue and mark record as pending verification
    rec.verification_status = "VERIFICATION_PENDING"
    rec.last_checked = datetime.utcnow().strftime("%Y-%m-%d")

    queue_entry = models.SourceChangeQueue(
        information_record_id=rec.id,
        source_url=incoming_data.get("source_url", rec.source_url),
        detected_change_summary=summary_text,
        change_type="RULE_CHANGE",
        diff_data=diffs,
        review_status="PENDING"
    )
    db.add(queue_entry)
    db.commit()
    db.refresh(queue_entry)
    return queue_entry
