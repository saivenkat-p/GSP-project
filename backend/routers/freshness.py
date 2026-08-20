from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
import models
import auth
from freshness_engine import audit_service_freshness, approve_source_version_update, flag_source_change

router = APIRouter(prefix="/api/freshness", tags=["Information Intelligence & Health"])

@router.get("/metrics")
def get_information_health_metrics(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return audit_service_freshness(db)

@router.get("/queue")
def get_source_change_queue(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.review_status == "PENDING").all()

@router.post("/approve/{change_id}")
def approve_version_change(
    change_id: int,
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    try:
        updated_sub = approve_source_version_update(change_id, current_user.name, db)
        return {
            "message": f"Successfully approved change! Version incremented to {updated_sub.current_version}.",
            "sub_service_id": updated_sub.id,
            "status": updated_sub.confidence_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
