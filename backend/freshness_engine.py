from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import models
from source_ingestion import compute_content_hash

def audit_service_freshness(db: Session) -> Dict[str, Any]:
    """
    Comprehensive freshness audit across InformationRecords, SubServices, and Sources.
    """
    records = db.query(models.InformationRecord).all()
    sub_services = db.query(models.SubService).all()
    sources = db.query(models.InformationSource).all()

    total_info = len(records)
    verified_info = sum(1 for r in records if r.verification_status == "VERIFIED")
    pending_info = sum(1 for r in records if r.verification_status == "VERIFICATION_PENDING")
    outdated_info = sum(1 for r in records if r.verification_status == "OUTDATED")
    superseded_info = sum(1 for r in records if r.verification_status == "SUPERSEDED")

    total_services = len(sub_services)
    verified_services = sum(1 for s in sub_services if s.confidence_status == "VERIFIED")
    pending_services = sum(1 for s in sub_services if s.confidence_status == "VERIFICATION_PENDING")
    outdated_services = sum(1 for s in sub_services if s.confidence_status == "OUTDATED")
    superseded_services = sum(1 for s in sub_services if s.confidence_status == "SUPERSEDED")

    pending_queue_count = db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.review_status == "PENDING").count()

    return {
        "information_records": {
            "total": total_info,
            "verified": verified_info,
            "pending": pending_info,
            "outdated": outdated_info,
            "superseded": superseded_info
        },
        "services": {
            "total": total_services,
            "verified": verified_services,
            "pending": pending_services,
            "outdated": outdated_services,
            "superseded": superseded_services
        },
        "sources": {
            "total": len(sources),
            "checked_today": sum(1 for src in sources if src.last_checked == datetime.utcnow().strftime("%Y-%m-%d")),
            "active": sum(1 for src in sources if src.active)
        },
        "pending_review_queue": pending_queue_count,
        "last_source_audit": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }

def approve_information_change(
    change_queue_id: int,
    admin_username: str,
    db: Session,
    reason: Optional[str] = "Admin manual verification from official portal"
) -> models.InformationRecord:
    """
    Approves an InformationRecord change queue item, increments version,
    creates historical version snapshot in InformationVersionHistory, and logs to AdminAuditLog.
    """
    queue_item = db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.id == change_queue_id).first()
    if not queue_item:
        raise ValueError("Source change entry not found")

    rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == queue_item.information_record_id).first()
    if not rec:
        raise ValueError("InformationRecord not found")

    # Increment version code
    v_num = float(rec.version.replace("V", "")) + 0.1
    new_version_code = f"V{v_num:.1f}"

    # Create historical version snapshot
    history_entry = models.InformationVersionHistory(
        record_id=rec.id,
        version_code=rec.version,  # Snapshot old version
        title_snapshot=rec.title,
        previous_title_snapshot=rec.previous_title,
        benefit_snapshot=rec.benefit_amount_str,
        deadline_snapshot=rec.application_deadline,
        eligibility_snapshot=rec.eligibility_criteria,
        change_summary=queue_item.detected_change_summary,
        diff_json=queue_item.diff_data,
        approved_by_admin=admin_username,
        official_effective_date=datetime.utcnow().strftime("%Y-%m-%d")
    )
    db.add(history_entry)

    # Apply diffs if any
    diffs = queue_item.diff_data or {}
    if "title" in diffs:
        rec.previous_title = rec.title
        rec.title = diffs["title"]["new"]
    if "benefit_amount_str" in diffs:
        rec.benefit_amount_str = diffs["benefit_amount_str"]["new"]
    if "application_deadline" in diffs:
        rec.application_deadline = diffs["application_deadline"]["new"]
    if "official_statutory_fee" in diffs:
        rec.official_statutory_fee = float(diffs["official_statutory_fee"]["new"])
    if "eligibility_criteria" in diffs:
        rec.eligibility_criteria = diffs["eligibility_criteria"]["new"]

    rec.version = new_version_code
    rec.verification_status = "VERIFIED"
    rec.last_verified = datetime.utcnow().strftime("%Y-%m-%d")
    queue_item.review_status = "APPROVED"

    # Admin Audit Log
    audit = models.AdminAuditLog(
        admin_username=admin_username,
        action_type="APPROVED_VERSION",
        record_type="InformationRecord",
        record_id=rec.id,
        old_value={"version": history_entry.version_code, "title": history_entry.title_snapshot},
        new_value={"version": new_version_code, "title": rec.title},
        source_url=queue_item.source_url,
        reason=reason
    )
    db.add(audit)

    db.commit()
    db.refresh(rec)
    return rec

def reject_information_change(
    change_queue_id: int,
    admin_username: str,
    db: Session,
    reason: Optional[str] = "Information could not be corroborated by official sources"
) -> models.SourceChangeQueue:
    """
    Rejects a pending change queue entry.
    """
    queue_item = db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.id == change_queue_id).first()
    if not queue_item:
        raise ValueError("Source change entry not found")

    queue_item.review_status = "REJECTED"
    
    # Revert record to VERIFIED or previous state if it was pending
    if queue_item.information_record_id:
        rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == queue_item.information_record_id).first()
        if rec:
            rec.verification_status = "VERIFIED"
    elif queue_item.sub_service_id:
        sub = db.query(models.SubService).filter(models.SubService.id == queue_item.sub_service_id).first()
        if sub:
            sub.confidence_status = "VERIFIED"

    audit = models.AdminAuditLog(
        admin_username=admin_username,
        action_type="REJECTED_CHANGE",
        record_type="SourceChangeQueue",
        record_id=str(queue_item.id),
        source_url=queue_item.source_url,
        reason=reason
    )
    db.add(audit)
    db.commit()
    return queue_item
