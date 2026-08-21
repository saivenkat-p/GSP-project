from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from database import get_db
import models
import auth
from freshness_engine import (
    audit_service_freshness,
    approve_information_change,
    reject_information_change
)

router = APIRouter(prefix="/api/freshness", tags=["Information Intelligence & Health"])

@router.get("/hero-banners")
def get_dynamic_hero_banners(
    state_id: str = "AP",
    db: Session = Depends(get_db)
):
    """
    Dynamic Government Opportunity Banners — 100% Sourced from Database Information Records.
    Only VERIFIED promotional records are returned.
    """
    records = (
        db.query(models.InformationRecord)
        .filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.is_promotional == True
        )
        .order_by(models.InformationRecord.banner_priority.desc())
        .limit(8)
        .all()
    )

    banners = []
    for r in records:
        category_icon = "🏛️"
        if "SCHOLARSHIP" in r.information_type:
            category_icon = "🎓"
        elif "BENEFIT" in r.information_type:
            category_icon = "💰"
        elif "UPDATE" in r.information_type or "RULE" in r.information_type:
            category_icon = "🔔"

        badge_text = "🟢 Government Verified" if r.badge_type == "GOVERNMENT_VERIFIED" else "🔵 Organization Verified"

        banners.append({
            "id": r.id,
            "category_tag": f"{category_icon} {r.category}",
            "title": r.title,
            "subtitle": r.description,
            "benefit_amount": r.benefit_amount_str or "Verified Opportunity",
            "tag1": r.department,
            "tag2": "100% Official Source",
            "deadline": r.application_deadline or "Active Scheme",
            "verification_badge": badge_text,
            "action_query": r.title,
            "official_source_url": r.source_url,
            "last_verified": r.last_verified,
            "color_theme": r.color_theme
        })

    return banners

@router.get("/metrics")
def get_information_health_metrics(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Information health metrics for the admin governance desk.
    """
    return audit_service_freshness(db)

@router.get("/queue")
def get_source_change_queue(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Pending change review queue entries.
    """
    return db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.review_status == "PENDING").all()

@router.post("/approve/{change_id}")
def approve_version_change(
    change_id: int,
    reason: Optional[str] = "Admin verified against official source",
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Approves change entry, increments record version, snapshots history, and logs admin audit.
    """
    try:
        updated_rec = approve_information_change(change_id, current_user.name, db, reason=reason)
        return {
            "message": f"Successfully approved change! Version incremented to {updated_rec.version}.",
            "record_id": updated_rec.id,
            "verification_status": updated_rec.verification_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reject/{change_id}")
def reject_version_change(
    change_id: int,
    reason: Optional[str] = "Rejected after official source verification",
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Rejects a pending change queue entry.
    """
    try:
        item = reject_information_change(change_id, current_user.name, db, reason=reason)
        return {
            "message": f"Change entry #{item.id} successfully rejected.",
            "status": item.review_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
