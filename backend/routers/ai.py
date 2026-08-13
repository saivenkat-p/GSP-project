from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import schemas
from ai_engine import process_ai_navigation

router = APIRouter(prefix="/api/ai", tags=["AI Navigator"])

@router.post("/navigate", response_model=schemas.AINavigationResponse)
def navigate_ai_service(
    request: schemas.AIQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Grounded AI Service Discovery Endpoint:
    Returns strict JSON response matching AI Navigation contract (Feedback Item #5).
    """
    return process_ai_navigation(
        query=request.query,
        state=request.state or "Andhra Pradesh",
        district=request.district,
        selected_answers=request.selected_answers,
        db=db
    )
