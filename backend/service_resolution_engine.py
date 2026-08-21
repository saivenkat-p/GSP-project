from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
import re
import models
import schemas

SESSION_CONTEXT_STORE: Dict[str, Dict[str, Any]] = {}

# Configurable Ranking Weights
WEIGHT_EXACT_NAME = 100
WEIGHT_SUB_SERVICE_NAME = 85
WEIGHT_HISTORICAL_MATCH = 90
WEIGHT_ALIAS_MATCH = 75
WEIGHT_ACTION_TYPE = 60
WEIGHT_KEYWORD_MATCH = 40
WEIGHT_CATEGORY_DEPT = 20

# Relevance Threshold: Candidates below this score will NOT be returned to prevent random retrieval
MIN_RELEVANCE_SCORE_THRESHOLD = 35.0

def normalize_text(text: str) -> str:
    """Removes punctuation and normalizes whitespace for clean intent detection."""
    t = text.lower().strip()
    # Remove common conversational punctuation
    t = re.sub(r'[?!.,;:\'\"()\-]', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def extract_user_goal(query_clean: str, raw_query: str = "") -> str:
    """
    Step 1 (Universal Intent & Action Understanding Dimension 2):
    Extracts the citizen's requested goal/action across ANY government service.
    Differentiates active goal from background context.
    """
    # 1. GREETING & CASUAL INTENTS
    greeting_patterns = [
        r'^(hi|hello|hey|heya|hlo|namaste|vanakkam|pranam|good\s*(morning|afternoon|evening|day)|greetings)(\s+there|\s+bot|\s+assistant|\s+gsp)?$',
        r'^(hi|hello|hey)\b'
    ]
    for pat in greeting_patterns:
        if re.match(pat, query_clean):
            words = query_clean.split()
            if len(words) <= 3 and any(w in ['hi', 'hello', 'hey', 'namaste', 'greetings', 'morning', 'afternoon', 'evening'] for w in words):
                return "GREETING"

    courtesy_words = ['thanks', 'thank you', 'thank u', 'thx', 'okay', 'ok', 'got it', 'sure', 'bye', 'goodbye', 'see you', 'great thanks', 'perfect thanks']
    if query_clean in courtesy_words or re.match(r'^(thanks|thank you|ok|okay|bye|goodbye)(\s+(a lot|so much|gsp|assistant))?$', query_clean):
        return "COURTESY"

    if re.search(r'\b(what is gsp|who are you|how does gsp work|about gsp|tell me about gsp|what can you do)\b', query_clean):
        return "GENERAL_GSP_INFO"

    # 2. INVENTORY & STATISTICAL INQUIRIES
    if re.search(r'\b(how many|count of|number of|total)\b.*\b(services?|categories?)\b', query_clean) or query_clean in ["how many services you have", "how many services", "total services"]:
        return "SERVICE_COUNT"
    if re.search(r'\b(how many|count of|number of|total)\b.*\b(schemes?|benefits?|welfare)\b', query_clean) or query_clean in ["how many schemes", "how many schemes you have"]:
        return "SCHEME_COUNT"
    if re.search(r'\b(what services|list services|available services|show services|what do you provide|what services do you have|what services you have)\b', query_clean) or query_clean in ["what services do you provide", "what services you have", "what services"]:
        return "SERVICE_LIST"

    # 3. BROAD AMBIGUOUS DISCOVERY
    if query_clean in ["scholarship", "scholarships", "all scholarships", "scholarship list"]:
        return "BROAD_SCHOLARSHIP_DISCOVERY"
    if query_clean in ["government schemes", "schemes", "government scheme", "all schemes", "welfare schemes", "scheme"]:
        return "BROAD_SCHEME_DISCOVERY"
    if query_clean in ["services", "all services", "government services", "service list"]:
        return "SERVICE_LIST"

    # 4. SCHEME & POLICY UPDATES INTENT
    if re.search(r'\b(new scheme updates?|new schemes?|recent schemes?|latest schemes?|latest benefits?|new government schemes?|schemes? recently launched|government updates?|recent updates?|rule changes?|notification updates?)\b', query_clean):
        return "LATEST_UPDATE"

    # 5. GOAL EXTRACTION (With Context vs. Goal Separation)
    # E.g. "I updated my mobile number in Aadhaar. How do I download the updated Aadhaar?"
    # The active question is "how do I download", so goal = DOWNLOAD.
    has_download_trigger = bool(re.search(r'\b(download|get copy|print|reprint|soft copy|pdf copy|digital copy|get another copy|how do i download|download my|get the new copy|download the updated)\b', query_clean))
    if has_download_trigger:
        return "DOWNLOAD"

    # E.g. "my licence is going to expire, what should I do?" or "expired last month, how can I get a new one?"
    has_renew_trigger = bool(re.search(r'\b(renew|renewal|renewing|extend validity|expired|going to expire|licence is expiring)\b', query_clean))
    if has_renew_trigger and not re.search(r'\b(birth|caste|income)\b', query_clean):
        return "RENEW"

    # E.g. "I lost my voter card", "lost my driving licence", "replacement card"
    has_replace_trigger = bool(re.search(r'\b(lost|misplaced|damaged|stolen|replacement|replace|duplicate card)\b', query_clean))
    if has_replace_trigger:
        return "REPLACE"

    # E.g. "my father's name is wrong on my birth certificate", "spelling mistake", "correction"
    has_correct_trigger = bool(re.search(r'\b(wrong|correction|correct|spelling mistake|name change|father name|mother name|dob correction|mistake in)\b', query_clean))
    if has_correct_trigger:
        return "CORRECT"

    # E.g. "how can I check my application status?", "track status"
    has_status_trigger = bool(re.search(r'\b(status|track|track application|application status|check status|where is my application|progress)\b', query_clean))
    if has_status_trigger:
        return "CHECK_STATUS"

    # E.g. "am I eligible for PM-KISAN?", "can I get this scholarship?", "who is eligible"
    has_elig_trigger = bool(re.search(r'\b(eligib|eligible|who is eligible|can i apply|am i eligible|criteria|qualif|who can apply|can i get this)\b', query_clean))
    if has_elig_trigger:
        return "CHECK_ELIGIBILITY"

    # E.g. "what documents do I need for this?", "required documents for income certificate"
    has_doc_trigger = bool(re.search(r'\b(documents?|proofs?|certificates? needed|requirements?|papers? needed|what documents|mandatory documents)\b', query_clean))
    if has_doc_trigger:
        return "DOCUMENT_REQUIREMENTS"

    # E.g. "how much does this service cost?", "fee for dl renewal"
    has_fee_trigger = bool(re.search(r'\b(fee|fees|cost|charges?|price|how much|statutory fee|pricing|payment)\b', query_clean))
    if has_fee_trigger:
        return "FEES"

    # E.g. "how long does this take?", "processing time", "delivery days"
    has_time_trigger = bool(re.search(r'\b(how long|processing time|delivery time|how many days|time taken|duration|when will i receive)\b', query_clean))
    if has_time_trigger:
        return "PROCESSING_TIME"

    # E.g. "what is the deadline?", "last date to apply", "when does it end"
    has_deadline_trigger = bool(re.search(r'\b(deadline|last date|due date|expiry date|when is the last date|when does it end|closing date)\b', query_clean))
    if has_deadline_trigger:
        return "DEADLINE"

    # E.g. "what are the benefits?", "how much money do I get?"
    has_benefit_trigger = bool(re.search(r'\b(benefits?|financial assistance|subsidy amount|how much money|payout|grant amount)\b', query_clean))
    if has_benefit_trigger:
        return "BENEFITS"

    # E.g. "where is the official website?", "official portal link"
    has_website_trigger = bool(re.search(r'\b(official website|official portal|portal url|website link|official link|where to apply online)\b', query_clean))
    if has_website_trigger:
        return "OFFICIAL_WEBSITE"

    # E.g. "how do I apply for a caste certificate?", "register for pm kisan"
    has_apply_trigger = bool(re.search(r'\b(how to apply|how can i apply|steps to apply|procedure|where to apply|process of applying|apply for|register for|new application)\b', query_clean))
    if has_apply_trigger:
        return "APPLY"

    # Scholarship specific search
    if re.search(r'\b(scholarships?|grants?|fellowships?|fee reimbursement|student aid)\b', query_clean):
        return "SCHOLARSHIP_SEARCH"

    # Default fallback to GENERAL INFORMATION / HOW TO
    return "INFORMATION"

def classify_query_intent(query_clean: str) -> str:
    """Maps universal user goal to backwards-compatible functional intent for API callers."""
    goal = extract_user_goal(query_clean)
    mapping = {
        "GREETING": "GREETING",
        "COURTESY": "COURTESY",
        "GENERAL_GSP_INFO": "GENERAL_GSP_INFO",
        "SERVICE_COUNT": "SERVICE_COUNT",
        "SCHEME_COUNT": "SCHEME_COUNT",
        "SERVICE_LIST": "SERVICE_LIST",
        "BROAD_SCHOLARSHIP_DISCOVERY": "BROAD_SCHOLARSHIP_DISCOVERY",
        "BROAD_SCHEME_DISCOVERY": "BROAD_SCHEME_DISCOVERY",
        "LATEST_UPDATE": "SCHEME_UPDATES",
        "CHECK_ELIGIBILITY": "ELIGIBILITY",
        "DOCUMENT_REQUIREMENTS": "DOCUMENT_REQUIREMENTS",
        "APPLY": "APPLICATION_PROCEDURE",
        "FEES": "FEE_INQUIRY",
        "DEADLINE": "DEADLINE_INQUIRY",
        "CHECK_STATUS": "STATUS_CHECK",
        "CORRECT": "CERTIFICATE_CORRECTION",
        "RENEW": "LICENCE_RENEWAL",
        "SCHOLARSHIP_SEARCH": "SCHOLARSHIP_SEARCH"
    }
    return mapping.get(goal, "GOVERNMENT_SERVICE_SEARCH")

def format_scheme_grounded_answer(rec: models.InformationRecord, historical_notice: Optional[Dict[str, Any]] = None, custom_heading: Optional[str] = None) -> str:
    """Generates a citizen-friendly, structured, grounded response for an InformationRecord."""
    lines = []
    if historical_notice:
        lines.append(f"ℹ️ **Note**: {historical_notice['explanation']}\n")

    title_display = custom_heading or rec.title
    lines.append(f"🏛️ **{title_display}**")
    lines.append(f"• **Department/Source**: {rec.department} ({rec.organization})")
    lines.append(f"• **Overview**: {rec.description}")

    if rec.benefit_amount_str:
        lines.append(f"• **Verified Benefit**: {rec.benefit_amount_str}")

    if rec.application_deadline:
        lines.append(f"• **Application Deadline**: {rec.application_deadline}")

    if rec.eligibility_criteria:
        elig_items = rec.eligibility_criteria if isinstance(rec.eligibility_criteria, list) else [str(rec.eligibility_criteria)]
        lines.append(f"• **Key Eligibility**: {'; '.join(elig_items[:2])}")

    if rec.required_documents:
        docs_summary = []
        for d in rec.required_documents[:3]:
            if isinstance(d, dict):
                docs_summary.append(d.get("name", ""))
            else:
                docs_summary.append(str(d))
        if docs_summary:
            lines.append(f"• **Mandatory Documents**: {', '.join([d for d in docs_summary if d])}")

    lines.append(f"• **Official Portal**: {rec.source_url}")
    lines.append(f"\n🟢 **Official Source — {rec.verification_status}** (Last Verified: {rec.last_verified})")
    return "\n".join(lines)

def format_service_grounded_answer(sub: models.SubService, parent: Optional[models.Service] = None) -> str:
    """Generates a citizen-friendly structured response for a statutory SubService."""
    lines = []
    lines.append(f"📋 **{sub.sub_service_name}**")
    if parent:
        lines.append(f"• **Authority / Department**: {parent.department} ({parent.official_name})")
    lines.append(f"• **Procedure**: {sub.description}")
    lines.append(f"• **Official Statutory Fee**: ₹{sub.official_fee:.2f}")
    lines.append(f"• **Expected Processing Time**: {sub.processing_time}")

    if sub.required_documents:
        docs = []
        for d in sub.required_documents[:3]:
            if isinstance(d, dict):
                docs.append(d.get("name", ""))
            else:
                docs.append(str(d))
        if docs:
            lines.append(f"• **Required Documents**: {', '.join([d for d in docs if d])}")

    if sub.official_portal_url:
        lines.append(f"• **Official Portal**: {sub.official_portal_url}")

    lines.append(f"\n🟢 **Official Source — {sub.confidence_status}** (Source-Backed Procedure)")
    return "\n".join(lines)

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
    GSP Grounded AI Assistant (Universal Service Intent & Action Understanding Pipeline).
    Features:
    1. 2-Dimensional Architecture: Dimension 1 (Service/Topic) + Dimension 2 (User Goal/Action)
    2. Context vs. Goal Separation (e.g. 'I updated mobile number in Aadhaar. How do I download?' -> Goal: DOWNLOAD)
    3. Multi-turn Session Memory & Topic Switching
    4. Goal-Tailored Grounded Answer Generation (Eligibility, Docs, Fees, SLA, Website, Steps)
    5. Zero Hallucination of External Government Actions
    """
    if selected_answers is None:
        selected_answers = {}

    if session_id not in SESSION_CONTEXT_STORE:
        SESSION_CONTEXT_STORE[session_id] = {
            "accumulated_answers": {},
            "last_intent": None,
            "last_sub_service_id": None,
            "last_service_id": None,
            "last_information_record_id": None,
            "last_topic_name": None,
            "history": []
        }
    
    session_ctx = SESSION_CONTEXT_STORE[session_id]
    session_ctx["accumulated_answers"].update(selected_answers)
    session_ctx["history"].append(query)

    query_clean = normalize_text(query)
    user_goal = extract_user_goal(query_clean, query)
    intent = classify_query_intent(query_clean)
    session_ctx["last_intent"] = intent

    # =========================================================================
    # STEP 1: CASUAL / ZERO-RETRIEVAL RESPONSES
    # =========================================================================
    if user_goal == "GREETING":
        return schemas.AINavigationResponse(
            intent="GREETING",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=(
                "Hello! I'm your GSP Grounded AI Assistant. I can help you find verified government schemes, "
                "scholarships, certificates, eligibility criteria, document requirements, and application procedures.\n\n"
                "What government service or scheme can I help you with today?"
            ),
            needs_follow_up=False,
            candidate_suggestions=[
                schemas.CandidateSuggestion(id="sug-1", name="Post Matric Scholarships", category="Education"),
                schemas.CandidateSuggestion(id="sug-2", name="Annadata Sukhibhava / PM-KISAN", category="Agriculture"),
                schemas.CandidateSuggestion(id="sug-3", name="Birth Certificate Name Correction", category="Certificates"),
                schemas.CandidateSuggestion(id="sug-4", name="Driving Licence Renewal", category="Transport")
            ],
            warnings=[]
        )

    if user_goal == "COURTESY":
        return schemas.AINavigationResponse(
            intent="COURTESY",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation="You're welcome! Let me know if you need help with any other verified government service, welfare scheme, or scholarship.",
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "GENERAL_GSP_INFO":
        return schemas.AINavigationResponse(
            intent="GENERAL_GSP_INFO",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=(
                "GSP (Government Service Partner) is an independent citizen guidance and assistance platform. "
                "We provide source-verified procedural steps, statutory fee breakdowns, document requirements, "
                "and verified operator assistance for government schemes and citizen certificates. "
                "All statutory government fees are strictly separated from assistance services."
            ),
            needs_follow_up=False,
            warnings=[]
        )

    # =========================================================================
    # STEP 2: BROAD DISCOVERY CLARIFICATIONS
    # =========================================================================
    if user_goal == "BROAD_SCHOLARSHIP_DISCOVERY":
        return schemas.AINavigationResponse(
            intent="BROAD_SCHOLARSHIP_DISCOVERY",
            confidence=0.9,
            confidence_status="VERIFIED",
            explanation=(
                "Sure! We track several verified scholarships. Are you looking for:\n"
                "1. **Post Matric Scholarships (Higher Education)** — Fee reimbursement for degree & engineering students.\n"
                "2. **Central Sector Scholarship (NSP)** — Class 12 top percentile merit scholarship.\n"
                "3. **LIC Golden Jubilee Scholarship** — For Class 10/12 passed students.\n"
                "4. **TCS Ignite & Corporate Grants** — Engineering & STEM scholarships.\n\n"
                "Which category or course are you applying for?"
            ),
            needs_follow_up=True,
            warnings=[]
        )

    if user_goal == "BROAD_SCHEME_DISCOVERY":
        return schemas.AINavigationResponse(
            intent="BROAD_SCHEME_DISCOVERY",
            confidence=0.9,
            confidence_status="VERIFIED",
            explanation=(
                "GSP tracks verified government welfare schemes across major departments:\n"
                "• **Agriculture**: Annadata Sukhibhava / PM-KISAN Farmer Support\n"
                "• **Health**: Dr. NTR Vaidya Seva (Cashless Hospitalization)\n"
                "• **Housing**: PMAY - Housing for All (Urban & Gramin)\n"
                "• **Education**: Post Matric Scholarships & Tuition Fee Reimbursement\n\n"
                "Which sector or benefit would you like details on?"
            ),
            needs_follow_up=True,
            warnings=[]
        )

    if user_goal == "SERVICE_LIST":
        categories = [c[0] for c in db.query(models.Service.category).distinct().all() if c[0]]
        cat_str = ", ".join(sorted(categories))
        return schemas.AINavigationResponse(
            intent="SERVICE_LIST",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=f"GSP provides citizen assistance across verified government categories including: {cat_str}. You can search for specific services like 'Driving licence renewal', 'Aadhaar update', or 'Income certificate'.",
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "SERVICE_COUNT":
        total_services = db.query(models.Service).count()
        total_sub_services = db.query(models.SubService).count()
        total_categories = db.query(models.Service.category).distinct().count()
        explanation = (
            f"GSP currently tracks {total_categories} statutory service categories, "
            f"{total_services} master government departments, and {total_sub_services} verified citizen sub-services "
            f"for your selected region."
        )
        return schemas.AINavigationResponse(
            intent="SERVICE_COUNT",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "SCHEME_COUNT":
        total_schemes = db.query(models.InformationRecord).filter(
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT", "SCHOLARSHIP"])
        ).count()
        explanation = f"GSP currently tracks {total_schemes} active and verified welfare schemes and scholarships."
        return schemas.AINavigationResponse(
            intent="SCHEME_COUNT",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    # =========================================================================
    # STEP 3: LATEST UPDATES & NOTIFICATIONS
    # =========================================================================
    if user_goal == "LATEST_UPDATE":
        recent_records = db.query(models.InformationRecord).filter(
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT", "SERVICE_UPDATE", "RULE_CHANGE", "SCHOLARSHIP"])
        ).order_by(desc(models.InformationRecord.published_at), desc(models.InformationRecord.banner_priority)).limit(4).all()

        if recent_records:
            lines = ["📢 **Latest Verified Government Scheme Updates & Citizen Notices**:\n"]
            for idx, r in enumerate(recent_records, 1):
                type_label = "Scheme" if "SCHEME" in r.information_type else ("Scholarship" if "SCHOLARSHIP" in r.information_type else "Rule Update")
                benefit_str = f" • Benefit: {r.benefit_amount_str}" if r.benefit_amount_str else ""
                deadline_str = f" • Deadline: {r.application_deadline}" if r.application_deadline else ""
                lines.append(f"{idx}. **{r.title}** ({type_label})\n   {r.description}{benefit_str}{deadline_str}\n   *Source: {r.organization}*")

            lines.append("\n🟢 **Official Sources — VERIFIED**")
            session_ctx["last_information_record_id"] = recent_records[0].id
            session_ctx["last_topic_name"] = recent_records[0].title
            rec_out = schemas.InformationRecordOut.model_validate(recent_records[0])
            return schemas.AINavigationResponse(
                intent="SCHEME_UPDATES",
                confidence=1.0,
                confidence_status="VERIFIED",
                explanation="\n\n".join(lines),
                needs_follow_up=False,
                resolved_information_record=rec_out,
                warnings=[]
            )

    # =========================================================================
    # STEP 4: TOPIC RESOLUTION & CONTEXTUAL MEMORY (Universal Engine)
    # =========================================================================
    sub_services: List[models.SubService] = db.query(models.SubService).all()
    info_records: List[models.InformationRecord] = db.query(models.InformationRecord).filter(
        models.InformationRecord.status == "ACTIVE"
    ).all()

    # Pre-build parent service lookup
    all_services: List[models.Service] = db.query(models.Service).all()
    service_by_id = {s.id: s for s in all_services}

    # Action Type Alignment Map for Goals
    GOAL_ACTION_BOOST = {
        "DOWNLOAD": ["Download", "Duplicate", "Reprint"],
        "RENEW": ["Renewal", "Renew"],
        "REPLACE": ["Duplicate", "Replacement", "Claim"],
        "CORRECT": ["Correction", "Update", "Change"],
        "UPDATE": ["Update", "Correction", "Change"],
        "APPLY": ["New Application", "Application", "Registration", "Claim"],
        "REGISTER": ["New Application", "Application", "Registration"],
    }

    # Helper: calculate topic & action relevance
    scored_service_candidates: List[Tuple[float, Optional[models.Service], models.SubService]] = []
    scored_info_candidates: List[Tuple[float, models.InformationRecord, bool, Optional[str]]] = []

    for sub in sub_services:
        parent = service_by_id.get(sub.service_id)
        # Apply state filtering
        if parent and parent.state_scope not in ["NAT", state_id, "ALL"]:
            continue

        score = 0.0
        sub_name_clean = normalize_text(sub.sub_service_name)
        parent_name_clean = normalize_text(parent.official_name) if parent else ""

        # Exact / Substring service match
        if sub_name_clean in query_clean:
            score += WEIGHT_SUB_SERVICE_NAME
        elif parent and parent_name_clean in query_clean:
            score += WEIGHT_EXACT_NAME
        elif parent and any(w in query_clean.split() for w in parent_name_clean.split() if len(w) > 3):
            score += 30.0

        # Alias Match
        for alias in (sub.aliases or []):
            alias_clean = normalize_text(alias)
            if alias_clean == query_clean:
                score += WEIGHT_EXACT_NAME + 15
            elif alias_clean in query_clean or query_clean in alias_clean:
                score += WEIGHT_ALIAS_MATCH

        if parent:
            for p_alias in (parent.aliases or []):
                p_alias_clean = normalize_text(p_alias)
                if p_alias_clean in query_clean:
                    score += WEIGHT_ALIAS_MATCH

        # Keywords
        for kw in (sub.keywords or []):
            if normalize_text(kw) in query_clean:
                score += WEIGHT_KEYWORD_MATCH

        # Goal Action Alignment
        if user_goal in GOAL_ACTION_BOOST:
            preferred_actions = GOAL_ACTION_BOOST[user_goal]
            if sub.action_type in preferred_actions:
                score += WEIGHT_ACTION_TYPE
            elif sub.action_type not in preferred_actions and score > 20:
                score -= 30.0  # Penalize non-matching action when specific goal requested

        if score > 0:
            scored_service_candidates.append((score, parent, sub))

    # Score InformationRecords
    for rec in info_records:
        rec_title_clean = normalize_text(rec.title)
        score = 0.0
        matched_hist_name = None
        is_superseded = False

        if rec_title_clean in query_clean or query_clean in rec_title_clean:
            score += WEIGHT_EXACT_NAME

        for h_name in (rec.historical_names or []):
            h_clean = normalize_text(h_name)
            if h_clean and (h_clean in query_clean or query_clean in h_clean):
                score += WEIGHT_HISTORICAL_MATCH + 10
                matched_hist_name = h_name
                is_superseded = True

        for alias in (rec.aliases or []):
            a_clean = normalize_text(alias)
            if a_clean == query_clean:
                score += WEIGHT_EXACT_NAME
            elif a_clean in query_clean:
                score += WEIGHT_ALIAS_MATCH

        for kw in (rec.keywords or []):
            if normalize_text(kw) in query_clean:
                score += WEIGHT_KEYWORD_MATCH

        # Scholarship Isolation
        if user_goal == "SCHOLARSHIP_SEARCH" and rec.information_type == "SCHOLARSHIP":
            score += 45.0

        if score > 0:
            scored_info_candidates.append((score, rec, is_superseded, matched_hist_name))

    scored_service_candidates.sort(key=lambda x: x[0], reverse=True)
    scored_info_candidates.sort(key=lambda x: x[0], reverse=True)

    best_service_score = scored_service_candidates[0][0] if scored_service_candidates else 0
    best_info_score = scored_info_candidates[0][0] if scored_info_candidates else 0

    has_direct_topic_match = max(best_service_score, best_info_score) >= MIN_RELEVANCE_SCORE_THRESHOLD
    has_active_context = bool(session_ctx.get("last_information_record_id") or session_ctx.get("last_sub_service_id"))

    # =========================================================================
    # STEP 5: CONTEXTUAL ATTRIBUTE INQUIRY DISPATCH (ELIGIBILITY, DOCS, FEES, SLA, WEBSITE)
    # =========================================================================
    context_attribute_goals = [
        "CHECK_ELIGIBILITY", "DOCUMENT_REQUIREMENTS", "FEES", "PROCESSING_TIME",
        "DEADLINE", "BENEFITS", "OFFICIAL_WEBSITE", "APPLY", "CHECK_STATUS"
    ]

    # If the user asked a contextual attribute question and we have an active context
    if user_goal in context_attribute_goals and (not has_direct_topic_match or len(query_clean.split()) <= 5) and has_active_context:
        # 1. Context bound to InformationRecord
        if session_ctx.get("last_information_record_id"):
            info_rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == session_ctx["last_information_record_id"]).first()
            if info_rec:
                info_out = schemas.InformationRecordOut.model_validate(info_rec)
                if user_goal == "CHECK_ELIGIBILITY":
                    elig_list = info_rec.eligibility_criteria or ["Standard residency and economic eligibility rules apply."]
                    exp = (
                        f"📋 **Eligibility Criteria for {info_rec.title}**:\n" +
                        "\n".join([f"• {e}" for e in elig_list]) +
                        f"\n\n🟢 **Official Source — {info_rec.verification_status}** ({info_rec.organization})"
                    )
                elif user_goal == "DOCUMENT_REQUIREMENTS":
                    docs_lines = []
                    for d in (info_rec.required_documents or []):
                        if isinstance(d, dict):
                            docs_lines.append(f"• **{d.get('name')}**{' (Mandatory)' if d.get('mandatory') else ''}: {d.get('description', '')}")
                        else:
                            docs_lines.append(f"• {d}")
                    exp = (
                        f"📑 **Required Documents for {info_rec.title}**:\n" +
                        ("\n".join(docs_lines) if docs_lines else "• Aadhaar Card & Relevant category/income certificates.") +
                        f"\n\n🟢 **Official Source — {info_rec.verification_status}**"
                    )
                elif user_goal in ["FEES", "COST"]:
                    exp = (
                        f"💰 **Fee Details for {info_rec.title}**:\n"
                        f"• **Official Statutory Fee**: ₹{info_rec.official_statutory_fee:.2f} (Government Fee)\n"
                        f"• **GSP Assistance Fee**: ₹{info_rec.gsp_assistance_fee:.2f} (Optional operator assistance)\n\n"
                        f"🟢 **Official Source — {info_rec.verification_status}**"
                    )
                elif user_goal == "DEADLINE":
                    deadline_val = info_rec.application_deadline or "Active & ongoing without explicit closing deadline"
                    exp = (
                        f"⏰ **Application Deadline for {info_rec.title}**:\n"
                        f"• **Verified Deadline**: {deadline_val}\n\n"
                        f"🟢 **Official Source — {info_rec.verification_status}**"
                    )
                elif user_goal == "OFFICIAL_WEBSITE":
                    exp = (
                        f"🔗 **Official Website & Portal for {info_rec.title}**:\n"
                        f"• **Portal URL**: {info_rec.source_url}\n"
                        f"• **Department / Authority**: {info_rec.department} ({info_rec.organization})\n\n"
                        f"🟢 **Official Source — {info_rec.verification_status}**"
                    )
                elif user_goal == "APPLY":
                    steps = info_rec.diy_steps or ["Step 1: Check eligibility.", "Step 2: Gather mandatory documents.", "Step 3: Submit online at official portal."]
                    exp = (
                        f"📝 **How to Apply for {info_rec.title}**:\n" +
                        "\n".join([f"{s}" for s in steps]) +
                        f"\n• **Official Application Portal**: {info_rec.source_url}" +
                        f"\n\n🟢 **Official Source — {info_rec.verification_status}**"
                    )
                else:
                    exp = f"Details for {info_rec.title}: Please visit official portal {info_rec.source_url}."

                intent_name = "CONTEXT_ELIGIBILITY" if user_goal == "CHECK_ELIGIBILITY" else (
                    "CONTEXT_DOCUMENTS_INQUIRY" if user_goal == "DOCUMENT_REQUIREMENTS" else (
                        "CONTEXT_FEE_INQUIRY" if user_goal == "FEES" else (
                            "CONTEXT_DEADLINE_INQUIRY" if user_goal == "DEADLINE" else f"CONTEXT_{user_goal}"
                        )
                    )
                )

                return schemas.AINavigationResponse(
                    intent=intent_name,
                    confidence=0.98,
                    confidence_status="VERIFIED",
                    explanation=exp,
                    needs_follow_up=False,
                    resolved_information_record=info_out,
                    documents=info_rec.required_documents or [],
                    eligibility=info_rec.eligibility_criteria or [],
                    official_fee=info_rec.official_statutory_fee,
                    warnings=[]
                )

        # 2. Context bound to SubService
        if session_ctx.get("last_sub_service_id"):
            sub_rec = db.query(models.SubService).filter(models.SubService.id == session_ctx["last_sub_service_id"]).first()
            if sub_rec:
                sub_out = schemas.SubServiceOut.model_validate(sub_rec)
                if user_goal == "DOCUMENT_REQUIREMENTS":
                    docs_lines = [f"• **{d.get('name') if isinstance(d, dict) else d}**" for d in (sub_rec.required_documents or [])]
                    exp = f"📑 **Required Documents for {sub_rec.sub_service_name}**:\n" + "\n".join(docs_lines)
                elif user_goal in ["FEES", "COST"]:
                    exp = f"💰 **Statutory Fee for {sub_rec.sub_service_name}** is ₹{sub_rec.official_fee:.2f}. Expected delivery: {sub_rec.processing_time}."
                elif user_goal == "PROCESSING_TIME":
                    exp = f"⏱️ **Processing Time for {sub_rec.sub_service_name}**: {sub_rec.processing_time} under standard government citizen charters."
                elif user_goal == "OFFICIAL_WEBSITE":
                    exp = f"🔗 **Official Portal for {sub_rec.sub_service_name}**: {sub_rec.official_portal_url}"
                elif user_goal == "APPLY":
                    steps = sub_rec.diy_steps or ["Submit application via MeeSeva / Official Department portal."]
                    exp = f"📝 **Procedure for {sub_rec.sub_service_name}**:\n" + "\n".join(steps)
                else:
                    exp = f"Details for {sub_rec.sub_service_name}: Processing time {sub_rec.processing_time}."

                intent_name = "CONTEXT_DOCUMENTS_INQUIRY" if user_goal == "DOCUMENT_REQUIREMENTS" else (
                    "CONTEXT_FEE_INQUIRY" if user_goal in ["FEES", "COST"] else f"CONTEXT_{user_goal}"
                )

                return schemas.AINavigationResponse(
                    intent=intent_name,
                    confidence=0.98,
                    confidence_status="VERIFIED",
                    explanation=exp,
                    needs_follow_up=False,
                    resolved_sub_service=sub_out,
                    documents=sub_rec.required_documents or [],
                    eligibility=sub_rec.eligibility_criteria or [],
                    official_fee=sub_rec.official_fee,
                    warnings=[]
                )

    # Prompt for context if user asked contextual question without context
    if user_goal in context_attribute_goals and not has_direct_topic_match and not has_active_context and len(query_clean.split()) <= 5:
        prompt_map = {
            "CHECK_ELIGIBILITY": "Which government scheme or scholarship would you like eligibility criteria for? (e.g. 'Post Matric Scholarship', 'PM-KISAN').",
            "DOCUMENT_REQUIREMENTS": "Which government certificate or service do you need the document checklist for? (e.g. 'Driving licence renewal', 'Income certificate', 'Aadhaar update').",
            "FEES": "Which service or scheme are you inquiring about the statutory fee for?",
            "PROCESSING_TIME": "Which service or certificate would you like the processing timeline for?",
            "DEADLINE": "Which scheme or scholarship deadline are you asking about?",
            "OFFICIAL_WEBSITE": "Which government department or service portal link are you looking for?",
            "CHECK_STATUS": "Which application or certificate status would you like to track?",
            "APPLY": "Which government scheme or service would you like application instructions for?"
        }
        return schemas.AINavigationResponse(
            intent=f"NEED_CONTEXT_{intent}",
            confidence=0.5,
            confidence_status="VERIFICATION_PENDING",
            explanation=prompt_map.get(user_goal, "Which government service would you like assistance with?"),
            needs_follow_up=True,
            warnings=[]
        )

    # =========================================================================
    # STEP 6: DIRECT RELEVANCE THRESHOLD CHECK
    # =========================================================================
    if not has_direct_topic_match:
        return schemas.AINavigationResponse(
            intent="UNKNOWN",
            confidence=0.0,
            confidence_status="NOT_FOUND",
            explanation=(
                "I couldn't find a verified government record relevant to your request, and couldn't verify official information for this query. "
                "Try asking about a specific scheme, scholarship, certificate, benefit or government service "
                "(e.g. 'Post Matric Scholarships', 'PM-KISAN', 'Driving licence renewal', 'Birth certificate correction', 'Download Aadhaar')."
            ),
            needs_follow_up=False,
            candidate_suggestions=[
                schemas.CandidateSuggestion(id="cat-1", name="Statutory Certificates & Civil Status", category="Identity"),
                schemas.CandidateSuggestion(id="cat-2", name="Transport & Driving Licence", category="Transport"),
                schemas.CandidateSuggestion(id="cat-3", name="Government Welfare Schemes", category="Welfare")
            ],
            warnings=["No registered government record met the minimum relevance threshold for this query."]
        )

    # =========================================================================
    # STEP 7: RESOLVE BEST RECORD & GENERATE GOAL-TAILORED ANSWER
    # =========================================================================
    if best_info_score >= best_service_score:
        _, raw_rec, is_superseded, matched_hist_name = scored_info_candidates[0]
        resolved_rec = raw_rec
        historical_notice = None

        if raw_rec.superseded_by_id:
            successor = db.query(models.InformationRecord).filter(models.InformationRecord.id == raw_rec.superseded_by_id).first()
            if successor:
                resolved_rec = successor
                historical_notice = {
                    "original_query": query,
                    "superseded_title": raw_rec.title,
                    "current_title": successor.title,
                    "explanation": f"You searched for '{raw_rec.title}', which is an earlier or historical version. The current official information is listed under '{successor.title}'."
                }
        elif is_superseded or matched_hist_name:
            historical_notice = {
                "original_query": query,
                "superseded_title": matched_hist_name or raw_rec.previous_title or raw_rec.title,
                "current_title": raw_rec.title,
                "explanation": f"You searched for '{matched_hist_name or raw_rec.previous_title}', which refers to an earlier scheme title. The current official record is listed under '{raw_rec.title}'."
            }

        # Update Session Context
        session_ctx["last_information_record_id"] = resolved_rec.id
        session_ctx["last_topic_name"] = resolved_rec.title
        session_ctx["last_sub_service_id"] = None

        # Tailor explanation to goal
        if user_goal == "CHECK_ELIGIBILITY":
            elig_list = resolved_rec.eligibility_criteria or ["Standard residency and economic eligibility rules apply."]
            grounded_explanation = (
                f"📋 **Eligibility Criteria for {resolved_rec.title}**:\n" +
                "\n".join([f"• {e}" for e in elig_list]) +
                f"\n\n🟢 **Official Source — {resolved_rec.verification_status}** ({resolved_rec.organization})"
            )
        elif user_goal == "DOCUMENT_REQUIREMENTS":
            docs_lines = []
            for d in (resolved_rec.required_documents or []):
                if isinstance(d, dict):
                    docs_lines.append(f"• **{d.get('name')}**{' (Mandatory)' if d.get('mandatory') else ''}: {d.get('description', '')}")
                else:
                    docs_lines.append(f"• {d}")
            grounded_explanation = (
                f"📑 **Required Documents for {resolved_rec.title}**:\n" +
                ("\n".join(docs_lines) if docs_lines else "• Aadhaar Card & Relevant category certificates.") +
                f"\n\n🟢 **Official Source — {resolved_rec.verification_status}**"
            )
        elif user_goal in ["FEES", "COST"]:
            grounded_explanation = (
                f"💰 **Statutory Fee for {resolved_rec.title}**:\n"
                f"• **Government Statutory Fee**: ₹{resolved_rec.official_statutory_fee:.2f}\n"
                f"• **Official Portal**: {resolved_rec.source_url}\n\n"
                f"🟢 **Official Source — {resolved_rec.verification_status}**"
            )
        elif user_goal == "OFFICIAL_WEBSITE":
            grounded_explanation = (
                f"🔗 **Official Website / Portal for {resolved_rec.title}**:\n"
                f"• **Portal URL**: {resolved_rec.source_url}\n"
                f"• **Department**: {resolved_rec.department} ({resolved_rec.organization})\n\n"
                f"🟢 **Official Source — {resolved_rec.verification_status}**"
            )
        else:
            grounded_explanation = format_scheme_grounded_answer(resolved_rec, historical_notice)

        rec_out = schemas.InformationRecordOut.model_validate(resolved_rec)

        return schemas.AINavigationResponse(
            intent=f"RESOLVED_{resolved_rec.information_type}",
            confidence=min(1.0, best_info_score / 100.0),
            confidence_status=resolved_rec.verification_status,
            explanation=grounded_explanation,
            needs_follow_up=False,
            resolved_information_record=rec_out,
            historical_superseded_notice=historical_notice,
            documents=resolved_rec.required_documents or [],
            eligibility=resolved_rec.eligibility_criteria or [],
            official_fee=resolved_rec.official_statutory_fee,
            warnings=[]
        )

    else:
        # SubService Winner
        _, parent_srv, best_sub = scored_service_candidates[0]

        # Update Session Context
        session_ctx["last_service_id"] = parent_srv.id if parent_srv else None
        session_ctx["last_sub_service_id"] = best_sub.id if best_sub else None
        session_ctx["last_topic_name"] = best_sub.sub_service_name
        session_ctx["last_information_record_id"] = None

        # Goal-Tailored Answer Generation for SubService
        if user_goal == "DOWNLOAD":
            grounded_explanation = (
                f"📥 **Download Digital Copy for {best_sub.sub_service_name}**:\n"
                f"• **Official Download Portal**: {best_sub.official_portal_url}\n"
                f"• **Authentication Required**: Mobile OTP on registered mobile / Application Reference Number.\n"
                f"• **Statutory Fee**: ₹{best_sub.official_fee:.2f} (Official digital copy)\n"
                f"• **Processing Time**: {best_sub.processing_time}\n\n"
                f"🟢 **Official Source — {best_sub.confidence_status}** (Source-Backed Procedure)"
            )
        elif user_goal == "DOCUMENT_REQUIREMENTS":
            docs_lines = [f"• **{d.get('name') if isinstance(d, dict) else d}**" for d in (best_sub.required_documents or [])]
            grounded_explanation = (
                f"📑 **Required Documents for {best_sub.sub_service_name}**:\n" +
                ("\n".join(docs_lines) if docs_lines else "• Valid photo identity & address proof.") +
                f"\n\n🟢 **Official Source — {best_sub.confidence_status}**"
            )
        elif user_goal in ["FEES", "COST"]:
            grounded_explanation = (
                f"💰 **Official Statutory Fee for {best_sub.sub_service_name}**:\n"
                f"• **Government Statutory Fee**: ₹{best_sub.official_fee:.2f}\n"
                f"• **Expected Delivery**: {best_sub.processing_time}\n"
                f"• **Official Portal**: {best_sub.official_portal_url}\n\n"
                f"🟢 **Official Source — {best_sub.confidence_status}**"
            )
        elif user_goal == "PROCESSING_TIME":
            grounded_explanation = (
                f"⏱️ **Official Processing Timeline for {best_sub.sub_service_name}**:\n"
                f"• **Timeline**: {best_sub.processing_time}\n"
                f"• **Department**: {parent_srv.department if parent_srv else 'Competent Government Authority'}\n\n"
                f"🟢 **Official Source — {best_sub.confidence_status}**"
            )
        elif user_goal == "OFFICIAL_WEBSITE":
            grounded_explanation = (
                f"🔗 **Official Government Portal for {best_sub.sub_service_name}**:\n"
                f"• **Official Portal URL**: {best_sub.official_portal_url}\n"
                f"• **Authority / Department**: {parent_srv.department if parent_srv else 'State/Central Government'}\n\n"
                f"🟢 **Official Source — {best_sub.confidence_status}**"
            )
        else:
            grounded_explanation = format_service_grounded_answer(best_sub, parent_srv)

        sub_out = schemas.SubServiceOut.model_validate(best_sub)

        return schemas.AINavigationResponse(
            intent=f"RESOLVED_SERVICE_{best_sub.action_type}",
            confidence=min(1.0, best_service_score / 100.0),
            confidence_status=best_sub.confidence_status or "VERIFIED",
            explanation=grounded_explanation,
            needs_follow_up=False,
            resolved_sub_service=sub_out,
            documents=best_sub.required_documents or [],
            eligibility=best_sub.eligibility_criteria or [],
            official_fee=best_sub.official_fee,
            warnings=[]
        )
