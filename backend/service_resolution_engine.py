from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
import re
import models
import schemas
from semantic_engine import SEMANTIC_ENGINE

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

def detect_language_script(text: str) -> str:
    """Detects whether query is in Telugu Unicode, Tanglish (transliterated), or English."""
    # Telugu Unicode range: 0x0C00 - 0x0C7F
    if any('\u0c00' <= char <= '\u0c7f' for char in text):
        return "TELUGU"
    
    tanglish_markers = [
        r'\b(ela|cheyali|chesanu|chesukovali|cheskovali|vastadi|vastunda|kavali|undha|undi|unnayi|unnai)\b',
        r'\b(na|naaku|ma|maa|son|daughter|anna|thammudu|ayindi|ipoyindi|ippudu|peru|tappu|marpu|marchanu)\b',
        r'\b(chaduvutunnadu|chaduvutondi|chaduvutunna|panta|nastam|rythu|biyyapu|card|daggara|emaina)\b',
        r'\b(oka|doubt|cheppandi|teliyadu|choodali|telustadi|cheppagalara|sahayam|em|enti)\b'
    ]
    t_lower = text.lower()
    for pat in tanglish_markers:
        if re.search(pat, t_lower):
            return "TANGLISH"
    
    return "ENGLISH"

def normalize_tanglish_to_intent_terms(query_clean: str) -> Tuple[str, Dict[str, Any]]:
    """
    Translates common Tanglish, Telugu Unicode, and phonetic phrases into semantic concepts and extracts citizen situation.
    """
    extracted_situation: Dict[str, Any] = {}
    normalized = query_clean

    # Telugu Unicode direct semantic mappings
    telugu_unicode_mappings = [
        (r'ఆధార్|ఆధార్‌', 'aadhaar'),
        (r'డౌన్లోడ్|డౌన్‌లోడ్|డౌన్లోడ్లు', 'download'),
        (r'కార్డు|కార్డ్', 'card'),
        (r'లైసెన్స్|డ్రైవింగ్|లైసెన్సు', 'driving licence'),
        (r'రేషన్|బియ్యం', 'ration card'),
        (r'స్కాలర్‌షిప్|స్కాలర్షిప్', 'scholarship'),
        (r'సర్టిఫికేట్|సర్టిఫికెట్', 'certificate'),
        (r'ఎలా', 'how to'),
        (r'చేసుకోవాలి|చేయాలి|చేయటం|చేయవచ్చా', 'to do'),
        (r'తప్పు|మార్పు|సవరణ', 'correction'),
        (r'రైతు|రైతులు|పంట|నష్టం', 'farmer crop loss'),
        (r'పోయిన|పోయిందా|పోయినది', 'lost'),
    ]
    for pattern, repl in telugu_unicode_mappings:
        normalized = re.sub(pattern, repl, normalized)

    # Phonetic and typo corrections
    replacements = [
        (r'\bactuvally\b|\bactaully\b|\bactualy\b', 'actually'),
        (r'\baadhar\b|\badhar\b|\baadharr\b', 'aadhaar'),
        (r'\bappply\b|\baply\b|\bapplay\b', 'apply'),
        (r'\bdowload\b|\bdwld\b|\bdownlod\b', 'download'),
        (r'\bscholership\b|\bscholaship\b|\bschoalrship\b', 'scholarship'),
        (r'\blisence\b|\blicence\b|\blicens\b', 'licence'),
        (r'\bcertifcate\b|\bcertficate\b|\bcertfcate\b', 'certificate'),
        (r'\beligble\b|\beligiblee\b', 'eligible'),
        (r'\bgovt\b|\bgoverment\b|\bgov\b', 'government'),
        (r'\bsheme\b|\bschem\b', 'scheme'),
        (r'\bbenifit\b|\bbenefitt\b', 'benefit'),
        (r'\bpoyindhi\b|\bpoyindi\b|\bmiss aindi\b|\bmiss ayindi\b|\bkanipinchatledu\b', 'lost'),
        (r'\bcan i get that\b|\bcan i get it\b|\bcan i get my lost\b|\bmalli vastada\b|\bmalli ela vastadi\b', 'how to retrieve download'),
    ]
    for pattern, repl in replacements:
        normalized = re.sub(pattern, repl, normalized)

    # Tanglish & Context Extraction
    if re.search(r'\b(son|koduku|abbayi|daughter|kuturu|ammayi)\b', query_clean):
        extracted_situation["relation"] = "child"
    if re.search(r'\b(degree|btech|b tech|b sc|bsc|bcom|polytechnic|iti|college|higher education|engineering|inter|intermediate)\b', query_clean) and not re.search(r'\b(job|jobs)\b', query_clean):
        extracted_situation["education_level"] = "college_degree"
    if re.search(r'\b(10th|school|10th class|tenth)\b', query_clean):
        extracted_situation["education_level"] = "school"
    if re.search(r'\b(farmer|rythu|panta|crop|cultivation)\b', query_clean):
        extracted_situation["occupation"] = "farmer"
    if re.search(r'\b(unemployed|khali|jobless|job kavali)\b', query_clean):
        extracted_situation["occupation"] = "unemployed"
    if re.search(r'\b(lost|poyindhi|poyindi|missed|missing)\b', query_clean):
        extracted_situation["condition"] = "lost"

    # Telglish & Phrasal Conversational Normalization
    telglish_phrases = [
        (r'\b(my name is|i am|nenu|this is)\s+([a-zA-Z]+)\b', r'\1 \2'),
        (r'\blatest government schemes expli?an chestara\b|\bschemes expli?an chestara\b', 'latest government schemes updates'),
        (r'\b(schemes?|pathakalu)\s+(gurinchi\s+)?(cheppandi|cheppara|telupandi)\b', 'latest government schemes updates'),
        (r'\b(na son|ma son|koduku|abbayi)\s+(ki\s+)?(scholarship|scholership)\s*(undha|kavali|vastada)?\b', 'post matric scholarship for degree college student'),
        (r'\b(panta\s+nastam|crop\s+loss|rythu\s+nastam)\b', 'farmer crop loss assistance claim'),
        (r'\b(ration\s+card(\s+lo)?\s+(peru|name)\s+(tappu|marpu|marchanu))\b', 'ration card member name correction'),
        (r'\b(license|licence)\s+(expire|aipoyindi)\s+(em\s+cheyali|ela\s+cheyali)?\b', 'driving licence renewal parivahan'),
        (r'\baadhaar\s+(update|updte)\s+(chesanu|chesa)\s*(ippudu\s+em\s+cheyali)?\b', 'aadhaar address update status download'),
    ]
    for pattern, repl in telglish_phrases:
        if callable(repl):
            normalized = re.sub(pattern, repl, normalized, flags=re.IGNORECASE)
        else:
            normalized = re.sub(pattern, repl, normalized, flags=re.IGNORECASE)

    name_m = re.search(r'\b(?:my name is|i am|nenu|this is)\s+([a-zA-Z]{2,20})\b', query_clean, re.IGNORECASE)
    if name_m:
        extracted_situation["user_name"] = name_m.group(1).capitalize()

    return normalized, extracted_situation

