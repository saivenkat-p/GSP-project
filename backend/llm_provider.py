from typing import List, Dict, Any, Optional
import os
import json
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are the GSP (Government Service Provider) AI Assistant.
You are a warm, highly knowledgeable, and conversational assistant for Indian citizens.

Core Guidelines:
1. Understand the citizen's question before answering.
2. Speak naturally, warmly, and simply. Never sound robotic.
3. Fully understand English, Telugu (Unicode), Tanglish (Telugu written in English script), mixed Telugu-English, typos, phonetic spelling, and informal citizen phrasing.
4. For normal conversation (greetings, 'how are you', 'thank you'), respond warmly and naturally.
5. For general knowledge questions ('what is AI', 'what is machine learning'), answer normally and helpfully.
6. For government-specific inquiries, base your facts strictly on the provided verified GSP evidence.
7. Separate the citizen's situation from the specific service goal:
   - If they lost their Aadhaar: explain how to retrieve/download e-Aadhaar online (UIDAI portal). Do NOT confuse this with Address Update.
   - If they want to apply for a fresh Aadhaar: explain new enrolment at an Aadhaar Seva Kendra.
   - If their licence expired: explain driving licence renewal on Parivahan Sarathi.
   - If their child is in college / engineering: explain relevant post-matric / engineering scholarships.
   - If their ration card has a name mistake: explain ration card correction / member update.
8. Never invent government schemes, eligibility, statutory fees, deadlines, procedures, or portal links.
9. If verified evidence is not available for a specific query, honestly state that official information is not yet verified in the database.
10. If the user asks for the official portal link, provide the exact official URL from the verified evidence.
"""

class LLMProvider:
    def classify_and_plan(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def generate_response(
        self,
        query: str,
        mode: str,
        conversation_history: List[Dict[str, str]],
        evidence: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> str:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        import google.generativeai as genai
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.client = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=SYSTEM_PROMPT
        )

    def classify_and_plan(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        prompt = f"""
You are the query analysis engine of the GSP Assistant.
Analyze the user's message and return a JSON object with:
- mode: "CONVERSATIONAL" (for greetings, thank you, bye), "GENERAL_AI" (general knowledge / what is AI), or "GOVERNMENT_GROUNDED" (for government schemes, certificates, scholarships, citizen services, ration cards, Aadhaar, licences, etc.)
- intent: short string (e.g. GREETING, GENERAL_AI, AADHAAR_LOST, AADHAAR_ENROLMENT, SCHOLARSHIP_SEARCH, DL_RENEWAL, RATION_CORRECTION, CONTEXT_FEE_INQUIRY, CONTEXT_DOCUMENTS_INQUIRY, CONTEXT_ELIGIBILITY, CONTEXT_PROCESSING_TIME, CONTEXT_WEBSITE_INQUIRY)
- needs_retrieval: boolean (true if GOVERNMENT_GROUNDED)
- search_query: search terms to query the verified government database
- situation: citizen's personal situation
- goal: citizen's specific service objective

User message: "{query}"
Recent conversation context: {json.dumps(conversation_history[-4:] if conversation_history else [])}

Return ONLY a valid JSON object.
"""
        try:
            resp = self.client.generate_content(prompt)
            text = resp.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())
        except Exception:
            return {
                "mode": "GOVERNMENT_GROUNDED" if any(w in query.lower() for w in ["aadhar", "aadhaar", "card", "scheme", "scholarship", "licence", "license", "ration", "certificate"]) else "CONVERSATIONAL",
                "intent": "CITIZEN_INQUIRY",
                "needs_retrieval": True,
                "search_query": query,
                "situation": None,
                "goal": None
            }

    def generate_response(
        self,
        query: str,
        mode: str,
        conversation_history: List[Dict[str, str]],
        evidence: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> str:
        prompt = f"""
Conversation History:
{json.dumps(conversation_history[-6:] if conversation_history else [])}

User's Latest Message: "{query}"
Mode: {mode}
Intent: {intent}

Verified Evidence from Official GSP Database:
{json.dumps(evidence, indent=2) if evidence else "None (No verified records found)"}

Task: Respond to the citizen in a natural, friendly, and helpful manner.
If evidence is present, synthesize the relevant steps, documents, statutory fee, and official portal URL clearly.
If no evidence is present for a government query, honestly inform them that verified records are not available.
Do not dump raw JSON. Speak directly to the citizen.
"""
        try:
            resp = self.client.generate_content(prompt)
            return resp.text.strip()
        except Exception:
            return f"I understand your request regarding '{query}'. Please allow me a moment to reconnect with the verified service network."


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def classify_and_plan(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        prompt = f"""
Analyze the user's message and return a JSON object with:
- mode: "CONVERSATIONAL", "GENERAL_AI", or "GOVERNMENT_GROUNDED"
- intent: short string
- needs_retrieval: boolean
- search_query: search terms for verified government database
- situation: citizen's personal situation
- goal: citizen's specific objective

