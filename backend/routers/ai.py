from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import schemas
from ai_engine import process_ai_chat_navigation

router = APIRouter(prefix="/api/ai", tags=["Grounded AI Assistant"])

@router.post("/chat", response_model=schemas.AINavigationResponse)
def grounded_ai_chat(
    req: schemas.AIChatRequest,
    db: Session = Depends(get_db)
):
    return process_ai_chat_navigation(
        session_id=req.session_id or "session-default",
        query=req.query,
        state_id=req.state_id or "AP",
        district_id=req.district_id or "AP-NTR",
        mandal_name=req.mandal_name or "Vijayawada Urban",
        selected_answers=req.selected_answers,
        db=db
    )

@router.post("/navigate", response_model=schemas.AINavigationResponse)
def grounded_ai_navigate(
    req: schemas.AIChatRequest,
    db: Session = Depends(get_db)
):
    return process_ai_chat_navigation(
        session_id=req.session_id or "session-default",
        query=req.query,
        state_id=req.state_id or "AP",
        district_id=req.district_id or "AP-NTR",
        mandal_name=req.mandal_name or "Vijayawada Urban",
        selected_answers=req.selected_answers,
        db=db
    )