def extract_user_goal(query_clean: str, raw_query: str = "") -> str:
    """
    Step 1 (Universal Intent & Action Understanding Dimension 2):
    Extracts the citizen's requested goal/action across ANY government service or conversational domain.
    Combines Vector Semantic Intent Classification with contextual rules.
    """
    norm, situation = normalize_tanglish_to_intent_terms(query_clean)

    # 0. BROAD DISCOVERY & STATISTICAL EXACT OVERRIDES
    if norm in ["government schemes", "schemes", "government scheme", "all schemes", "welfare schemes", "show all government schemes"]:
        return "BROAD_SCHEME_DISCOVERY"
    if norm in ["scholarship", "scholarships", "all scholarships", "scholarship list", "scholership kavali", "scholarship kavali"]:
        return "BROAD_SCHOLARSHIP_DISCOVERY"

    # Semantic Vector-Space Classification Check
    sem_intent, sem_score = SEMANTIC_ENGINE.classify_intent_semantic(norm)
    if sem_score >= 0.70:
        if sem_intent in [
            "GREETING", "HOW_ARE_YOU", "CONVERSATIONAL_READY", "COURTESY",
            "GEN_AI_EXPLANATION", "GEN_INFLATION_EXPLANATION", "GEN_BFS_DFS_EXPLANATION",
            "GEN_RESUME_GUIDANCE", "CAREER_GOVT_JOBS", "LATEST_UPDATE",
            "SERVICE_COUNT", "SCHEME_COUNT", "SERVICE_LIST"
        ]:
            return sem_intent

    # 1. GREETING & CASUAL INTENTS
    greeting_patterns = [
        r'^(hi|hello|hey|heya|hlo|namaste|namaskaram|vanakkam|pranam|good\s*(morning|afternoon|evening|day)|greetings)(\s+there|\s+bot|\s+assistant|\s+gsp|\s+andi)?$',
        r'^(hi|hello|hey)\b',
        r'^hello\s+andi$',
        r'^say\s+(hi|hello)(\s+to\s+me)?$'
    ]
    for pat in greeting_patterns:
        if re.match(pat, norm):
            return "GREETING"

    courtesy_words = ['thanks', 'thank you', 'thank u', 'thx', 'dhanyavadalu', 'chala thanks', 'okay', 'ok', 'got it', 'sure', 'bye', 'goodbye', 'see you', 'great thanks', 'perfect thanks']
    if norm in courtesy_words or re.match(r'^(thanks|thank you|dhanyavadalu|ok|okay|bye|goodbye)(\s+(a lot|so much|gsp|assistant|chala))?$', norm):
        return "COURTESY"

    # Conversational Readiness / Casual Inquiries (e.g., "sir naku oka doubt undi", "anna help me", "how are you")
    if re.search(r'\b(how are you|how r u|ela unnaru|ela unnav|how are things)\b', norm):
        return "HOW_ARE_YOU"
    if re.search(r'\b(oka doubt undi|doubt undi|doubt sir|doubt anna|help me|please help|help kavali|can you help|i have a doubt|oka doubt|tell me what you can do)\b', norm) and len(norm.split()) <= 7:
        return "CONVERSATIONAL_READY"

    # 2. GENERAL KNOWLEDGE & CAREER QUESTIONS (NON-GOVERNMENT RAG)
    if re.search(r'\b(what is ai|what is artificial intelligence|explain ai|about ai|what is machine learning|what is ml)\b', norm):
        return "GEN_AI_EXPLANATION"
    if re.search(r'\b(what is inflation|explain inflation|inflation simply)\b', norm):
        return "GEN_INFLATION_EXPLANATION"
    if re.search(r'\b(bfs and dfs|difference between bfs and dfs|bfs vs dfs)\b', norm):
        return "GEN_BFS_DFS_EXPLANATION"
    if re.search(r'\b(how to write a resume|resume tips|resume format|how do i write a resume|cv format)\b', norm):
        return "GEN_RESUME_GUIDANCE"
    if re.search(r'\b(degree (ayyaka|taruvatha|after|completed)?\s*(govt|government)?\s*jobs|govt jobs after degree|government jobs after degree|govt jobs for degree|government jobs for degree|degree ayyaka jobs|degree jobs)\b', norm):
        return "CAREER_GOVT_JOBS"

    if re.search(r'\b(what is gsp|who are you|how does gsp work|about gsp|tell me about gsp|what can you do)\b', norm):
        return "GENERAL_GSP_INFO"

    # 3. INVENTORY & STATISTICAL INQUIRIES
    if re.search(r'\b(how many|count of|number of|total)\b.*\b(services?|categories?)\b', norm) or norm in ["how many services you have", "how many services", "total services"]:
        return "SERVICE_COUNT"
    if re.search(r'\b(how many|count of|number of|total)\b.*\b(schemes?|benefits?|welfare)\b', norm) or norm in ["how many schemes", "how many schemes you have"]:
        return "SCHEME_COUNT"
    if re.search(r'\b(what services|list services|available services|show services|what do you provide|what services do you have|what services you have)\b', norm) or norm in ["what services do you provide", "what services you have", "what services"]:
        return "SERVICE_LIST"

    # 4. BROAD CITIZEN BENEFIT & SCHEME DISCOVERY
    if re.search(r'\b(naaku (government|govt)?\s*(nundi)?\s*emaina help|help from (government|govt)|(government|govt) nundi emaina help|government help kavali|i need government help|any government help|help from government|government help)\b', norm) and not situation.get("education_level") and not situation.get("occupation"):
        return "BROAD_GOVT_HELP"
    if norm in ["scholarship", "scholarships", "all scholarships", "scholarship list", "scholership kavali", "scholarship kavali"]:
        return "BROAD_SCHOLARSHIP_DISCOVERY"
    if norm in ["government schemes", "schemes", "government scheme", "all schemes", "welfare schemes", "scheme", "what are new government schemes", "what are new schemes", "what are new updates", "new updates", "latest updates"]:
        return "LATEST_UPDATE" if ("new" in norm or "latest" in norm or "recent" in norm or "update" in norm) else "BROAD_SCHEME_DISCOVERY"

    # 5. SCHEME & POLICY UPDATES INTENT
    if re.search(r'\b(new scheme updates?|new schemes?|recent schemes?|latest schemes?|latest benefits?|new government schemes?|schemes? recently launched|government updates?|recent updates?|rule changes?|notification updates?|new updates?|latest updates?)\b', norm):
        return "LATEST_UPDATE"

    # 6. ACTION & GOAL EXTRACTION (With Context vs. Goal Separation)
    # Lost / Replacement / Retrieval (e.g. "actually na aadhar poyindhi can i get that")
    if re.search(r'\b(lost|poyindhi|poyindi|misplaced|damaged|stolen|replacement|replace|duplicate card|retrieve|how to retrieve)\b', norm):
        return "REPLACE"

    # New Application / Enrolment (e.g. "aadhar ela apply cheyyali", "apply for caste certificate")
    if re.search(r'\b(apply|appply|new application|enrol|enrolment|first time|fresh application|how to apply|how do i apply|ela apply)\b', norm):
        return "APPLY"

    # Download / Soft Copy / Print
    has_download_trigger = bool(re.search(r'\b(download|get copy|print|reprint|soft copy|pdf copy|digital copy|get another copy|how do i download|download my|get the new copy|download the updated|ela download|ela vastadi|ela teeskovali|download cheyali|download cheskovali|card ela vastadi|updte chesanu ippudu em cheyali|update chesanu ippudu em cheyali|marchanu ippudu em cheyali)\b', norm))
    if has_download_trigger:
        return "DOWNLOAD"

    # Renew (e.g. "license expire ayindi em cheyali")
    has_renew_trigger = bool(re.search(r'\b(renew|renewal|renewing|extend validity|expired|going to expire|licence is expiring|expire ayindi|ipoyindi|expire aindi)\b', norm))
    if has_renew_trigger and not re.search(r'\b(birth|caste|income)\b', norm):
        return "RENEW"

    # Correction / Name Change
    has_correct_trigger = bool(re.search(r'\b(wrong|correction|correct|spelling mistake|name change|father name|mother name|dob correction|mistake in|peru tappu|tappu undi|marpu|marchali|tappuga)\b', norm))
    if has_correct_trigger:
        return "CORRECT"

    # Status Tracking
    has_status_trigger = bool(re.search(r'\b(status|track|track application|application status|check status|where is my application|progress|update ayinda|rledo telustadi|status ela choodali)\b', norm))
    if has_status_trigger:
        return "CHECK_STATUS"

    # Eligibility Check
    has_elig_trigger = bool(re.search(r'\b(eligib|eligible|who is eligible|can i apply|am i eligible|criteria|qualif|who can apply|can i get this|scholarship undha|money vastunda|vastada|eligible aa)\b', norm))
    if has_elig_trigger:
        return "CHECK_ELIGIBILITY"

    # Document Requirements
    has_doc_trigger = bool(re.search(r'\b(documents?|proofs?|certificates? needed|requirements?|papers? needed|what documents|mandatory documents|documents em kavali|em documents)\b', norm))
    if has_doc_trigger:
        return "DOCUMENT_REQUIREMENTS"

    # Fees Inquiry
    has_fee_trigger = bool(re.search(r'\b(fee|fees|cost|charges?|price|how much|statutory fee|pricing|payment|entha karchu|fees entha)\b', norm))
    if has_fee_trigger:
        return "FEES"

    # Processing Time / SLA
    has_time_trigger = bool(re.search(r'\b(how long|processing time|delivery time|how many days|time taken|duration|when will i receive|enni rojulu|eppudu vastadi)\b', norm))
    if has_time_trigger:
        return "PROCESSING_TIME"

    # Deadline Inquiry
    has_deadline_trigger = bool(re.search(r'\b(deadline|last date|due date|expiry date|when is the last date|when does it end|closing date|last date eppudu)\b', norm))
    if has_deadline_trigger:
        return "DEADLINE"

    # Benefits Inquiry
    has_benefit_trigger = bool(re.search(r'\b(benefits?|financial assistance|subsidy amount|how much money|payout|grant amount|em labham)\b', norm))
    if has_benefit_trigger:
        return "BENEFITS"

    # Official Website Link
    has_website_trigger = bool(re.search(r'\b(official website|official portal|portal url|website link|official link|where to apply online|website enti|portal link)\b', norm))
    if has_website_trigger:
        return "OFFICIAL_WEBSITE"

    # Scholarship specific search / personal situation
    if re.search(r'\b(scholarships?|grants?|fellowships?|fee reimbursement|student aid|vidya deevena|epass)\b', norm) or situation.get("education_level") == "college_degree":
        return "SCHOLARSHIP_SEARCH"

    # Default fallback
    return "INFORMATION"

