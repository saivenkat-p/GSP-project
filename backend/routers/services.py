from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/services", tags=["Services"])

@router.get("", response_model=List[schemas.ServiceOut])
def get_services(
    category: Optional[str] = None,
    state: Optional[str] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Service).filter(models.Service.status == "active")
    if category and category != "All":
        q = q.filter(models.Service.category == category)
    if state and state != "All":
        q = q.filter(models.Service.state == state)
    if query:
        q = q.filter(models.Service.official_name.ilike(f"%{query}%"))
    return q.all()

@router.get("/categories", response_model=List[str])
def get_service_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Service.category).distinct().all()
    return ["All"] + [c[0] for c in categories if c[0]]

@router.get("/{service_id}", response_model=schemas.ServiceOut)
def get_service_by_id(service_id: str, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Verified government service not found")
    return service
