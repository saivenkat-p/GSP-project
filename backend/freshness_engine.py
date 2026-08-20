from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import models

def audit_service_freshness(db: Session) -> Dict[str, Any]:
    """
    Scans all SubService records to calculate source freshness metrics,
    flagging outdated or pending verification items.
    """
    sub_services = db.query(models.SubService).all()
    
    total = len(sub_services)
    verified = 0
    pending = 0
    outdated = 0

    for s in sub_services:
        if s.confidence_status == "VERIFIED":
            verified += 1
        elif s.confidence_status == "VERIFICATION_PENDING":
            pending += 1
        else:
            outdated += 1

    pending_queue_count = db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.review_status == "PENDING").count()

    return {
        "total_services": total,
        "verified_count": verified,
        "pending_count": pending,
        "outdated_count": outdated,
        "pending_review_queue": pending_queue_count,
        "last_source_audit": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    }

def flag_source_change(
    sub_service_id: str,
    source_url: str,
    change_summary: str,
    diff_data: dict,
    db: Session
) -> models.SourceChangeQueue:
    """
    Flags a potential document or fee change into Admin review queue
    and updates SubService status to VERIFICATION_PENDING.
    """
    sub_srv = db.query(models.SubService).filter(models.SubService.id == sub_service_id).first()
    if sub_srv:
        sub_srv.confidence_status = "VERIFICATION_PENDING"

    change_entry = models.SourceChangeQueue(
        sub_service_id=sub_service_id,
        source_url=source_url,
        detected_change_summary=change_summary,
        diff_data=diff_data,
        review_status="PENDING"
    )
    db.add(change_entry)
    db.commit()
    db.refresh(change_entry)
    return change_entry

def approve_source_version_update(
    change_queue_id: int,
    admin_name: str,
    db: Session
) -> models.SubService:
    """
    Approves a source change entry, creates a new ServiceVersion snapshot (e.g. V2.0),
    and updates confidence status back to 🟢 VERIFIED.
    """
    queue_item = db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.id == change_queue_id).first()
    if not queue_item:
        raise ValueError("Source change entry not found")

    sub_srv = db.query(models.SubService).filter(models.SubService.id == queue_item.sub_service_id).first()
    if not sub_srv:
        raise ValueError("SubService record not found")

    # Increment version code
    v_num = float(sub_srv.current_version.replace("V", "")) + 1.0
    new_version_code = f"V{v_num:.1f}"

    # Create historical version snapshot
    version_snapshot = models.ServiceVersion(
        sub_service_id=sub_srv.id,
        version_code=new_version_code,
        changes_summary=queue_item.detected_change_summary,
        snapshot_json={
            "official_fee": sub_srv.official_fee,
            "required_documents": sub_srv.required_documents,
            "diff": queue_item.diff_data
        },
        approved_by_admin=admin_name
    )
    db.add(version_snapshot)

    # Update active SubService
    sub_srv.current_version = new_version_code
    sub_srv.confidence_status = "VERIFIED"
    sub_srv.last_verified = datetime.utcnow().strftime("%Y-%m-%d")
    queue_item.review_status = "APPROVED"

    db.commit()
    db.refresh(sub_srv)
    return sub_srv
