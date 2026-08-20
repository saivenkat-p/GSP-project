from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

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
    q = db.query(models.Service)
    if category and category != "All":
        q = q.filter(models.Service.category == category)
    if state_id and state_id != "All":
        q = q.filter(models.Service.state_scope == state_id)
    if query:
        q = q.filter(models.Service.official_name.ilike(f"%{query}%"))
    return q.all()

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
        query_clean = query.lower()
        filtered_sub = [
            sub for sub in srv.sub_services
            if query_clean in sub.sub_service_name.lower()
            or query_clean in sub.action_type.lower()
            or any(query_clean in alias.lower() for alias in (sub.aliases or []))
            or any(query_clean in kw.lower() for kw in (sub.keywords or []))
        ]
        srv.sub_services = filtered_sub

    return srv

@router.get("/sub-services/{sub_id}", response_model=schemas.SubServiceOut)
def get_sub_service_by_id(sub_id: str, db: Session = Depends(get_db)):
    sub = db.query(models.SubService).filter(models.SubService.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Sub-service record not found")
    return sub
