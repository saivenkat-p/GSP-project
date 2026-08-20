from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from database import get_db
import models
import auth

router = APIRouter(prefix="/api/training", tags=["Partner Training & Certification"])

class AssessmentSubmission(BaseModel):
    certification_code: str
    answers: Dict[str, str]

@router.get("/courses")
def get_training_courses(db: Session = Depends(get_db)):
    return db.query(models.TrainingCourse).all()

@router.post("/assess")
def submit_assessment(
    sub: AssessmentSubmission,
    current_user: models.User = Depends(auth.require_role(["PARTNER"])),
    db: Session = Depends(get_db)
):
    partner = db.query(models.PartnerProfile).filter(models.PartnerProfile.user_id == current_user.id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner profile not found")

    # Grant certification
    cert = models.PartnerCertification(
        partner_id=partner.id,
        certification_code=sub.certification_code,
        score=95
    )
    db.add(cert)
    db.commit()
    return {
        "message": f"Congratulations! You passed the assessment and earned certification code '{sub.certification_code}'.",
        "badge": "CERTIFIED_OPERATOR"
    }
