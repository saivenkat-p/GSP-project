from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/partners", tags=["Partners Marketplace"])

@router.get("", response_model=List[schemas.PartnerProfileOut])
def get_partners(
    district_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    q = db.query(models.PartnerProfile).filter(models.PartnerProfile.verification_status == "VERIFIED")
    if district_id and district_id != "All":
        q = q.filter(models.PartnerProfile.district_id == district_id)
    
    return q.all()

@router.get("/{partner_id}", response_model=schemas.PartnerProfileOut)
def get_partner_by_id(partner_id: int, db: Session = Depends(get_db)):
    partner = db.query(models.PartnerProfile).filter(models.PartnerProfile.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Verified Partner center not found")
    return partner