User message: "{query}"
Recent conversation context: {json.dumps(conversation_history[-4:] if conversation_history else [])}

Return ONLY valid JSON.
"""
        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content)
        except Exception:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "CITIZEN_INQUIRY",
                "needs_retrieval": True,
                "search_query": query,
                "situation": None,
                "goal": None
            }

    def generate_response(
        self,
        query: str,
        mode: str,
        conversation_history: List[Dict[str, str]],
        evidence: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> str:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in (conversation_history[-6:] if conversation_history else []):
            role = "user" if h.get("sender") == "user" else "assistant"
            messages.append({"role": role, "content": h.get("text", "")})

        user_content = f"""
User's Latest Message: "{query}"
Mode: {mode}
Intent: {intent}

Verified Evidence from Official GSP Database:
{json.dumps(evidence, indent=2) if evidence else "None"}

Synthesize a natural, empathetic, and accurate answer for the citizen.
"""
        messages.append({"role": "user", "content": user_content})

        try:
            resp = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return f"I'm processing your inquiry regarding '{query}'. Please check back in a moment."


class MockProvider(LLMProvider):
    """
    Simple, transparent deterministic mock fallback for offline tests and CI/CD.
    """
    def classify_and_plan(
        self,
        query: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        q = query.lower().strip()
        last_evidence = (context or {}).get("last_evidence", [])
        
        # Casual Greetings & Conversational Readiness
        if "my name is " in q or any(w == q for w in ["hi", "hello", "namaste", "namaskaram", "hey", "hello andi", "hi sir", "hello sir", "namaste sir", "greetings"]):
            return {"mode": "CONVERSATIONAL", "intent": "GREETING", "needs_retrieval": False, "search_query": ""}
        
        # Check chit chat / courtesy
        if any(w in q for w in ["how are you", "how r u", "thank you", "thanks", "bye", "andi oka help kavali", "oka small doubt", "sir naaku oka doubt undi", "doubt sir", "doubt anna"]):
            return {"mode": "CONVERSATIONAL", "intent": "COURTESY", "needs_retrieval": False, "search_query": ""}
        
        # Check general AI / jokes / cooking
        if any(w in q for w in ["what is ai", "what is artificial intelligence", "tell me something interesting", "tell me a joke", "cook pizza", "bake a cake"]):
            return {"mode": "GENERAL_AI", "intent": "GENERAL_AI", "needs_retrieval": False, "search_query": ""}

        # Check Contextual Follow-up inquiries if previous turn had evidence and current query is short follow-up
        if last_evidence and not any(w in q for w in ["actually", "actuvally", "instead", "another", "my ration card", "my voter", "my driving"]):
            if any(w in q for w in ["cost", "fee", "how much", "charges"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CONTEXT_FEE_INQUIRY",
                    "needs_retrieval": False,
                    "search_query": "",
                    "situation": "Inquiring about statutory fee for previous service",
                    "goal": "Fee Inquiry"
                }
            if any(w in q for w in ["how long", "time", "days", "timeline", "duration", "processing"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CONTEXT_PROCESSING_TIME",
                    "needs_retrieval": False,
                    "search_query": "",
                    "situation": "Inquiring about processing time for previous service",
                    "goal": "Processing Time"
                }
            if any(w in q for w in ["document", "documents", "proof", "papers", "what documents"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CONTEXT_DOCUMENTS_INQUIRY",
                    "needs_retrieval": False,
                    "search_query": "",
                    "situation": "Inquiring about required documents for previous service",
                    "goal": "Documents Inquiry"
                }
            if any(w in q for w in ["eligible", "eligibility", "qualify", "am i eligible", "can i get"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CONTEXT_ELIGIBILITY",
                    "needs_retrieval": False,
                    "search_query": "",
                    "situation": "Inquiring about eligibility criteria for previous service",
                    "goal": "Eligibility Inquiry"
                }
            if any(w in q for w in ["website", "portal", "link", "url", "where to apply", "where is the official website"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CONTEXT_WEBSITE_INQUIRY",
                    "needs_retrieval": False,
                    "search_query": "",
                    "situation": "Inquiring about official portal URL for previous service",
                    "goal": "Portal Link"
                }

        # Broad Scheme Discovery
        if q in ["government schemes", "schemes", "govt schemes", "welfare schemes", "what government help is available", "government schemes available"]:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "BROAD_SCHEME_DISCOVERY",
                "needs_retrieval": False,
                "search_query": "",
                "situation": "Citizen exploring government schemes broadly",
                "goal": "Broad Scheme Discovery"
            }

        # Scheme Updates
        if any(phrase in q for phrase in ["scheme update", "scheme updates", "new schemes", "new scheme updates", "latest schemes", "what are new government schemes", "latest updates"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "SCHEME_UPDATES",
                "needs_retrieval": True,
                "search_query": "Birth Certificate Father Name Correction Driving Licence Renewal Scheme Update",
                "situation": "Citizen seeking latest government scheme and procedure updates",
                "goal": "Scheme Updates"
            }

        # Driving Licence Renewal (Check before lost/generic cards!)
        if any(w in q for w in ["driving licence", "driving license", "dl", "licence", "license"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "DL_RENEWAL",
                "needs_retrieval": True,
                "search_query": "Driving Licence Renewal Form 9 Sarathi",
                "situation": "Driving licence expired or needs renewal",
                "goal": "Renewal"
            }

        # Voter Card
        if "voter" in q:
            if any(w in q for w in ["lost", "missing", "poyindhi", "poyindi", "kanapadakunda"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "VOTER_LOST",
                    "needs_retrieval": True,
                    "search_query": "Duplicate Voter ID Card Replacement Form 8",
                    "situation": "Lost voter card",
                    "goal": "Duplicate Replacement"
                }
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "VOTER_SERVICE",
                "needs_retrieval": True,
                "search_query": "Duplicate Voter ID Card Replacement Form 8 NVSP",
                "situation": "Voter card service",
                "goal": "Voter ID"
            }

        # Caste Certificate
        if "caste" in q or "community" in q:
            if any(w in q for w in ["duplicate", "copy", "another"]):
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "CASTE_CERT_SERVICE",
                    "needs_retrieval": True,
                    "search_query": "Duplicate Caste Certificate MeeSeva Integrated",
                    "situation": "Lost or replacement caste certificate",
                    "goal": "Duplicate Copy"
                }
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "CASTE_CERT_SERVICE",
                "needs_retrieval": True,
                "search_query": "Integrated Certificate SC ST BC MeeSeva Caste",
                "situation": "Applying for caste certificate",
                "goal": "New Application"
            }

        # Income Certificate
        if "income" in q or "aadhaya" in q:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "INCOME_CERT_SERVICE",
                "needs_retrieval": True,
                "search_query": "Income Certificate MeeSeva Revenue",
                "situation": "Applying for income certificate",
                "goal": "Income Certificate"
            }

        # PM Kisan / Agriculture (check before general scholarships)
        if "pm-kisan" in q or "pm kisan" in q or "kisan" in q or "annadata" in q or "crop" in q or "rythu bharosa" in q or "farmer" in q:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "PM_KISAN_INFO",
                "needs_retrieval": True,
                "search_query": query,
                "situation": "Farmer seeking agricultural or PM-KISAN support",
                "goal": "Agricultural Benefit"
            }

        # Scholarships / Education / Student
        if any(w in q for w in ["scholarship", "scholership", "student", "degree", "b.tech", "engineering", "college", "fees", "abbai", "son", "pillodu", "lic scholarship", "jagananna vidya deevena", "vidya deevena", "lic"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "SCHOLARSHIP_SEARCH",
                "needs_retrieval": True,
                "search_query": query,
                "situation": "Student seeking education financial assistance",
                "goal": "Scholarship Discovery"
            }

        # Ration Card
        if any(w in q for w in ["ration", "rice card", "biyyapu"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "RATION_CARD_SERVICE",
                "needs_retrieval": True,
                "search_query": "Ration Card Member Addition EPDS AP",
                "situation": "Ration card update/inquiry",
                "goal": "Member / Name Correction"
            }

        # Healthcare / Aarogyasri / Vaidya Seva
        if "aarogyasri" in q or "vaidya seva" in q or "health card" in q or "ayushman" in q:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "HEALTHCARE_SCHEME",
                "needs_retrieval": True,
                "search_query": "Dr NTR Vaidya Seva Trust Scheme YSR Aarogyasri Health Scheme",
                "situation": "Citizen inquiring about state health assurance",
                "goal": "Healthcare Coverage"
            }

        # Birth Certificate Correction
        if "birth" in q or "father" in q or "mother" in q or "pillala" in q:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "BIRTH_CERT_CORRECTION",
                "needs_retrieval": True,
                "search_query": "Birth Certificate Child Name Correction Inclusion",
                "situation": "Correction in birth registration record",
                "goal": "Name Correction"
            }

        # Website / Portal Link Contextual Inquiry
        if last_evidence and any(w in q for w in ["portal", "link", "website", "url", "site", "online apply site", "web link", "official site", "official website"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "CONTEXTUAL_WEBSITE_INQUIRY",
                "needs_retrieval": False,
                "search_query": "",
                "situation": "Citizen requesting official portal link for current service/scheme",
                "goal": "Portal Link"
            }

        # Telugu Unicode Aadhaar Download
        if "ఆధార్" in q or "డౌన్లోడ్" in q:
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "AADHAAR_DOWNLOAD",
                "needs_retrieval": True,
                "search_query": "Aadhaar Card Download UIDAI myAadhaar PDF",
                "situation": "Citizen requesting Telugu Aadhaar digital download",
                "goal": "Aadhaar Download"
            }

        # Aadhaar Card Download / Status / Updated Card
        if any(phrase in q for phrase in ["download", "downlod", "soft copy", "pdf", "ela vastadi", "vastundi", "print", "get copy", "how to get", "updated", "updte", "update chesa", "updte chesanu"]):
            if "aadhar" in q or "aadhaar" in q or "adar" in q or "adhaar" in q or "adhar" in q or "card" in q:
                return {
                    "mode": "GOVERNMENT_GROUNDED",
                    "intent": "AADHAAR_DOWNLOAD",
                    "needs_retrieval": True,
                    "search_query": "Aadhaar Card Download UIDAI myAadhaar PDF",
                    "situation": "Citizen wants to download or retrieve official Aadhaar PDF",
                    "goal": "Aadhaar Download"
                }

        # Lost Aadhaar / Missing Card
        if any(w in q for w in ["poyindhi", "poyindi", "lost", "missing", "kanapadakunda", "miss ayyindi", "miss ayindi"]):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "AADHAAR_LOST",
                "needs_retrieval": True,
                "search_query": "Lost Aadhaar Retrieval Duplicate Download myAadhaar",
                "situation": "Lost Aadhaar card",
                "goal": "Retrieve / Download"
            }

        # Fresh Aadhaar Enrolment
        if any(w in q for w in ["apply", "enrolment", "fresh", "kavali", "first time", "appply"]) and ("aadhaar" in q or "aadhar" in q):
            return {
                "mode": "GOVERNMENT_GROUNDED",
                "intent": "AADHAAR_ENROLMENT",
                "needs_retrieval": True,
                "search_query": "New Aadhaar Enrolment Fresh Application UIDAI Enrolment Centre",
                "situation": "New Aadhaar applicant",
                "goal": "New Enrolment"
            }

        # General Government search
        return {
            "mode": "GOVERNMENT_GROUNDED",
            "intent": "GOVERNMENT_INQUIRY",
            "needs_retrieval": True,
            "search_query": query,
            "situation": None,
            "goal": None
        }

    def generate_response(
        self,
        query: str,
        mode: str,
        conversation_history: List[Dict[str, str]],
        evidence: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
        intent: Optional[str] = None
    ) -> str:
        if mode == "CONVERSATIONAL":
            if "name is" in query.lower():
                name_part = query.lower().split("name is")[-1].strip().split()[0].title()
                return f"Hello {name_part}! I'm your GSP Grounded AI Assistant. How can I help you today?"
            if any(w in query.lower() for w in ["how are you", "how r u"]):
                return "I'm doing great! How can I assist you with government services or citizen information today?"
            if any(w in query.lower() for w in ["thanks", "thank you"]):
                return "You're very welcome! If you need any more information regarding government schemes or services, feel free to ask."
            return "Hello! I'm your GSP Grounded AI Assistant. How can I help you today?"
        
        if mode == "GENERAL_AI":
            if any(w in query.lower() for w in ["joke", "pizza", "cook", "cake"]):
                return "I couldn't find a verified government record for that query in the GSP database. I specialize in verified government services, welfare schemes, certificates, and citizen guidance."
            return "Artificial Intelligence (AI) refers to computer systems engineered to perform tasks that typically require human intelligence, such as visual perception, language understanding, and decision making."

        if not evidence:
            return "I couldn't verify or find a verified government record for that request in the GSP database yet. Please check the official government portal or request assistance from our staff."

        primary = evidence[0]
        title = primary.get("sub_service_name") or primary.get("title") or primary.get("service_name", "Service")
        fee = primary.get("official_fee", 0.0)
        proc_time = primary.get("processing_time", "Standard Timeline")
        url = primary.get("official_portal_url") or primary.get("official_source_url", "")

        if intent == "CONTEXTUAL_WEBSITE_INQUIRY" and evidence:
            url = evidence[0].get("official_website_url") or evidence[0].get("source_url") or "https://myaadhaar.uidai.gov.in"
            return f"You can access the official verified portal directly here: {url}"

        if intent == "CONTEXT_FEE_INQUIRY":
            return f"The statutory official fee for **{title}** is ₹{fee:.2f}."

        if intent == "CONTEXT_PROCESSING_TIME":
            return f"The official processing timeline for **{title}** is {proc_time}."

        if intent == "CONTEXT_DOCUMENTS_INQUIRY":
            docs = primary.get("documents", [])
            doc_str = ", ".join([d.get("name", "") for d in docs]) if docs else "standard verification documents"
            return f"For **{title}**, the mandatory documents required are: {doc_str}."

        if intent == "CONTEXT_ELIGIBILITY":
            el = primary.get("eligibility", [])
            el_str = "\n".join([f"- {e}" for e in el]) if el else "Must satisfy standard state residency requirements."
            return f"Eligibility Criteria for **{title}**:\n{el_str}"

        if intent == "CONTEXT_WEBSITE_INQUIRY":
            return f"The official verified portal website for **{title}** is {url}."

        if intent == "SCHEME_UPDATES":
            return f"Latest Verified Government Scheme Updates:\n- **{title}**: {primary.get('description', '')}\nOfficial Source: {url}"

        # Lost Aadhaar specific natural explanation
        if "Lost Aadhaar" in title or "sub-aadhaar-lost" == primary.get("id"):
            return f"Yes, you can retrieve and download your Aadhaar again even if you have lost the physical card. You can retrieve your EID/UID online and download the official e-Aadhaar PDF copy via the myAadhaar portal ({url}). Official statutory fee: ₹{fee:.2f} (Free)."

        # Aadhaar Download
        if "e-Aadhaar" in title or "sub-aadhaar-download" == primary.get("id"):
            return f"To Download your e-Aadhaar digital copy online, visit the official myAadhaar portal at {url}. Statutory fee: ₹{fee:.2f}."

        # Aadhaar Enrolment specific natural explanation
        if "New Aadhaar Enrolment" in title or "sub-aadhaar-enrolment" == primary.get("id"):
            return f"To apply for a new Aadhaar card, physical biometric enrolment is required at an authorized Aadhaar Enrolment Centre. Official statutory fee is ₹{fee:.2f} (Free for fresh enrolment). You can book an appointment at {url}."

        # Driving licence renewal
        if "Driving Licence Renewal" in title or "sub-dl-renewal" == primary.get("id"):
            return f"You can renew your Driving Licence online through the official Parivahan Sarathi portal ({url}). Statutory fee is ₹{fee:.2f} and processing takes approximately {proc_time}."

        # PM Kisan
        if "PM-KISAN" in title or "Annadata Sukhibhava" in title:
            el = primary.get("eligibility", [])
            el_str = "\n".join([f"- {e}" for e in el]) if el else "Small and marginal farmer landholders."
            return f"Under **{title}**, eligible farmers receive financial assistance. Eligibility Criteria:\n{el_str}\nOfficial Source: {url}"

        # Scholarship
        if "Scholarship" in title or "Higher Education" in primary.get("category", ""):
            benefit = primary.get("benefit_amount", "Full tuition fee reimbursement and financial support")
            return f"Under **{title}**, eligible students receive {benefit}. You can apply through the official portal ({url}). Statutory fee: ₹{fee:.2f}."

        if any(w in query.lower() for w in ["document", "documents", "proof", "papers"]) and primary.get("documents"):
            docs = primary.get("documents", [])
            doc_str = ", ".join([d.get("name", "") for d in docs])
            return f"For **{title}**, the Required Documents are: {doc_str}. Official procedure is available via {url}. Statutory fee: ₹{fee:.2f}, Processing time: {proc_time}."

        return f"For **{title}**, the official procedure is available via {url}. Statutory fee: ₹{fee:.2f}, Processing time: {proc_time}."


def get_llm_provider() -> LLMProvider:
    provider_type = os.getenv("LLM_PROVIDER", "").lower()
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if (provider_type == "gemini" or not provider_type) and gemini_key:
        return GeminiProvider(api_key=gemini_key)
    elif provider_type == "openai" and openai_key:
        return OpenAIProvider(api_key=openai_key)
    elif openai_key and not gemini_key:
        return OpenAIProvider(api_key=openai_key)
    elif gemini_key:
        return GeminiProvider(api_key=gemini_key)
    
    return MockProvider()
