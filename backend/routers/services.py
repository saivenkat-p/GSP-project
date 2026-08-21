from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from database import get_db
import models
import schemas
from service_resolution_engine import resolve_citizen_query

router = APIRouter(prefix="/api/services", tags=["Services Taxonomy & Intelligence"])

@router.get("", response_model=List[schemas.ServiceIntelligenceOut])
def get_services(
    category: Optional[str] = None,
    state_id: Optional[str] = "AP",
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns statutory parent services and sub-services.
    Includes state-specific services + National (NAT/ALL) services so Central Govt services do not disappear.
    """
    q = db.query(models.Service)
    if category and category != "All":
        q = q.filter(models.Service.category == category)
    if state_id and state_id != "All":
        q = q.filter(models.Service.state_scope.in_([state_id, "NAT", "ALL"]))
    if query:
        q = q.filter(models.Service.official_name.ilike(f"%{query}%"))
    return q.all()

@router.get("/categories")
def get_service_categories(
    state_id: Optional[str] = "AP",
    db: Session = Depends(get_db)
):
    """
    Returns unique statutory categories directly from the database (Phase 3).
    """
    q = db.query(models.Service.category).distinct()
    if state_id and state_id != "All":
        q = q.filter(models.Service.state_scope.in_([state_id, "NAT", "ALL"]))
    categories = [c[0] for c in q.all() if c[0]]
    return ["All"] + sorted(categories)

@router.get("/taxonomy/summary", response_model=schemas.TaxonomySummaryOut)
def get_taxonomy_summary(
    state_id: Optional[str] = "AP",
    db: Session = Depends(get_db)
):
    """
    Returns live dynamically computed taxonomy counts from the database.
    Zero fabricated numbers (Phase 11).
    """
    services_q = db.query(models.Service)
    if state_id and state_id != "All":
        services_q = services_q.filter(models.Service.state_scope.in_([state_id, "NAT", "ALL"]))
    
    total_services = services_q.count()
    
    sub_q = db.query(models.SubService)
    total_sub_services = sub_q.count()
    
    cats = [c[0] for c in db.query(models.Service.category).distinct().all() if c[0]]
    
    verified_records = db.query(models.InformationRecord).filter(
        models.InformationRecord.verification_status == "VERIFIED",
        models.InformationRecord.status == "ACTIVE"
    ).count()

    return {
        "total_categories": len(cats),
        "total_services": total_services,
        "total_sub_services": total_sub_services,
        "total_verified_records": verified_records,
        "categories": sorted(cats)
    }

@router.get("/search", response_model=schemas.AINavigationResponse)
def universal_service_search(
    q: str,
    session_id: Optional[str] = "search-session",
    state_id: Optional[str] = "AP",
    district_id: Optional[str] = "AP-NTR",
    mandal_name: Optional[str] = "Vijayawada Urban",
    db: Session = Depends(get_db)
):
    """
    Universal Service Search API — Powered by Single Universal Resolution Engine.
    Accepts natural language queries, typos, aliases, and exact service terms.
    """
    return resolve_citizen_query(
        session_id=session_id,
        query=q,
        state_id=state_id,
        district_id=district_id,
        mandal_name=mandal_name,
        db=db
    )

@router.get("/catalog/{service_id}", response_model=schemas.ServiceIntelligenceOut)
def get_service_catalog_by_id(
    service_id: str,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    srv = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not srv:
        raise HTTPException(status_code=404, detail="Service record not found")

    if query:
        srv.sub_services = [
            sub for sub in srv.sub_services 
            if query.lower() in sub.sub_service_name.lower() 
            or query.lower() in sub.action_type.lower()
            or any(query.lower() in a.lower() for a in (sub.aliases or []))
        ]
    return srv

@router.get("/sub-services/{sub_id}", response_model=schemas.SubServiceOut)
def get_sub_service_by_id(
    sub_id: str,
    db: Session = Depends(get_db)
):
    sub = db.query(models.SubService).filter(models.SubService.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Sub-service record not found")
    return sub