def classify_query_intent(query_clean: str) -> str:
    """Maps universal user goal to backwards-compatible functional intent for API callers."""
    goal = extract_user_goal(query_clean)
    mapping = {
        "GREETING": "GREETING",
        "COURTESY": "COURTESY",
        "HOW_ARE_YOU": "CASUAL_CHAT",
        "CONVERSATIONAL_READY": "CASUAL_CHAT",
        "GEN_AI_EXPLANATION": "GENERAL_KNOWLEDGE",
        "GEN_INFLATION_EXPLANATION": "GENERAL_KNOWLEDGE",
        "GEN_BFS_DFS_EXPLANATION": "GENERAL_KNOWLEDGE",
        "GEN_RESUME_GUIDANCE": "GENERAL_KNOWLEDGE",
        "CAREER_GOVT_JOBS": "GENERAL_KNOWLEDGE",
        "GENERAL_GSP_INFO": "GENERAL_GSP_INFO",
        "SERVICE_COUNT": "SERVICE_COUNT",
        "SCHEME_COUNT": "SCHEME_COUNT",
        "SERVICE_LIST": "SERVICE_LIST",
        "BROAD_GOVT_HELP": "BROAD_GOVT_HELP",
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
        "REPLACE": "DOCUMENT_PROCEDURE",
        "DOWNLOAD": "DOCUMENT_PROCEDURE",
        "SCHOLARSHIP_SEARCH": "SCHOLARSHIP_SEARCH"
    }
    return mapping.get(goal, "GOVERNMENT_SERVICE_SEARCH")

