from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import models
import schemas

def process_ai_navigation(
    query: str,
    state: str = "Andhra Pradesh",
    district: Optional[str] = None,
    selected_answers: Optional[Dict[str, str]] = None,
    db: Session = None
) -> schemas.AINavigationResponse:
    """
    Grounded AI Service Navigation Engine (Strict JSON Schema Output)
    Pipeline:
      1. Natural Language Intent Classification & Term Matching
      2. Verified Knowledge Retrieval against Database Services
      3. Missing Field Identification (District, Purpose, Caste Category)
      4. Grounded Response Formulation (Zero Hallucination)
    """
    if selected_answers is None:
        selected_answers = {}

    query_clean = query.lower().strip()
    
    # 1. RETRIEVE ALL VERIFIED SERVICES FOR MATCHING
    services: List[models.Service] = db.query(models.Service).filter(models.Service.status == "active").all()
    
    best_match: Optional[models.Service] = None
    max_score = 0

    # Keyword scoring algorithm against verified key_terms & official_name
    for service in services:
        score = 0
        for term in service.key_terms:
            if term.lower() in query_clean:
                score += 2
        if service.category.lower() in query_clean:
            score += 1
        if service.official_name.lower() in query_clean:
            score += 4
            
        if score > max_score:
            max_score = score
            best_match = service

    # 2. NO MATCH FOUND (Zero Hallucination Policy)
    if not best_match or max_score < 2:
        return schemas.AINavigationResponse(
            intent="unknown_service",
            confidence=0.10,
            needs_follow_up=False,
            questions=[],
            service=None,
            source_status="not_found",
            explanation=f"No verified government service information found matching your query: '{query}'. Please try rephrasing (e.g., 'income certificate', 'caste certificate', 'encumbrance certificate', 'adangal', 'driving license renewal').",
            warnings=["Please ensure you specify valid government service keywords."]
        )

    # 3. INTERACTIVE FOLLOW-UP QUESTION EVALUATION
    # Check if district is required but missing from request & selected_answers
    district_answer = selected_answers.get("district") or district
    purpose_answer = selected_answers.get("purpose")
    category_answer = selected_answers.get("category")

    follow_up_questions = []

    # If district is not provided yet
    if not district_answer:
        follow_up_questions.append(
            schemas.FollowUpQuestion(
                field="district",
                question=f"Which district in {state} are you applying from?",
                options=["NTR / Vijayawada", "Visakhapatnam", "Guntur", "Tirupati", "Anantapur", "Kurnool", "East Godavari"]
            )
        )

    # Specific follow-ups based on service intent
    if best_match.id == "ap-income-certificate" and not purpose_answer:
        follow_up_questions.append(
            schemas.FollowUpQuestion(
                field="purpose",
                question="What is the primary purpose of your Income Certificate application?",
                options=["College Admission / Fee Reimbursement (Jagananna Vidya Deevena)", "Government Welfare Scheme", "Bank Loan / Financial", "Other"]
            )
        )

    if best_match.id == "ap-caste-certificate" and not category_answer:
        follow_up_questions.append(
            schemas.FollowUpQuestion(
                field="category",
                question="Which community reservation category applies to your family?",
                options=["BC (Backward Classes)", "SC (Scheduled Castes)", "ST (Scheduled Tribes)", "OC (Open Category / General)"]
            )
        )

    # If follow-ups are needed, return intermediate JSON with follow_up questions
    if follow_up_questions:
        return schemas.AINavigationResponse(
            intent=best_match.id,
            confidence=min(0.85 + (max_score * 0.03), 0.98),
            needs_follow_up=True,
            questions=follow_up_questions,
            service=None,
            source_status="verified" if not best_match.is_demo_data else "demo_data",
            explanation=f"Found verified service: '{best_match.official_name}'. Please answer the follow-up question to finalize your exact application requirement.",
            warnings=[]
        )

    # 4. FINAL RESOLVED SERVICE RESPONSE
    service_schema = schemas.ServiceOut.from_orm(best_match)
    
    explanation_text = (
        f"Based on your query, the correct official service is **{best_match.official_name}** "
        f"managed by the {best_match.department}. "
        f"The official fee is ₹{best_match.official_fee:.0f} with an estimated processing time of {best_match.processing_time}. "
        f"Applications are submitted through the official portal: {best_match.official_url} or your local Village Secretariat (Grama Sachivalayam)."
    )

    return schemas.AINavigationResponse(
        intent=best_match.id,
        confidence=min(0.90 + (max_score * 0.02), 0.99),
        needs_follow_up=False,
        questions=[],
        service=service_schema,
        eligibility=best_match.eligibility_criteria,
        documents=best_match.required_documents,
        official_fee=best_match.official_fee,
        processing_time=best_match.processing_time,
        official_source=best_match.official_url,
        source_last_verified=best_match.source_last_verified,
        source_status="verified" if not best_match.is_demo_data else "demo_data",
        explanation=explanation_text,
        warnings=["Ensure all uploaded scanned documents are clear and legible to prevent Tahsildar office rejection."]
    )
