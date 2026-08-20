from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
import models
import schemas

router = APIRouter(prefix="/api/locations", tags=["Location Hierarchy"])

@router.get("/tree", response_model=List[schemas.StateOut])
def get_location_tree(db: Session = Depends(get_db)):
    """Returns State -> District -> Mandal -> Locality hierarchy tree."""
    return db.query(models.State).all()

@router.get("/nearby-offices")
def get_nearby_government_offices(
    district_id: Optional[str] = "AP-NTR",
    db: Session = Depends(get_db)
):
    offices = db.query(models.GovernmentOffice).filter(models.GovernmentOffice.district_id == district_id).all()
    return offices