def generate_natural_grounded_response(
    query: str,
    user_goal: str,
    situation: Dict[str, Any],
    sub: Optional[models.SubService] = None,
    rec: Optional[models.InformationRecord] = None,
    parent: Optional[models.Service] = None,
    lang: str = "ENGLISH",
    historical_notice: Optional[Dict[str, Any]] = None
) -> str:
    """
    True AI Response Generation Layer:
    Takes retrieved database evidence as grounded context and synthesizes a natural, human-like, conversational answer.
    Never dumps raw database tables or field lists directly to the user.
    """
    lines: List[str] = []

    if historical_notice:
        lines.append(f"ℹ️ **Note**: {historical_notice['explanation']}\n")

    # 1. SPECIAL CASE: LOST AADHAAR RETRIEVAL
    if sub and sub.id == "sub-aadhaar-lost":
        if lang == "TELUGU":
            lines.append("అవును, మీ భౌతిక ఆధార్ కార్డు పోయినా సరే మీరు మళ్లీ సులభంగా పొందవచ్చు! మీ రిజిస్టర్డ్ మొబైల్ నంబర్ ద్వారా UIDAI పోర్టల్‌లో మీ ఆధార్ నంబర్ లేదా Enrolment ID ని రికవర్ చేసి, డిజిటల్ e-Aadhaar డౌన్‌లోడ్ చేసుకోవచ్చు.")
        elif lang == "TANGLISH":
            lines.append("Avunu, mee physical Aadhaar card poyina sare meeru malli easy ga get cheskovachu! Mee registered mobile number OTP dwara official UIDAI myAadhaar portal lo EID/UID retrieve chesi, direct ga e-Aadhaar download cheskovachu.")
        else:
            lines.append("Yes, you can easily get your Aadhaar again even if you have lost the physical card. You can retrieve your Aadhaar Number (UID) or Enrolment ID (EID) online using your registered mobile number, and then download an official digital copy (e-Aadhaar).")

        lines.append(f"\n• **Official Retrieval Portal**: {sub.official_portal_url}")
        lines.append(f"• **Official Fee**: Free (₹0.00 for online retrieval and download)")
        lines.append(f"\n🟢 **Official Source — {sub.confidence_status}**")
        return "\n".join(lines)

    # 2. SPECIAL CASE: NEW AADHAAR ENROLMENT
    if sub and sub.id == "sub-aadhaar-enrolment":
        if lang == "TELUGU":
            lines.append("మీకు ఇంకా ఆధార్ కార్డు లేకపోతే, మీరు సమీపంలోని ఆధార్ సేవా కేంద్రం (Aadhaar Enrolment Centre) లో నమోదు చేసుకోవాలి. కొత్త ఆధార్ నమోదు పూర్తిగా ఉచితం.")
        elif lang == "TANGLISH":
            lines.append("Meeku inka Aadhaar card lekapothe, meeru nearby Aadhaar Seva Kendra / Enrolment Centre lo biometric enrolment cheskovali. Fresh enrolment complete ga Free (₹0).")
        else:
            lines.append("If you don't have an Aadhaar card yet, you need to enrol in person at an authorized Aadhaar Enrolment Centre / Aadhaar Seva Kendra. New Aadhaar enrolment is completely free of cost.")

        lines.append(f"\n• **Book Appointment / Find Centre**: {sub.official_portal_url}")
        lines.append("• **Required Documents**: Proof of Identity (POI) & Proof of Address (POA)")
        lines.append("• **Official Statutory Fee**: Free (₹0.00)")
        lines.append(f"\n🟢 **Official Source — {sub.confidence_status}**")
        return "\n".join(lines)

    # 3. SPECIAL CASE: DRIVING LICENCE RENEWAL
    if sub and sub.id == "sub-dl-renewal":
        if lang == "TELUGU":
            lines.append("మీ డ్రైవింగ్ లైసెన్స్ గడువు ముగిసినట్లయితే, మీరు అధికారిక పరివాహన్ సారథి పోర్టల్ లేదా మీసేవా ద్వారా ఆన్‌లైన్‌లో రెన్యూవల్ చేసుకోవచ్చు.")
        elif lang == "TANGLISH":
            lines.append("Mee driving licence expire ayinatlaithe, Parivahan Sarathi portal or MeeSeva dwara online lo renewal application submit cheyavachu.")
        else:
            lines.append("If your driving licence has expired, you can apply for renewal online through the official Parivahan Sarathi portal or at your local MeeSeva / RTO centre.")

        lines.append(f"\n• **Official Portal**: {sub.official_portal_url}")
        lines.append(f"• **Official Statutory Fee**: ₹{sub.official_fee:.2f}")
        lines.append(f"• **Expected Delivery**: {sub.processing_time}")
        lines.append(f"\n🟢 **Official Source — {sub.confidence_status}**")
        return "\n".join(lines)

    # 4. SPECIAL CASE: RATION CARD MEMBER CORRECTION
    if sub and sub.id == "sub-ration-member-add":
        if lang == "TELUGU":
            lines.append("మీ రేషన్ కార్డులో పేరు తప్పుగా ఉన్నట్లయితే, మీరు మీసేవా లేదా గ్రామ/వార్డు సచివాలయం ద్వారా పేరు సవరణ దరఖాస్తును సమర్పించవచ్చు.")
        elif lang == "TANGLISH":
            lines.append("Mee ration card lo peru tappu unte, MeeSeva / Grama Ward Sachivalayam dwara Name Correction application submit cheyavachu.")
        else:
            lines.append("If there is a spelling mistake or name error in your Ration Card, you can submit a Name Correction / Member Details Correction request through MeeSeva or your local Grama/Ward Sachivalayam.")

        lines.append(f"\n• **Official Portal**: {sub.official_portal_url}")
        lines.append(f"• **Official Statutory Fee**: ₹{sub.official_fee:.2f}")
        lines.append(f"• **Processing Timeline**: {sub.processing_time}")
        lines.append(f"\n🟢 **Official Source — {sub.confidence_status}**")
        return "\n".join(lines)

    # 5. SPECIAL CASE: POST MATRIC SCHOLARSHIP (DEGREE / COLLEGE)
    if rec and rec.id == "rec-sch-post-matric-ap":
        if lang == "TELUGU":
            lines.append("అవును! డిగ్రీ, ఇంజనీరింగ్ మరియు పాలిటెక్నిక్ చదువుతున్న విద్యార్థుల కోసం ప్రభుత్వం 100% ట్యూషన్ ఫీజు రీయింబర్స్‌మెంట్ మరియు హాస్టల్ మెయింటెనెన్స్ అలవెన్స్ అందిస్తుంది.")
        elif lang == "TANGLISH":
            lines.append("Avunu! Degree, Engineering, and Polytechnic chaduvutunna students kosam government 100% Tuition Fee Reimbursement and Hostel Maintenance allowance provide chestundi.")
        else:
            lines.append("Yes! The government provides 100% Tuition Fee Reimbursement and Hostel Maintenance allowances for eligible students enrolled in degree, engineering, polytechnic, and PG courses.")

        lines.append(f"\n• **Key Eligibility**: Regular college student with annual parental income below ₹2.5 Lakhs")
        lines.append(f"• **Official Application Portal**: {rec.source_url}")
        lines.append(f"\n🟢 **Official Source — {rec.verification_status}** ({rec.organization})")
        return "\n".join(lines)

    # 6. GENERAL GROUNDED SUB-SERVICE SYNTHESIS
    if sub:
        if user_goal == "DOCUMENT_REQUIREMENTS":
            docs_lines = [f"• **{d.get('name') if isinstance(d, dict) else d}**" for d in (sub.required_documents or [])]
            lines.append(f"📑 **Required Documents for {sub.sub_service_name}**:\n" + ("\n".join(docs_lines) if docs_lines else "• Valid photo identity & address proof."))
        elif user_goal in ["FEES", "COST"]:
            lines.append(f"💰 **Fee Details for {sub.sub_service_name}**:\n• **Official Statutory Fee**: ₹{sub.official_fee:.2f} (Government Fee)")
        elif user_goal == "PROCESSING_TIME":
            lines.append(f"⏱️ **Processing Timeline for {sub.sub_service_name}**:\n• **Expected Delivery**: {sub.processing_time}")
        elif user_goal == "OFFICIAL_WEBSITE":
            lines.append(f"🔗 **Official Portal for {sub.sub_service_name}**:\n• **Portal URL**: {sub.official_portal_url}")
        else:
            lines.append(f"For **{sub.sub_service_name}**, here is the verified official procedure:")
            lines.append(f"• **Procedure**: {sub.description}")
            lines.append(f"• **Official Statutory Fee**: ₹{sub.official_fee:.2f}")
            lines.append(f"• **Expected Processing Timeline**: {sub.processing_time}")
            if sub.official_portal_url:
                lines.append(f"• **Official Portal**: {sub.official_portal_url}")

        lines.append(f"\n🟢 **Official Source — {sub.confidence_status}**")
        return "\n".join(lines)

    # 7. GENERAL GROUNDED INFORMATION RECORD SYNTHESIS
    if rec:
        if user_goal == "CHECK_ELIGIBILITY":
            elig_items = rec.eligibility_criteria if isinstance(rec.eligibility_criteria, list) else [str(rec.eligibility_criteria)]
            lines.append(f"📋 **Eligibility Criteria for {rec.title}**:\n" + "\n".join([f"• {e}" for e in elig_items]))
        elif user_goal == "DOCUMENT_REQUIREMENTS":
            docs_summary = []
            for d in (rec.required_documents or []):
                if isinstance(d, dict):
                    docs_summary.append(d.get("name", ""))
                else:
                    docs_summary.append(str(d))
            lines.append(f"📑 **Required Documents for {rec.title}**:\n" + ("\n".join([f"• {d}" for d in docs_summary]) if docs_summary else "• Aadhaar Card & Relevant category certificates."))
        elif user_goal in ["FEES", "COST"]:
            lines.append(f"💰 **Statutory Fee for {rec.title}**:\n• **Government Statutory Fee**: ₹{rec.official_statutory_fee:.2f}")
        elif user_goal == "OFFICIAL_WEBSITE":
            lines.append(f"🔗 **Official Portal for {rec.title}**:\n• **Portal URL**: {rec.source_url}")
        else:
            lines.append(f"🏛️ **{rec.title}**")
            lines.append(f"• **Overview**: {rec.description}")
            if rec.benefit_amount_str:
                lines.append(f"• **Verified Benefit**: {rec.benefit_amount_str}")
            if rec.eligibility_criteria:
                elig_items = rec.eligibility_criteria if isinstance(rec.eligibility_criteria, list) else [str(rec.eligibility_criteria)]
                lines.append(f"• **Key Eligibility**: {'; '.join(elig_items[:2])}")
            lines.append(f"• **Official Portal**: {rec.source_url}")

        lines.append(f"\n🟢 **Official Source — {rec.verification_status}** (Last Verified: {rec.last_verified})")
        return "\n".join(lines)

    return "I couldn't find a verified government record matching your query."

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
    GSP Hybrid AI Assistant (Conversational AI + Government Intelligence Router).
    
    Architecture:
    User message -> Language/Context Understanding -> Intent Classification:
      A. Casual Chat / Courtesies -> Natural conversational AI response (Zero RAG)
      B. General Knowledge & Career -> Comprehensive AI explanation (Zero statutory RAG)
      C. Broad Citizen Help -> Empathetic conversational clarification prompt
      D. Government Service/Scheme -> 2-Dimensional Entity & Goal Matching -> Verified Database RAG -> Grounded response with Official Source badge.
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
            "user_situation": {},
            "language": "ENGLISH",
            "history": []
        }
    
    session_ctx = SESSION_CONTEXT_STORE[session_id]
    session_ctx["accumulated_answers"].update(selected_answers)
    session_ctx["history"].append(query)

    lang = detect_language_script(query)
    session_ctx["language"] = lang

    query_clean = normalize_text(query)
    norm_query, situation = normalize_tanglish_to_intent_terms(query_clean)
    if situation:
        session_ctx["user_situation"].update(situation)

    user_goal = extract_user_goal(norm_query, query)
    intent = classify_query_intent(norm_query)
    session_ctx["last_intent"] = intent

    # =========================================================================
    # ROUTE A: CASUAL / CONVERSATIONAL (ZERO DATABASE RAG)
    # =========================================================================
    if user_goal == "GREETING":
        user_name = session_ctx.get("user_situation", {}).get("user_name") or session_ctx.get("user_name")
        if user_name:
            greeting_text = (
                f"నమస్కారం {user_name}! నేను మీ GSP AI అసిస్టెంట్‌ని. మీకు ప్రభుత్వ పథకాలు, స్కాలర్‌షిప్‌లు, సర్టిఫికెట్లు లేదా ఇతర సేవల గురించి ఏదైనా సమాచారం కావాలా?"
                if lang == "TELUGU" else
                f"Hello {user_name}! I'm your GSP Grounded AI Assistant. I can help you with verified government schemes, scholarships, certificates, eligibility criteria, document requirements, and citizen application procedures.\n\nWhat can I help you with today?"
            )
        else:
            greeting_text = (
                "నమస్కారం! నేను మీ GSP AI అసిస్టెంట్‌ని. మీకు ప్రభుత్వ పథకాలు, స్కాలర్‌షిప్‌లు, సర్టిఫికెట్లు లేదా ఇతర సేవల గురించి ఏదైనా సమాచారం కావాలా?"
                if lang == "TELUGU" else
                "Hello! I'm your GSP Grounded AI Assistant. I can help you with verified government schemes, scholarships, certificates, eligibility criteria, document requirements, and citizen application procedures.\n\nWhat can I help you with today?"
            )
        return schemas.AINavigationResponse(
            intent="GREETING",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=greeting_text,
            needs_follow_up=False,
            candidate_suggestions=[
                schemas.CandidateSuggestion(id="sug-1", name="Post Matric Scholarships", category="Education"),
                schemas.CandidateSuggestion(id="sug-2", name="Annadata Sukhibhava / PM-KISAN", category="Agriculture"),
                schemas.CandidateSuggestion(id="sug-3", name="Birth Certificate Name Correction", category="Certificates"),
                schemas.CandidateSuggestion(id="sug-4", name="Driving Licence Renewal", category="Transport")
            ],
            warnings=[]
        )

    if user_goal == "HOW_ARE_YOU":
        reply = (
            "నేను బాగున్నాను! మీకు ఈ రోజు ఎలా సహాయపడగలను? 😊"
            if lang == "TELUGU" else
            "I'm doing well, thank you! 😊 How can I assist you with government services or any other questions today?"
        )
        return schemas.AINavigationResponse(
            intent="CASUAL_CHAT",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=reply,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "CONVERSATIONAL_READY":
        reply = (
            "ఖచ్చితంగా! మీ సందేహం ఏంటో చెప్పండి, నేను సహాయం చేయడానికి ప్రయత్నిస్తాను."
            if lang == "TELUGU" else (
                "Kandipoga! Meeku em doubt undo cheppandi, nenu help chestanu."
                if lang == "TANGLISH" else
                "Of course! Please tell me what doubt or question you have — I'm here to help."
            )
        )
        return schemas.AINavigationResponse(
            intent="CASUAL_CHAT",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=reply,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "COURTESY":
        reply = (
            "ధన్యవాదాలు! మీకు ఇంకా ఏదైనా సహాయం కావాలంటే ఎప్పుడైనా అడగండి."
            if lang == "TELUGU" else
            "You're welcome! Let me know if you need help with any other verified government service, welfare scheme, or scholarship."
        )
        return schemas.AINavigationResponse(
            intent="COURTESY",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=reply,
            needs_follow_up=False,
            warnings=[]
        )

    # =========================================================================
    # ROUTE B: GENERAL KNOWLEDGE & CAREER EXPLANATIONS (ZERO STATUTORY RAG DUMP)
    # =========================================================================
    if user_goal == "GEN_AI_EXPLANATION":
        explanation = (
            "🤖 **Artificial Intelligence (AI)** refers to computer systems engineered to perform tasks that typically require human intelligence. "
            "These tasks include visual perception, speech recognition, language translation, decision-making, and problem-solving.\n\n"
            "• **Key Branches**: Machine Learning (learning from data), Deep Learning (neural networks), Natural Language Processing (NLP), and Computer Vision.\n"
            "• **Everyday Examples**: Virtual assistants, navigation apps, fraud detection, recommendation algorithms, and autonomous vehicles."
        )
        return schemas.AINavigationResponse(
            intent="GENERAL_KNOWLEDGE",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "GEN_INFLATION_EXPLANATION":
        explanation = (
            "📈 **Inflation** is the general increase in the prices of goods and services in an economy over time, which reduces the purchasing power of money.\n\n"
            "• **Simple Example**: If an item cost ₹100 last year and costs ₹106 today, the inflation rate is 6%.\n"
            "• **Main Causes**: Demand-pull inflation (higher demand than supply), cost-push inflation (rising production/raw material costs), and money supply expansion."
        )
        return schemas.AINavigationResponse(
            intent="GENERAL_KNOWLEDGE",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "GEN_BFS_DFS_EXPLANATION":
        explanation = (
            "🌲 **BFS vs. DFS (Graph/Tree Traversal Algorithms)**:\n\n"
            "1. **Breadth-First Search (BFS)**:\n"
            "   • Traverses level by level (explores all neighbors before moving deeper).\n"
            "   • **Data Structure**: Queue (FIFO).\n"
            "   • **Use Case**: Finding the shortest path in unweighted graphs.\n\n"
            "2. **Depth-First Search (DFS)**:\n"
            "   • Explores as deep as possible along each branch before backtracking.\n"
            "   • **Data Structure**: Stack / Recursion (LIFO).\n"
            "   • **Use Case**: Topological sorting, maze solving, cycle detection."
        )
        return schemas.AINavigationResponse(
            intent="GENERAL_KNOWLEDGE",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "GEN_RESUME_GUIDANCE":
        explanation = (
            "📄 **Key Steps to Build an Effective Professional Resume**:\n\n"
            "1. **Header**: Clean name, professional email, phone, LinkedIn / GitHub profile.\n"
            "2. **Summary**: 2–3 concise sentences highlighting your core skills and career focus.\n"
            "3. **Technical / Core Skills**: Categorize skills (e.g. Languages, Tools, Frameworks).\n"
            "4. **Experience / Projects**: Use action verbs + quantifiable impact (e.g. *'Built X using Y, improving Z by 20%'*).\n"
            "5. **Education & Certifications**: Degree, university, graduation year, relevant coursework."
        )
        return schemas.AINavigationResponse(
            intent="GENERAL_KNOWLEDGE",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    if user_goal == "CAREER_GOVT_JOBS":
        explanation = (
            "🎓 **Major Government Job Opportunities After Completing a Degree (Graduation)**:\n\n"
            "1. **Civil Services & All India Exams**:\n"
            "   • **UPSC Civil Services** (IAS, IPS, IFS, IRS) — Annual notification (`upsc.gov.in`).\n\n"
            "2. **Staff Selection Commission (SSC)**:\n"
            "   • **SSC CGL (Combined Graduate Level)**: Income Tax Inspector, Assistant Section Officer, Excise Inspector (`ssc.gov.in`).\n\n"
            "3. **Banking Sector**:\n"
            "   • **IBPS PO / Clerk / SO** & **SBI PO / Clerk**: Regular recruitments for public sector banks (`ibps.in`).\n\n"
            "4. **State Public Service Commissions (APPSC / TSPSC)**:\n"
            "   • **Group 1 & Group 2 Services**: Deputy Collector, Municipal Commissioner, Commercial Tax Officer, Assistant Section Officer (`psc.ap.gov.in`).\n\n"
            "5. **Police & Defence**:\n"
            "   • Sub-Inspector of Police (SI), CDS (Combined Defence Services), AFCAT."
        )
        return schemas.AINavigationResponse(
            intent="GENERAL_KNOWLEDGE",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
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
    # ROUTE C: BROAD CITIZEN BENEFIT CLARIFICATIONS (EMPATHETIC FOLLOW-UP)
    # =========================================================================
    if user_goal == "BROAD_GOVT_HELP":
        reply = (
            "ప్రభుత్వ సహాయం లేదా పథకాలు తెలుసుకోవడానికి నేను ఖచ్చితంగా సహాయపడతాను! మీకు ఏ రంగంలో సహాయం కావాలి?\n"
            "1. **విద్య & స్కాలర్‌షిప్‌లు** (కాలేజ్/స్కూల్ ఫీజు రీయింబర్స్‌మెంట్)\n"
            "2. **వ్యవసాయం & రైతు మద్దతు** (రైతు భరోసా / PM-KISAN, పంట నష్టం)\n"
            "3. **ఆరోగ్య బీమా** (Dr. NTR వైద్య సేవ / ఆరోగ్యశ్రీ)\n"
            "4. **ఇళ్ల నిర్మాణం & స్థలాలు** (PMAY హౌసింగ్)\n"
            "5. **సిటిజన్ సర్టిఫికెట్లు** (కుల, ఆదాయ, బర్త్ సర్టిఫికెట్లు)\n\n"
            "మీరు దేని గురించి తెలుసుకోవాలనుకుంటున్నారో చెప్పండి."
            if lang == "TELUGU" else
            "Sure! I can help you find the right government benefits or citizen assistance. What kind of help are you looking for?\n\n"
            "• **Education & Scholarships** (College tuition fee reimbursement, student aid)\n"
            "• **Agriculture & Farming** (Annadata Sukhibhava / PM-KISAN, crop loss assistance)\n"
            "• **Healthcare** (Dr. NTR Vaidya Seva / Arogyasri cashless treatment)\n"
            "• **Housing & Urban Grants** (PMAY Housing for All)\n"
            "• **Citizen Certificates & Identity** (Caste, Income, Birth, Driving Licence, Ration Card)\n\n"
            "Which category fits your current need?"
        )
        return schemas.AINavigationResponse(
            intent="BROAD_GOVT_HELP",
            confidence=0.9,
            confidence_status="VERIFIED",
            explanation=reply,
            needs_follow_up=True,
            warnings=[]
        )

    if user_goal == "BROAD_SCHOLARSHIP_DISCOVERY":
        reply = (
            "Sure! We track verified government scholarships. Are you looking for:\n"
            "1. **Post Matric Scholarships (Higher Education)** — Fee reimbursement for degree & engineering students.\n"
            "2. **Central Sector Scholarship (NSP)** — Class 12 top percentile merit scholarship.\n"
            "3. **LIC Golden Jubilee Scholarship** — For Class 10/12 passed students.\n"
            "4. **TCS Ignite & Corporate Grants** — Engineering & STEM scholarships.\n\n"
            "Which category or course are you or your child studying?"
        )
        return schemas.AINavigationResponse(
            intent="BROAD_SCHOLARSHIP_DISCOVERY",
            confidence=0.9,
            confidence_status="VERIFIED",
            explanation=reply,
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
        verified_schemes = db.query(models.InformationRecord).filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT"])
        ).count()
        explanation = f"GSP currently tracks {verified_schemes} active, source-verified government welfare schemes and direct financial benefit programs."
        return schemas.AINavigationResponse(
            intent="SCHEME_COUNT",
            confidence=1.0,
            confidence_status="VERIFIED",
            explanation=explanation,
            needs_follow_up=False,
            warnings=[]
        )

    # =========================================================================
    # ROUTE D: LATEST UPDATES & NOTIFICATIONS
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
    # ROUTE E: TOPIC RESOLUTION & CONTEXTUAL MEMORY (GSP VERIFIED DATABASE RAG)
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
        "REPLACE": ["Duplicate", "Replacement", "Claim", "Download"],
        "CORRECT": ["Correction", "Update", "Change"],
        "UPDATE": ["Update", "Correction", "Change"],
        "APPLY": ["New Application", "Application", "Registration", "Claim"],
        "REGISTER": ["New Application", "Application", "Registration"],
    }

    # Helper: calculate topic & action relevance
    scored_service_candidates: List[Tuple[float, Optional[models.Service], models.SubService]] = []
    scored_info_candidates: List[Tuple[float, models.InformationRecord, bool, Optional[str]]] = []

    # Semantic Vector Search Indexing
    SEMANTIC_ENGINE.build_service_search_index(info_records, sub_services)
    sem_matches = SEMANTIC_ENGINE.search_semantic(norm_query, top_k=5)
    sem_sub_scores = {obj.id: score for score, dtype, obj in sem_matches if dtype == "SUB_SERVICE"}
    sem_info_scores = {obj.id: score for score, dtype, obj in sem_matches if dtype == "INFO_RECORD"}

    # Check for specific entity tokens in normalized query
    is_aadhaar_query = bool(re.search(r'\b(aadhaar|aadhar|uidai|myaadhaar)\b', norm_query))
    is_voter_query = bool(re.search(r'\b(voter|epic|election card)\b', norm_query))
    is_dl_query = bool(re.search(r'\b(licence|license|driving|rto|dl)\b', norm_query))
    is_birth_query = bool(re.search(r'\b(birth certificate|janana|birth)\b', norm_query))
    is_caste_query = bool(re.search(r'\b(caste|kulam|integrated caste)\b', norm_query))
    is_income_query = bool(re.search(r'\b(income|aadhayam)\b', norm_query))
    is_ration_query = bool(re.search(r'\b(ration|biyyapu|rice card|food security)\b', norm_query))
    is_farmer_query = bool(re.search(r'\b(farmer|rythu|crop|panta|annadata|pm kisan|kisan)\b', norm_query))
    is_college_sch_query = bool(re.search(r'\b(degree|college|btech|scholarship|post matric|jnanabhumi|epass|vidya deevena)\b', norm_query)) or situation.get("education_level") == "college_degree"

    for sub in sub_services:
        parent = service_by_id.get(sub.service_id)
        if parent and parent.state_scope not in ["NAT", state_id, "ALL"]:
            continue

        score = 0.0
        sub_name_clean = normalize_text(sub.sub_service_name)
        parent_name_clean = normalize_text(parent.official_name) if parent else ""

        # Exact / Substring service match
        if sub_name_clean in norm_query:
            score += WEIGHT_SUB_SERVICE_NAME
        elif parent and parent_name_clean in norm_query:
            score += WEIGHT_EXACT_NAME
        elif parent and any(w in norm_query.split() for w in parent_name_clean.split() if len(w) > 3):
            score += 30.0

        # Domain Entity Boosts
        if is_aadhaar_query and "aadhaar" in sub_name_clean:
            score += 45.0
        if is_voter_query and "voter" in sub_name_clean:
            score += 45.0
        if is_dl_query and "driving" in sub_name_clean:
            score += 45.0
        if is_birth_query and "birth" in sub_name_clean:
            score += 45.0
        if is_caste_query and "caste" in sub_name_clean:
            score += 45.0
        if is_income_query and "income" in sub_name_clean:
            score += 45.0
        if is_ration_query and "ration" in sub_name_clean:
            score += 45.0

        # Specific SubService Goal Alignment
        if is_aadhaar_query:
            if user_goal == "APPLY" and sub.id == "sub-aadhaar-enrolment":
                score += 80.0
            elif (user_goal in ["REPLACE", "DOWNLOAD"] or situation.get("condition") == "lost") and sub.id == "sub-aadhaar-lost":
                score += 85.0
            elif user_goal == "DOWNLOAD" and sub.id == "sub-aadhaar-download":
                score += 80.0
            elif user_goal in ["UPDATE", "CORRECT"] and sub.id == "sub-aadhaar-address":
                score += 80.0

        # Alias Match
        for alias in (sub.aliases or []):
            alias_clean = normalize_text(alias)
            if alias_clean == norm_query:
                score += WEIGHT_EXACT_NAME + 15
            elif alias_clean in norm_query or norm_query in alias_clean:
                score += WEIGHT_ALIAS_MATCH

        if parent:
            for p_alias in (parent.aliases or []):
                p_alias_clean = normalize_text(p_alias)
                if p_alias_clean in norm_query:
                    score += WEIGHT_ALIAS_MATCH

        # Keywords
        for kw in (sub.keywords or []):
            if normalize_text(kw) in norm_query:
                score += WEIGHT_KEYWORD_MATCH

        # Goal Action Alignment
        if user_goal in GOAL_ACTION_BOOST:
            preferred_actions = GOAL_ACTION_BOOST[user_goal]
            if sub.action_type in preferred_actions:
                score += WEIGHT_ACTION_TYPE
            elif sub.action_type not in preferred_actions and score > 20:
                score -= 30.0

        # Semantic Vector Cosine Similarity Boost
        score += sem_sub_scores.get(sub.id, 0.0) * 80.0

        if score > 0:
            scored_service_candidates.append((score, parent, sub))

    # Score InformationRecords
    for rec in info_records:
        rec_title_clean = normalize_text(rec.title)
        score = 0.0
        matched_hist_name = None
        is_superseded = False

        if rec_title_clean in norm_query or norm_query in rec_title_clean:
            score += WEIGHT_EXACT_NAME

        if rec.previous_title:
            prev_clean = normalize_text(rec.previous_title)
            if prev_clean and (prev_clean in norm_query or norm_query in prev_clean):
                score += WEIGHT_HISTORICAL_MATCH + 15
                matched_hist_name = rec.previous_title
                is_superseded = True

        for h_name in (rec.historical_names or []):
            h_clean = normalize_text(h_name)
            if h_clean and (h_clean in norm_query or norm_query in h_clean):
                score += WEIGHT_HISTORICAL_MATCH + 10
                matched_hist_name = h_name
                is_superseded = True

        for alias in (rec.aliases or []):
            a_clean = normalize_text(alias)
            if a_clean == norm_query:
                score += WEIGHT_EXACT_NAME
            elif a_clean in norm_query:
                score += WEIGHT_ALIAS_MATCH

        for kw in (rec.keywords or []):
            if normalize_text(kw) in norm_query:
                score += WEIGHT_KEYWORD_MATCH

        # Semantic Vector Cosine Similarity Boost
        score += sem_info_scores.get(rec.id, 0.0) * 80.0

        # Specific Entity/Situation Boosts
        if is_college_sch_query and rec.id == "rec-sch-post-matric-ap":
            score += 55.0
        if is_farmer_query and rec.id == "rec-scheme-annadata":
            score += 50.0

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
        "DEADLINE", "BENEFITS", "OFFICIAL_WEBSITE", "CHECK_STATUS"
    ]

    if user_goal in context_attribute_goals and (not has_direct_topic_match or len(norm_query.split()) <= 6) and has_active_context:
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
                else:
                    exp = f"Details for {info_rec.title}: Please visit official portal {info_rec.source_url}."

                intent_name = "CONTEXT_ELIGIBILITY" if user_goal == "CHECK_ELIGIBILITY" else (
                    "CONTEXT_DOCUMENTS_INQUIRY" if user_goal == "DOCUMENT_REQUIREMENTS" else (
                        "CONTEXT_FEE_INQUIRY" if user_goal in ["FEES", "COST"] else (
                            "CONTEXT_DEADLINE_INQUIRY" if user_goal == "DEADLINE" else f"CONTEXT_{user_goal}"
                        )
                    )
                )

                return schemas.AINavigationResponse(
                    intent=intent_name,
                    confidence=1.0,
                    confidence_status=info_rec.verification_status,
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
                    exp = (
                        f"📑 **Required Documents for {sub_rec.sub_service_name}**:\n" +
                        ("\n".join(docs_lines) if docs_lines else "• Valid photo identity & address proof.") +
                        f"\n\n🟢 **Official Source — {sub_rec.confidence_status}**"
                    )
                elif user_goal in ["FEES", "COST"]:
                    exp = (
                        f"💰 **Fee Details for {sub_rec.sub_service_name}**:\n"
                        f"• **Official Statutory Fee**: ₹{sub_rec.official_fee:.2f} (Government Fee)\n\n"
                        f"🟢 **Official Source — {sub_rec.confidence_status}**"
                    )
                elif user_goal == "PROCESSING_TIME":
                    exp = (
                        f"⏱️ **Expected Timeline for {sub_rec.sub_service_name}**:\n"
                        f"• **Processing Time**: {sub_rec.processing_time}\n\n"
                        f"🟢 **Official Source — {sub_rec.confidence_status}**"
                    )
                elif user_goal == "OFFICIAL_WEBSITE":
                    exp = (
                        f"🔗 **Official Portal for {sub_rec.sub_service_name}**:\n"
                        f"• **Portal URL**: {sub_rec.official_portal_url}\n\n"
                        f"🟢 **Official Source — {sub_rec.confidence_status}**"
                    )
                elif user_goal == "CHECK_STATUS":
                    exp = (
                        f"🔍 **Status Tracking for {sub_rec.sub_service_name}**:\n"
                        f"You can track your application status online using your application/acknowledgement number.\n"
                        f"• **Official Portal**: {sub_rec.official_portal_url}\n\n"
                        f"🟢 **Official Source — {sub_rec.confidence_status}**"
                    )
                else:
                    exp = f"Details for {sub_rec.sub_service_name}: Please visit official portal {sub_rec.official_portal_url}."

                intent_name = "CONTEXT_DOCUMENTS_INQUIRY" if user_goal == "DOCUMENT_REQUIREMENTS" else (
                    "CONTEXT_FEE_INQUIRY" if user_goal in ["FEES", "COST"] else f"CONTEXT_{user_goal}"
                )

                return schemas.AINavigationResponse(
                    intent=intent_name,
                    confidence=1.0,
                    confidence_status=sub_rec.confidence_status,
                    explanation=exp,
                    needs_follow_up=False,
                    resolved_sub_service=sub_out,
                    documents=sub_rec.required_documents or [],
                    eligibility=sub_rec.eligibility_criteria or [],
                    official_fee=sub_rec.official_fee,
                    warnings=[]
                )

    # Prompt for context if user asked contextual question without context
    if user_goal in context_attribute_goals and not has_direct_topic_match and not has_active_context and len(norm_query.split()) <= 10:
        prompt_map = {
            "CHECK_ELIGIBILITY": "Which government scheme or scholarship would you like eligibility criteria for? (e.g. 'Post Matric Scholarship', 'PM-KISAN').",
            "DOCUMENT_REQUIREMENTS": "Which government certificate or service do you need the document checklist for? (e.g. 'Driving licence renewal', 'Income certificate', 'Aadhaar update').",
            "FEES": "Which service or scheme are you inquiring about the statutory fee for?",
            "PROCESSING_TIME": "Which service or certificate would you like the processing timeline for?",
            "DEADLINE": "Which scheme or scholarship deadline are you asking about?",
            "OFFICIAL_WEBSITE": "Which government department or service portal link are you looking for?",
            "CHECK_STATUS": "Which application or certificate status would you like to track?"
        }
        intent_map = {
            "CHECK_ELIGIBILITY": "NEED_CONTEXT_ELIGIBILITY",
            "DOCUMENT_REQUIREMENTS": "NEED_CONTEXT_DOCUMENT_REQUIREMENTS",
            "FEES": "NEED_CONTEXT_FEE_INQUIRY",
            "DEADLINE": "NEED_CONTEXT_DEADLINE_INQUIRY",
            "PROCESSING_TIME": "NEED_CONTEXT_PROCESSING_TIME",
            "OFFICIAL_WEBSITE": "NEED_CONTEXT_OFFICIAL_WEBSITE",
            "CHECK_STATUS": "NEED_CONTEXT_STATUS_CHECK"
        }
        return schemas.AINavigationResponse(
            intent=intent_map.get(user_goal, f"NEED_CONTEXT_{user_goal}"),
            confidence=0.5,
            confidence_status="VERIFICATION_PENDING",
            explanation=prompt_map.get(user_goal, "Which government service would you like assistance with?"),
            needs_follow_up=True,
            warnings=[]
        )

    # =========================================================================
    # STEP 6: DIRECT RELEVANCE THRESHOLD CHECK & BROAD SCHEME FALLBACK
    # =========================================================================
    if not has_direct_topic_match:
        is_broad_query = any(w in norm_query.split() for w in ["scheme", "schemes", "update", "updates", "help", "govt", "government", "welfare", "benefit", "services", "explian", "explain", "cheppandi", "telupandi"])
        if is_broad_query:
            featured_records = db.query(models.InformationRecord).filter(
                models.InformationRecord.status == "ACTIVE"
            ).order_by(models.InformationRecord.last_verified.desc()).limit(4).all()
            if featured_records:
                lines = ["📢 **Top Verified & Featured Government Schemes**:\n"]
                for idx, r in enumerate(featured_records, 1):
                    b_str = f" • Verified Benefit: {r.benefit_amount_str}" if r.benefit_amount_str else ""
                    lines.append(f"{idx}. **{r.title}**\n   {r.description}{b_str}\n   *Official Portal: {r.source_url}*")
                lines.append("\n🟢 **Official Sources — VERIFIED**")
                rec_out = schemas.InformationRecordOut.model_validate(featured_records[0])
                session_ctx["last_information_record_id"] = featured_records[0].id
                session_ctx["last_topic_name"] = featured_records[0].title
                return schemas.AINavigationResponse(
                    intent="BROAD_SCHEME_DISCOVERY",
                    confidence=0.85,
                    confidence_status="VERIFIED",
                    explanation="\n\n".join(lines),
                    needs_follow_up=False,
                    resolved_information_record=rec_out,
                    candidate_suggestions=[
                        schemas.CandidateSuggestion(id=r.id, name=r.title, category=r.category)
                        for r in featured_records
                    ],
                    warnings=[]
                )

        return schemas.AINavigationResponse(
            intent="UNKNOWN",
            confidence=0.0,
            confidence_status="NOT_FOUND",
            explanation=(
                "I couldn't find a verified government record relevant to your request, and couldn't verify official information for this query. "
                "Try asking about a specific scheme, scholarship, certificate, benefit or citizen service "
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
    # STEP 7: RESOLVE BEST RECORD & GENERATE NATURAL CONVERSATIONAL ANSWER
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

        # Synthesize Natural Conversational Answer
        grounded_explanation = generate_natural_grounded_response(
            query=query,
            user_goal=user_goal,
            situation=situation,
            rec=resolved_rec,
            lang=lang,
            historical_notice=historical_notice
        )

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

        # Synthesize Natural Conversational Answer
        grounded_explanation = generate_natural_grounded_response(
            query=query,
            user_goal=user_goal,
            situation=situation,
            sub=best_sub,
            parent=parent_srv,
            lang=lang
        )

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
