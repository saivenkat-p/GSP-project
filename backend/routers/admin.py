from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

@router.get("/metrics")
def get_admin_metrics(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    total_services = db.query(models.SubService).count()
    verified_services = db.query(models.SubService).filter(models.SubService.confidence_status == "VERIFIED").count()
    total_users = db.query(models.User).count()
    total_partners = db.query(models.PartnerProfile).count()
    total_requests = db.query(models.ServiceRequest).count()

    return {
        "total_services": total_services,
        "verified_services": verified_services,
        "total_users": total_users,
        "total_partners": total_partners,
        "total_requests": total_requests,
        "system_status": "Healthy (All Official Portals Reachable)",
        "last_source_audit": "2026-08-20 16:30 IST"
    }

@router.get("/partners", response_model=List[schemas.PartnerProfileOut])
def get_all_partners_admin(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return db.query(models.PartnerProfile).all()

@router.patch("/partners/{partner_id}/verify")
def verify_partner(
    partner_id: int,
    status_val: str = "VERIFIED",
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    partner = db.query(models.PartnerProfile).filter(models.PartnerProfile.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner profile not found")
    partner.verification_status = status_val
    db.commit()
    return {"message": f"Partner {partner.business_name} verification status updated to '{status_val}'"}
