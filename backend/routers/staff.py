from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models
import schemas
import auth

router = APIRouter(prefix="/api/staff", tags=["Staff Lead Operations Desk"])

class LeadStatusUpdate(BaseModel):
    status: str # One of 14 statuses
    notes: Optional[str] = None
    official_application_no: Optional[str] = None
    partner_id: Optional[int] = None

class AddNoteRequest(BaseModel):
    note_text: str

@router.get("/leads", response_model=List[schemas.ServiceRequestOut])
def get_staff_leads_queue(
    status_filter: Optional[str] = None,
    current_user: models.User = Depends(auth.require_role(["STAFF", "ADMIN"])),
    db: Session = Depends(get_db)
):
    q = db.query(models.ServiceRequest)
    if status_filter and status_filter != "ALL":
        q = q.filter(models.ServiceRequest.status == status_filter)
    return q.all()

@router.patch("/leads/{request_id}/status")
def update_lead_status(
    request_id: int,
    upd: LeadStatusUpdate,
    current_user: models.User = Depends(auth.require_role(["STAFF", "ADMIN"])),
    db: Session = Depends(get_db)
):
    req = db.query(models.ServiceRequest).filter(models.ServiceRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Service lead request not found")

    req.status = upd.status
    if upd.notes:
        req.notes = upd.notes
    if upd.official_application_no:
        req.official_application_no = upd.official_application_no
    if upd.partner_id:
        req.partner_id = upd.partner_id

    # Create note log
    note = models.RequestNote(
        service_request_id=req.id,
        author_name=current_user.name,
        author_role="STAFF",
        note_text=f"Status updated to '{upd.status}'. Notes: {upd.notes or 'None'}"
    )
    db.add(note)
    db.commit()
    return {"message": f"Lead #{request_id} status updated to {upd.status}"}

@router.post("/leads/{request_id}/notes")
def add_lead_note(
    request_id: int,
    req_note: AddNoteRequest,
    current_user: models.User = Depends(auth.require_role(["STAFF", "ADMIN", "PARTNER"])),
    db: Session = Depends(get_db)
):
    note = models.RequestNote(
        service_request_id=request_id,
        author_name=current_user.name,
        author_role=current_user.role,
        note_text=req_note.note_text
    )
    db.add(note)
    db.commit()
    return {"message": "Note added successfully"}
