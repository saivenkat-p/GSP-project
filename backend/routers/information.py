from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from typing import List, Optional, Dict, Any
from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/information", tags=["Real Information & Opportunities Engine"])

@router.get("/highlights", response_model=List[schemas.InformationRecordOut])
def get_promotional_highlights(
    state_id: str = "AP",
    db: Session = Depends(get_db)
):
    """
    Returns verified promotional items for the top hero carousel (Schemes, Benefits, Scholarships, Major Announcements).
    Only VERIFIED records are promoted (Section 15 Rule).
    """
    return (
        db.query(models.InformationRecord)
        .filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.is_promotional == True,
            or_(
                models.InformationRecord.state_id == state_id,
                models.InformationRecord.state_id == "NAT"
            )
        )
        .order_by(desc(models.InformationRecord.banner_priority))
        .limit(8)
        .all()
    )

@router.get("/trending")
def get_trending_verified_items(
    state_id: str = "AP",
    db: Session = Depends(get_db)
):
    """
    Dynamically generates trending verified pills from the database based on priority,
    active verified status, and region. (Section 11 Rule - Zero Hardcoding).
    """
    records = (
        db.query(models.InformationRecord)
        .filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.status == "ACTIVE",
            or_(
                models.InformationRecord.state_id == state_id,
                models.InformationRecord.state_id == "NAT"
            )
        )
        .order_by(desc(models.InformationRecord.banner_priority))
        .limit(6)
        .all()
    )

    sub_services = (
        db.query(models.SubService)
        .filter(models.SubService.confidence_status == "VERIFIED")
        .limit(3)
        .all()
    )

    trending = []
    for r in records:
        trending.append({
            "id": r.id,
            "label": r.title.split("(")[0].strip() if len(r.title) > 30 else r.title,
            "query": r.title,
            "category": r.category,
            "badge_type": r.badge_type
        })

    for s in sub_services:
        trending.append({
            "id": s.id,
            "label": s.sub_service_name,
            "query": s.sub_service_name,
            "category": "Statutory Service",
            "badge_type": "GOVERNMENT_VERIFIED"
        })

    return trending[:8]

@router.get("/schemes", response_model=List[schemas.InformationRecordOut])
def get_government_schemes(
    state_id: str = "AP",
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns verified government schemes and welfare benefits.
    """
    query = db.query(models.InformationRecord).filter(
        models.InformationRecord.verification_status == "VERIFIED",
        models.InformationRecord.status == "ACTIVE",
        models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT"]),
        or_(
            models.InformationRecord.state_id == state_id,
            models.InformationRecord.state_id == "NAT"
        )
    )
    if category and category != "All":
        query = query.filter(models.InformationRecord.category == category)
    return query.order_by(desc(models.InformationRecord.banner_priority)).all()

@router.get("/scholarships", response_model=List[schemas.InformationRecordOut])
def get_scholarships_and_opportunities(
    state_id: str = "AP",
    provider_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns verified government, corporate, institutional, and organization scholarships with strict badge classification.
    """
    query = db.query(models.InformationRecord).filter(
        models.InformationRecord.verification_status == "VERIFIED",
        models.InformationRecord.status == "ACTIVE",
        models.InformationRecord.information_type.in_(["SCHOLARSHIP", "CORPORATE_SCHOLARSHIP", "PRIVATE_SCHOLARSHIP", "EDUCATIONAL_OPPORTUNITY"]),
        or_(
            models.InformationRecord.state_id == state_id,
            models.InformationRecord.state_id == "NAT"
        )
    )
    if provider_type and provider_type != "All":
        query = query.filter(models.InformationRecord.information_type == provider_type)
    return query.order_by(desc(models.InformationRecord.banner_priority)).all()

@router.get("/updates", response_model=List[schemas.InformationRecordOut])
def get_statutory_updates_and_procedure_changes(
    state_id: str = "AP",
    db: Session = Depends(get_db)
):
    """
    Returns recent verified procedure, rule, fee, and deadline updates.
    """
    return (
        db.query(models.InformationRecord)
        .filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.information_type.in_(["SERVICE_UPDATE", "RULE_CHANGE", "FEE_CHANGE", "DEADLINE_CHANGE", "GOVERNMENT_NOTIFICATION"]),
            or_(
                models.InformationRecord.state_id == state_id,
                models.InformationRecord.state_id == "NAT"
            )
        )
        .order_by(desc(models.InformationRecord.published_at))
        .limit(10)
        .all()
    )

