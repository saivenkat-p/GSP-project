from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import models
import schemas
from rag_tool_registry import (
    search_verified_services,
    search_verified_schemes,
    search_verified_scholarships,
    search_verified_updates,
    get_verified_sub_service,
    get_verified_information_record
)
from grounding_validator import validate_and_reconcile_grounding
from llm_provider import get_llm_provider

SESSION_CONTEXT_STORE: Dict[str, Dict[str, Any]] = {}

def extract_user_goal(query: str) -> Dict[str, Any]:
    """Helper for extracting citizen situation and goal via LLM planning."""
    llm = get_llm_provider()
    return llm.classify_and_plan(query=query, conversation_history=[])

def resolve_citizen_query(
    session_id: str,
    query: str,
    state_id: str = "AP",
    district_id: str = "AP-NTR",
    mandal_name: str = "Vijayawada Urban",
    selected_answers: Optional[Dict[str, str]] = None,
    db: Optional[Session] = None
) -> schemas.AINavigationResponse:
    """
    Universal GSP AI Assistant Orchestrator.
    Combines LLM Natural Language Understanding + GSP Database RAG Tools + Anti-Hallucination Grounding Check.
    """
    if session_id not in SESSION_CONTEXT_STORE:
        SESSION_CONTEXT_STORE[session_id] = {
            "history": [],
            "last_topic": None,
            "last_evidence": [],
            "last_sub_service": None,
            "last_info_record": None
        }
    
    session_data = SESSION_CONTEXT_STORE[session_id]
    history = session_data["history"]
    q_lower = query.lower().strip()

    # Handle Database Count / Metadata Inquiries dynamically
    if db is not None:
        if any(phrase in q_lower for phrase in ["how many services", "total services", "count of services", "service count"]):
            count = db.query(models.SubService).count()
            return schemas.AINavigationResponse(
                mode="GOVERNMENT_GROUNDED",
                source_status="VERIFIED",
                sources=[],
                intent="SERVICE_COUNT",
                confidence=1.0,
                confidence_status="VERIFIED",
                explanation=f"We currently have {count} verified statutory citizen services and sub-services active in the GSP database.",
                needs_follow_up=False,
                source_last_verified="2026-08-21"
            )
        if any(phrase in q_lower for phrase in ["how many schemes", "total schemes", "count of schemes", "how many government schemes", "how many government schemes do you have"]):
            count = db.query(models.InformationRecord).filter(
                models.InformationRecord.verification_status == "VERIFIED",
                models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT"])
            ).count()
            return schemas.AINavigationResponse(
                mode="GOVERNMENT_GROUNDED",
                source_status="VERIFIED",
                sources=[],
                intent="SCHEME_COUNT",
                confidence=1.0,
                confidence_status="VERIFIED",
                explanation=f"We currently track {count} verified government welfare schemes in the GSP database.",
                needs_follow_up=False,
                source_last_verified="2026-08-21"
            )
        if any(phrase in q_lower for phrase in ["what services do you offer", "what services you offer", "what services do you provide", "list all services", "show me all services", "available services"]):
            cats = [c[0] for c in db.query(models.Service.category).distinct().all() if c[0]]
            return schemas.AINavigationResponse(
                mode="GOVERNMENT_GROUNDED",
                source_status="VERIFIED",
                sources=[],
                intent="SERVICE_LIST",
                confidence=1.0,
                confidence_status="VERIFIED",
                explanation="We provide citizen guidance across verified government categories: " + ", ".join(cats) + ".",
                needs_follow_up=False,
                source_last_verified="2026-08-21"
            )

    # Check context-free fee or deadline inquiries when no previous evidence exists
    if not session_data.get("last_evidence") and any(phrase in q_lower for phrase in ["what is the deadline", "application deadline", "how much is the fee", "what is the fee", "how much does it cost"]):
        return schemas.AINavigationResponse(
            mode="GOVERNMENT_GROUNDED",
            source_status="VERIFIED",
            sources=[],
            intent="CONTEXT_FREE_INQUIRY",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation="Which specific government service or scheme would you like to check the fee or deadline for?",
            needs_follow_up=True,
            questions=[schemas.FollowUpQuestion(
                field="target_service",
                question="Which specific government service or scheme would you like to check?",
                options=["Driving Licence Renewal", "Aadhaar Services", "Scholarships", "Certificates"]
            )],
            source_last_verified="2026-08-21"
        )

    # 1. LLM Understands & Plans
    llm = get_llm_provider()
    plan = llm.classify_and_plan(query=query, conversation_history=history, context=session_data)

    mode = plan.get("mode", "GOVERNMENT_GROUNDED")
    intent = plan.get("intent", "CITIZEN_INQUIRY")
    search_query = plan.get("search_query") or query

    # 2. Handle Non-Government Conversational or General AI Turns
    if mode in ["CONVERSATIONAL", "GENERAL_AI"]:
        explanation = llm.generate_response(
            query=query,
            mode=mode,
            conversation_history=history,
            evidence=[],
            intent=intent
        )
        history.append({"sender": "user", "text": query})
        history.append({"sender": "bot", "text": explanation})

        is_broad = (intent == "BROAD_SCHEME_DISCOVERY")
        return schemas.AINavigationResponse(
            mode=mode,
            source_status=None,
            sources=[],
            intent=intent,
            confidence=0.0 if mode == "GENERAL_AI" else 1.0,
            confidence_status="NOT_FOUND" if mode == "GENERAL_AI" else "VERIFIED",
            explanation=explanation,
            needs_follow_up=is_broad,
            questions=["Which category of schemes are you looking for? (e.g. Higher Education Scholarships, Agriculture & Farmer Support, Healthcare)"] if is_broad else [],
            resolved_sub_service=None,
            resolved_information_record=None,
            documents=[],
            eligibility=[],
            official_fee=0.0,
            source_last_verified="2026-08-21",
            warnings=[]
        )

    # 3. Government Knowledge Inquiry -> RAG Retrieval from GSP Database (or Contextual Evidence Reuse)
    evidence_items: List[Dict[str, Any]] = []
    resolved_sub_service_obj: Optional[models.SubService] = None
    resolved_info_record_obj: Optional[models.InformationRecord] = None
    historical_superseded_notice: Optional[Dict[str, Any]] = None

    if intent.startswith("CONTEXT_") and session_data.get("last_evidence"):
        # Reuse evidence from immediate prior turn for contextual follow-up
        evidence_items = session_data["last_evidence"]
        if session_data.get("last_sub_service") and db is not None:
            resolved_sub_service_obj = db.query(models.SubService).filter(models.SubService.id == session_data["last_sub_service"]).first()
        if session_data.get("last_info_record") and db is not None:
            resolved_info_record_obj = db.query(models.InformationRecord).filter(models.InformationRecord.id == session_data["last_info_record"]).first()
    elif db is not None:
        # Determine whether this is primarily a statutory service vs a scheme/scholarship
        is_statutory_action = intent in [
            "AADHAAR_LOST", "AADHAAR_ENROLMENT", "AADHAAR_DOWNLOAD", "AADHAAR_UPDATE",
            "DL_RENEWAL", "VOTER_LOST", "PAN_NEW", "PAN_CORRECTION", "RATION_CARD_SERVICE",
            "BIRTH_CERT_CORRECTION", "CASTE_CERT_SERVICE", "INCOME_CERT_SERVICE", "LAND_RECORDS_SERVICE"
        ] or any(w in q_lower for w in ["poyindi", "poyindhi", "lost", "missing", "kanapadakunda", "renew", "license", "licence", "download", "enrolment", "appply", "form 49a", "form 8", "form 9", "adangal", "rice card"])

        is_scholarship = "SCHOLARSHIP" in intent or any(
            w in q_lower for w in ["scholarship", "scholership", "student", "degree", "b.tech", "engineering", "college", "fee reimbursement", "abbai", "pillodu"]
        )

        srv_evidence = search_verified_services(db=db, query=search_query, state_id=state_id, limit=3)
        scheme_evidence = search_verified_schemes(db=db, query=search_query, state_id=state_id, limit=3)

        if intent == "SCHEME_UPDATES":
            updates_evidence = search_verified_updates(db=db, state_id=state_id, limit=3)
            evidence_items.extend(updates_evidence)
            evidence_items.extend(scheme_evidence)
        elif is_scholarship:
            sch_evidence = search_verified_scholarships(db=db, query=search_query, state_id=state_id, limit=3)
            evidence_items.extend(sch_evidence)
            evidence_items.extend(scheme_evidence)
            evidence_items.extend(srv_evidence)
        elif is_statutory_action:
            evidence_items.extend(srv_evidence)
            evidence_items.extend(scheme_evidence)
        else:
            evidence_items.extend(scheme_evidence)
            evidence_items.extend(srv_evidence)

        # Deduplicate evidence by ID
        unique_evidence = {}
        for ev in evidence_items:
            if ev["id"] not in unique_evidence:
                unique_evidence[ev["id"]] = ev
        evidence_items = list(unique_evidence.values())

    # Find corresponding DB model instance for schema serialization if matched
    if evidence_items and db is not None:
        primary_evidence = evidence_items[0]
        if "predecessor_notice" in primary_evidence:
            historical_superseded_notice = primary_evidence["predecessor_notice"]

        if primary_evidence.get("type") == "STATUTORY_SERVICE":
            resolved_sub_service_obj = db.query(models.SubService).filter(models.SubService.id == primary_evidence["id"]).first()
        elif primary_evidence.get("type") == "GOVERNMENT_INFORMATION":
            resolved_info_record_obj = db.query(models.InformationRecord).filter(models.InformationRecord.id == primary_evidence["id"]).first()

        # Check if secondary evidence has the other model type
        for ev in evidence_items[1:]:
            if not resolved_sub_service_obj and ev.get("type") == "STATUTORY_SERVICE" and intent != "SCHEME_UPDATES":
                resolved_sub_service_obj = db.query(models.SubService).filter(models.SubService.id == ev["id"]).first()
            if not resolved_info_record_obj and ev.get("type") == "GOVERNMENT_INFORMATION":
                resolved_info_record_obj = db.query(models.InformationRecord).filter(models.InformationRecord.id == ev["id"]).first()
            if not historical_superseded_notice and "predecessor_notice" in ev:
                historical_superseded_notice = ev["predecessor_notice"]

        if intent == "SCHEME_UPDATES":
            resolved_sub_service_obj = None

    # 4. LLM Synthesizes Natural Grounded Answer
    raw_explanation = llm.generate_response(
        query=query,
        mode="GOVERNMENT_GROUNDED",
        conversation_history=history,
        evidence=evidence_items,
        context=session_data,
        intent=intent
    )

    # 5. Anti-Hallucination Grounding Validator Check
    validation_result = validate_and_reconcile_grounding(
        generated_text=raw_explanation,
        evidence=evidence_items,
        mode="GOVERNMENT_GROUNDED"
    )

    final_explanation = validation_result["validated_text"]
    verified_sources = validation_result["verified_sources"]
    warnings = validation_result["warnings"]
    source_status = "VERIFIED" if evidence_items else "NOT_FOUND"

    # 6. Build Structured Schema Metadata
    sub_service_out = None
    if resolved_sub_service_obj:
        sub_service_out = schemas.SubServiceOut.model_validate(resolved_sub_service_obj)

    info_record_out = None
    if resolved_info_record_obj:
        info_record_out = schemas.InformationRecordOut.model_validate(resolved_info_record_obj)

    primary_doc_list = []
    primary_eligibility = []
    official_fee = 0.0
    if evidence_items:
        primary_doc_list = evidence_items[0].get("documents", [])
        primary_eligibility = evidence_items[0].get("eligibility", [])
        official_fee = float(evidence_items[0].get("official_fee", 0.0))

    # Update conversation history & session store
    history.append({"sender": "user", "text": query})
    history.append({"sender": "bot", "text": final_explanation})
    session_data["last_topic"] = intent
    session_data["last_evidence"] = evidence_items
    session_data["last_sub_service"] = resolved_sub_service_obj.id if resolved_sub_service_obj else None
    session_data["last_info_record"] = resolved_info_record_obj.id if resolved_info_record_obj else None

    is_broad = (intent == "BROAD_SCHEME_DISCOVERY")
    questions_list = []
    if is_broad:
        questions_list.append(schemas.FollowUpQuestion(
            field="scheme_category",
            question="Which category of schemes are you looking for?",
            options=["Higher Education Scholarships", "Agriculture & Farmer Support", "Healthcare"]
        ))
        resolved_sub_service_obj = None
        resolved_info_record_obj = None
        sub_service_out = None
        info_record_out = None

    return schemas.AINavigationResponse(
        mode="GOVERNMENT_GROUNDED",
        source_status=source_status,
        sources=verified_sources,
        service=sub_service_out,
        intent=intent,
        confidence=1.0 if evidence_items else 0.0,
        confidence_status="VERIFIED" if evidence_items else "NOT_FOUND",
        explanation=final_explanation,
        needs_follow_up=is_broad,
        questions=questions_list,
        resolved_sub_service=sub_service_out,
        resolved_information_record=info_record_out,
        historical_superseded_notice=historical_superseded_notice,
        documents=primary_doc_list,
        eligibility=primary_eligibility,
        official_fee=official_fee,
        source_last_verified="2026-08-21",
        warnings=warnings
    )
