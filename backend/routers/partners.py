from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/partners", tags=["Partners Marketplace"])

@router.get("", response_model=List[schemas.PartnerOut])
def get_partners(
    district: Optional[str] = None,
    service_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.Partner).filter(models.Partner.verification_status == "verified")
    if district and district != "All":
        q = q.filter(models.Partner.district == district)
    
    partners = q.all()
    if service_id:
        partners = [p for p in partners if service_id in (p.supported_service_ids or [])]
    
    return partners

@router.get("/{partner_id}", response_model=schemas.PartnerOut)
def get_partner_by_id(partner_id: int, db: Session = Depends(get_db)):
    partner = db.query(models.Partner).filter(models.Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Verified Partner center not found")
    return partner