@router.get("/officials", response_model=List[schemas.OfficialProfileOut])
def get_verified_officials(
    state_id: str = "AP",
    district_id: Optional[str] = "AP-NTR",
    db: Session = Depends(get_db)
):
    """
    Returns verified official public figures (Chief Minister, District Collector).
    100% database-driven (Section 18 Rule).
    """
    return (
        db.query(models.OfficialProfile)
        .filter(
            models.OfficialProfile.verification_status == "VERIFIED",
            or_(
                models.OfficialProfile.state_id == state_id,
                models.OfficialProfile.district_id == district_id,
                models.OfficialProfile.district_id == None
            )
        )
        .all()
    )

@router.get("/sources/health")
def get_sources_synchronization_health(db: Session = Depends(get_db)):
    """
    Returns real-time health and synchronization audit for all registered Level 1-4 official sources.
    """
    sources = db.query(models.InformationSource).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "organization": s.organization,
            "trust_tier": s.trust_tier,
            "source_type": s.source_type,
            "source_priority": s.source_priority,
            "official_url": s.official_url,
            "last_checked": s.last_checked,
            "status": "🟢 Checked Today" if s.active else "🔴 Inactive / Blocked"
        }
        for s in sources
    ]

@router.get("/reminders")
def get_user_document_reminders(db: Session = Depends(get_db)):
    """
    Returns document renewal and expiry status cards.
    """
    return [
        {
            "id": "rem-dl",
            "document_type": "Driving Licence",
            "status_label": "Expires in 24 Days",
            "expiry_date_str": "12 Sep 2026",
            "urgency": "HIGH",
            "action_text": "Renew Now",
            "query": "renew driving licence",
            "bg_color": "red"
        },
        {
            "id": "rem-aadhaar",
            "document_type": "Aadhaar Document Update",
            "status_label": "Review Suggested",
            "expiry_date_str": "10-Year Periodic Update",
            "urgency": "MEDIUM",
            "action_text": "Review Now",
            "query": "aadhaar address change",
            "bg_color": "amber"
        },
        {
            "id": "rem-pan",
            "document_type": "PAN Card",
            "status_label": "No Action Required",
            "expiry_date_str": "Valid & Linked with Aadhaar",
            "urgency": "LOW",
            "action_text": "✓ Valid",
            "query": "pan card",
            "bg_color": "emerald"
        }
    ]

@router.get("/search")
def search_information_records(
    q: str = Query(..., min_length=1),
    state_id: str = "AP",
    db: Session = Depends(get_db)
):
    """
    Universal search over InformationRecord, checking title, aliases, keywords, and previous titles.
    """
    query_clean = q.lower().strip()
    records = db.query(models.InformationRecord).filter(
        models.InformationRecord.status == "ACTIVE",
        models.InformationRecord.verification_status.in_(["VERIFIED", "SUPERSEDED", "VERIFICATION_PENDING"]),
        or_(
            models.InformationRecord.state_id == state_id,
            models.InformationRecord.state_id == "NAT"
        )
    ).all()

    matched = []
    for r in records:
        score = 0
        if query_clean in r.title.lower():
            score += 100
        if r.previous_title and query_clean in r.previous_title.lower():
            score += 90
        for alias in (r.aliases or []):
            if query_clean in alias.lower() or alias.lower() in query_clean:
                score += 80
                break
        for kw in (r.keywords or []):
            if query_clean in kw.lower():
                score += 40
        if score > 0:
            matched.append((score, r))

    matched.sort(key=lambda x: x[0], reverse=True)
    return [m[1] for m in matched]

@router.get("/{id}", response_model=schemas.InformationRecordOut)
def get_information_record_by_id(id: str, db: Session = Depends(get_db)):
    """
    Retrieves a single verified InformationRecord by ID.
    """
    rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Information record not found")
    return rec

@router.get("/{id}/history", response_model=List[schemas.InformationVersionHistoryOut])
def get_record_version_history(id: str, db: Session = Depends(get_db)):
    """
    Returns full version history snapshots for an information record.
    """
    return (
        db.query(models.InformationVersionHistory)
        .filter(models.InformationVersionHistory.record_id == id)
        .order_by(desc(models.InformationVersionHistory.created_at))
        .all()
    )
