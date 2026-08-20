from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/requests", tags=["Service Requests & Timeline"])

@router.post("", response_model=schemas.ServiceRequestOut)
def create_service_request(
    req_in: schemas.ServiceRequestCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    sub_service = db.query(models.SubService).filter(models.SubService.id == req_in.sub_service_id).first()
    if not sub_service:
        raise HTTPException(status_code=404, detail="Sub-service not found")

    new_request = models.ServiceRequest(
        citizen_id=current_user.id,
        sub_service_id=req_in.sub_service_id,
        assistance_tier=req_in.assistance_tier or "LEVEL_B_FORM_HELP",
        status="NEW",
        citizen_location_str=req_in.citizen_location_str or "Vijayawada, NTR District (AP)",
        notes=req_in.notes,
        callback_requested=req_in.callback_requested,
        official_statutory_fee=sub_service.official_fee,
        gsp_assistance_fee=150.0,
        partner_commission=100.0
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request

@router.get("", response_model=List[schemas.ServiceRequestOut])
def get_user_service_requests(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role == "PARTNER":
        partner = db.query(models.PartnerProfile).filter(models.PartnerProfile.user_id == current_user.id).first()
        if not partner:
            return []
        return db.query(models.ServiceRequest).filter(models.ServiceRequest.partner_id == partner.id).all()
    elif current_user.role in ["STAFF", "ADMIN"]:
        return db.query(models.ServiceRequest).all()
    else:
        return db.query(models.ServiceRequest).filter(models.ServiceRequest.citizen_id == current_user.id).all()

@router.get("/{request_id}", response_model=schemas.ServiceRequestOut)
def get_service_request_by_id(
    request_id: int,
    db: Session = Depends(get_db)
):
    req = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service request not found")
    return req
