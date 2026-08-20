from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- LOCATION SCHEMAS ---
class LocalityOut(BaseModel):
    id: str
    name: str
    pincode: Optional[str] = None
    class Config:
        from_attributes = True

class MandalOut(BaseModel):
    id: str
    name: str
    localities: List[LocalityOut] = []
    class Config:
        from_attributes = True

class DistrictOut(BaseModel):
    id: str
    name: str
    mandals: List[MandalOut] = []
    class Config:
        from_attributes = True

class StateOut(BaseModel):
    id: str
    name: str
    districts: List[DistrictOut] = []
    class Config:
        from_attributes = True

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str = "CITIZEN"  # CITIZEN, PARTNER, STAFF, ADMIN
    phone: Optional[str] = None
    state_id: str = "AP"
    district_id: str = "AP-NTR"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# --- SERVICE INTELLIGENCE RECORD SCHEMAS ---
class SubServiceOut(BaseModel):
    id: str
    service_id: str
    sub_service_name: str
    action_type: str
    aliases: List[str] = []
    keywords: List[str] = []
    description: Optional[str] = None
    eligibility_criteria: List[str] = []
    required_documents: List[Dict[str, Any]] = []
    diy_steps: List[str] = []
    official_fee: float
    processing_time: str
    application_method: str
    physical_presence_requirement: str  # NOT_REQUIRED | MAY_BE_REQUIRED | REQUIRED
    physical_presence_reason: Optional[str] = None
    official_portal_url: str
    official_source_url: str
    information_version: str = "V1.0"
    last_checked: str
    last_verified: str
    confidence_status: str  # VERIFIED | VERIFICATION_PENDING | OUTDATED
    required_certification_code: str
    is_demo_data: bool

    class Config:
        from_attributes = True

class ServiceIntelligenceOut(BaseModel):
    id: str
    official_name: str
    category: str
    state_scope: str = "AP"
    district_scope: str = "ALL"
    department: str
    description: str
    aliases: List[str] = []
    keywords: List[str] = []
    verification_status: str = "VERIFIED"
    last_verified: str = "2026-08-20"
    sub_services: List[SubServiceOut] = []

    class Config:
        from_attributes = True

# --- GROUNDED AI CHAT & NAVIGATION SCHEMAS ---
class FollowUpQuestion(BaseModel):
    field: str
    question: str
    options: Optional[List[str]] = None

class AIChatRequest(BaseModel):
    session_id: Optional[str] = "session-default"
    query: str
    state_id: Optional[str] = "AP"
    district_id: Optional[str] = "AP-NTR"
    mandal_name: Optional[str] = "Vijayawada Urban"
    selected_answers: Optional[Dict[str, str]] = Field(default_factory=dict)

class AINavigationResponse(BaseModel):
    session_id: str
    intent: str
    confidence: float
    needs_follow_up: bool
    questions: List[FollowUpQuestion] = []
    service: Optional[ServiceIntelligenceOut] = None
    resolved_sub_service: Optional[SubServiceOut] = None
    candidate_suggestions: List[Dict[str, Any]] = []
    eligibility: List[str] = []
    documents: List[Dict[str, Any]] = []
    official_fee: Optional[float] = None
    gsp_assistance_fee: Optional[float] = None
    processing_time: Optional[str] = None
    physical_presence: Optional[str] = None
    official_source: Optional[str] = None
    source_last_verified: Optional[str] = None
    confidence_status: str = "VERIFIED" # VERIFIED | VERIFICATION_PENDING | OUTDATED | NOT_FOUND
    explanation: str
    warnings: List[str] = []

# --- LEAD & SERVICE REQUEST SCHEMAS ---
class ServiceRequestCreate(BaseModel):
    sub_service_id: str
    assistance_tier: str = "LEVEL_B_FORM_HELP" # LEVEL_A_DIY | LEVEL_B_FORM_HELP | LEVEL_C_PROCESS_HELP | LEVEL_D_FULL_HELP
    citizen_location_str: Optional[str] = "Vijayawada, NTR District (AP)"
    notes: Optional[str] = None
    callback_requested: bool = True

class ServiceRequestOut(BaseModel):
    id: int
    citizen_id: int
    sub_service_id: str
    partner_id: Optional[int]
    staff_id: Optional[int]
    assistance_tier: str
    status: str
    citizen_location_str: str
    official_application_no: Optional[str]
    notes: Optional[str]
    callback_requested: bool
    official_statutory_fee: float
    gsp_assistance_fee: float
    partner_commission: float
    created_at: datetime
    updated_at: datetime
    sub_service: Optional[SubServiceOut]

    class Config:
        from_attributes = True

# --- PARTNER & TRAINING SCHEMAS ---
class PartnerProfileOut(BaseModel):
    id: int
    business_name: str
    center_type: str
    verification_status: str
    phone: str
    address: str
    district_id: str
    mandal_name: str
    distance_km: float
    rating: float
    reviews_count: int
    badge_label: str
    partner_assistance_fee: float

    class Config:
        from_attributes = True
