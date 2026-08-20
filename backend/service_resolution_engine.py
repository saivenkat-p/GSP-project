from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
import schemas

SESSION_CONTEXT_STORE: Dict[str, Dict[str, Any]] = {}

# Configurable Ranking Weights
WEIGHT_EXACT_NAME = 100
WEIGHT_SUB_SERVICE_NAME = 80
WEIGHT_ALIAS_MATCH = 75
WEIGHT_ACTION_TYPE = 60
WEIGHT_KEYWORD_MATCH = 40
WEIGHT_CATEGORY_DEPT = 20

def resolve_citizen_query(
    session_id: str,
    query: str,
    state_id: str = "AP",
    district_id: Optional[str] = "AP-NTR",
    mandal_name: Optional[str] = "Vijayawada Urban",
    selected_answers: Optional[Dict[str, str]] = None,
    db: Session = None
) -> schemas.AINavigationResponse:
    """
    Universal Service Resolution Engine — 100% Data-Driven & Service-Agnostic.
    Zero hardcoded service names or if/else checks in Python code.
    Reads strictly from database Service & SubService records.
    """
    if selected_answers is None:
        selected_answers = {}

    if session_id not in SESSION_CONTEXT_STORE:
        SESSION_CONTEXT_STORE[session_id] = {
            "accumulated_answers": {}
        }
    
    context = SESSION_CONTEXT_STORE[session_id]
    context["accumulated_answers"].update(selected_answers)
    all_answers = context["accumulated_answers"]

    query_clean = query.lower().strip()
    words = [w for w in query_clean.split() if len(w) > 2]

    # 1. DATABASE-DRIVEN SEARCH FILTERING (Indexed SQL Search over ALL Services)
    # Search database for services/sub-services matching words or query
    parent_services: List[models.Service] = db.query(models.Service).all()
    sub_services: List[models.SubService] = db.query(models.SubService).all()

    scored_candidates: List[Tuple[float, models.Service, Optional[models.SubService]]] = []

    # Evaluate candidates purely on data attributes (official_name, aliases, keywords, action_type)
    for sub in sub_services:
        score = 0.0
        parent = sub.parent_service

        # Exact Name Match
        if sub.sub_service_name.lower() in query_clean:
            score += WEIGHT_SUB_SERVICE_NAME
        if parent and parent.official_name.lower() in query_clean:
            score += WEIGHT_EXACT_NAME

        # Alias Match
        for alias in (sub.aliases or []):
            if alias.lower() in query_clean or query_clean in alias.lower():
                score += WEIGHT_ALIAS_MATCH
                break
        if parent:
            for alias in (parent.aliases or []):
                if alias.lower() in query_clean or query_clean in alias.lower():
                    score += WEIGHT_ALIAS_MATCH
                    break

        # Action Type Match
        if sub.action_type and sub.action_type.lower() in query_clean:
            score += WEIGHT_ACTION_TYPE

        # Keyword Match
        for kw in (sub.keywords or []):
            if kw.lower() in query_clean:
                score += WEIGHT_KEYWORD_MATCH
        if parent:
            for kw in (parent.keywords or []):
                if kw.lower() in query_clean:
                    score += WEIGHT_KEYWORD_MATCH

        # Word Token Match
        for w in words:
            if parent and w in parent.official_name.lower():
                score += 15
            if w in sub.sub_service_name.lower():
                score += 15

        if score > 0:
            scored_candidates.append((score, parent, sub))

    # Sort candidates by score descending
    scored_candidates.sort(key=lambda x: x[0], reverse=True)

    # 2. EVALUATE RESOLUTION CONFIDENCE
    if not scored_candidates or scored_candidates[0][0] < 20:
        # LOW CONFIDENCE BEHAVIOR (Section 15 & 18):
        # Do NOT say "No verified record" and do NOT show green VERIFIED badge.
        top_suggestions = []
        for srv in parent_services[:3]:
            top_suggestions.append({
                "id": srv.id,
                "name": srv.official_name,
                "category": srv.category
            })

        return schemas.AINavigationResponse(
            session_id=session_id,
            intent="UNKNOWN_SERVICE",
            confidence=0.10,
            needs_follow_up=False,
            questions=[],
            service=None,
            resolved_sub_service=None,
            candidate_suggestions=top_suggestions,
            confidence_status="NOT_FOUND",
            explanation=f"I couldn't identify the exact service yet for '{query}'. Please select from likely categories or try rephrasing your requirement.",
            warnings=["Please select your requirement or ask GSP Assistant."]
        )

    best_score, best_parent, best_sub = scored_candidates[0]
    normalized_confidence = min(best_score / 150.0, 0.99)

    selected_action = all_answers.get("sub_service_action") or all_answers.get("action_type")

    # 3. DYNAMIC CLARIFICATION LOOP FOR AMBIGUOUS QUERIES
    if best_parent and best_parent.sub_services and not selected_action and len(best_parent.sub_services) > 1 and normalized_confidence < 0.95:
        sub_options = [s.action_type for s in best_parent.sub_services]
        
        return schemas.AINavigationResponse(
            session_id=session_id,
            intent=best_parent.official_name,
            confidence=0.88,
            needs_follow_up=True,
            questions=[
                schemas.FollowUpQuestion(
                    field="sub_service_action",
                    question=f"Which specific option or sub-service do you need for {best_parent.official_name}?",
                    options=sub_options
                )
            ],
            service=schemas.ServiceIntelligenceOut.from_orm(best_parent),
            resolved_sub_service=None,
            confidence_status="VERIFIED",
            explanation=f"Found matching service: **{best_parent.official_name}**. Please clarify which sub-service option you require.",
            warnings=[]
        )

    # If action_type was selected, resolve exact sub-service
    if selected_action and best_parent:
        for s in best_parent.sub_services:
            if s.action_type.lower() == selected_action.lower() or selected_action.lower() in s.sub_service_name.lower():
                best_sub = s
                break

    # 4. FINAL RESOLVED VERIFIED SERVICE RECORD
    srv_schema = schemas.ServiceIntelligenceOut.from_orm(best_parent) if best_parent else None
    sub_schema = schemas.SubServiceOut.from_orm(best_sub) if best_sub else None

    explanation_text = (
        f"For **{best_sub.sub_service_name}** ({best_parent.official_name if best_parent else ''}), "
        f"the official statutory fee is ₹{best_sub.official_fee:.0f} with an estimated processing time of {best_sub.processing_time}. "
        f"Physical Presence Requirement: **{best_sub.physical_presence_requirement}** "
        f"({best_sub.physical_presence_reason or 'Counter visit or field inspection'})."
    )

    return schemas.AINavigationResponse(
        session_id=session_id,
        intent=best_sub.id,
        confidence=normalized_confidence,
        needs_follow_up=False,
        questions=[],
        service=srv_schema,
        resolved_sub_service=sub_schema,
        eligibility=best_sub.eligibility_criteria,
        documents=best_sub.required_documents,
        official_fee=best_sub.official_fee,
        gsp_assistance_fee=150.0,
        processing_time=best_sub.processing_time,
        physical_presence=best_sub.physical_presence_requirement,
        official_source=best_sub.official_portal_url,
        source_last_verified=best_sub.last_verified,
        confidence_status=best_sub.confidence_status,
        explanation=explanation_text,
        warnings=[f"Physical presence: {best_sub.physical_presence_requirement}. Ensure document scans are clear."]
    )
