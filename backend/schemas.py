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

# --- V3 SOURCE REGISTRY SCHEMAS ---
class InformationSourceOut(BaseModel):
    id: str
    name: str
    organization: str
    source_type: str
    source_priority: str
    trust_tier: int
    base_url: str
    official_url: str
    state_scope: str
    department: str
    active: bool
    last_checked: str
    last_successful_fetch: str
    check_frequency_hours: int
    robots_allowed: bool

    class Config:
        from_attributes = True

# --- V3 INFORMATION RECORD SCHEMAS ---
class InformationVersionHistoryOut(BaseModel):
    id: int
    record_id: str
    version_code: str
    title_snapshot: str
    previous_title_snapshot: Optional[str] = None
    benefit_snapshot: Optional[str] = None
    deadline_snapshot: Optional[str] = None
    eligibility_snapshot: Optional[Any] = None
    change_summary: str
    diff_json: Dict[str, Any]
    approved_by_admin: str
    official_effective_date: str
    created_at: datetime

    class Config:
        from_attributes = True

class InformationRecordOut(BaseModel):
    id: str
    title: str
    previous_title: Optional[str] = None
    description: str
    information_type: str
    category: str
    organization: str
    department: str
    state_id: str
    district_id: Optional[str] = "ALL"
    mandal_id: Optional[str] = "ALL"
    source_id: Optional[str] = None
    source_url: str
    published_at: str
    effective_from: str
    effective_until: Optional[str] = None
    application_start: Optional[str] = None
    application_deadline: Optional[str] = None
    benefit_amount_str: Optional[str] = None
    eligibility_criteria: List[str] = []
    required_documents: List[Dict[str, Any]] = []
    diy_steps: List[str] = []
    official_statutory_fee: float = 0.0
    gsp_assistance_fee: float = 150.0
    partner_fee: float = 100.0
    status: str
    verification_status: str  # VERIFIED, VERIFICATION_PENDING, OUTDATED, SUPERSEDED, REJECTED
    badge_type: str  # GOVERNMENT_VERIFIED, ORGANIZATION_VERIFIED, PENDING_VERIFICATION
    source_trust_tier: int
    version: str
    previous_version_id: Optional[str] = None
    current_version_id: Optional[str] = None
    content_hash: Optional[str] = None
    last_checked: str
    aliases: List[str] = []
    historical_names: List[str] = []
    keywords: List[str] = []
    superseded_by_id: Optional[str] = None
    is_demo_data: bool = False
    banner_priority: int = 10
    is_promotional: bool = True
    color_theme: str = "emerald"

    class Config:
        from_attributes = True

class OfficialProfileOut(BaseModel):
    id: str
    name: str
    designation: str
    department: str
    state_id: str
    district_id: Optional[str] = None
    photo_url: Optional[str] = None
    official_source_url: str
    verification_status: str
    last_verified: str
    effective_from: str
    effective_until: Optional[str] = None

    class Config:
        from_attributes = True

class AdminAuditLogOut(BaseModel):
    id: int
    admin_username: str
    action_type: str
    record_type: str
    record_id: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    source_url: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

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
    current_version: str = "V1.0"
    last_checked: str
    last_verified: str
    confidence_status: str  # VERIFIED | VERIFICATION_PENDING | OUTDATED | SUPERSEDED
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
    last_verified: str = "2026-08-21"
    sub_services: List[SubServiceOut] = []

    class Config:
        from_attributes = True

class TaxonomySummaryOut(BaseModel):
    total_categories: int
    total_services: int
    total_sub_services: int
    total_verified_records: int
    categories: List[str]

# --- GROUNDED AI CHAT & NAVIGATION SCHEMAS ---
class AIChatRequest(BaseModel):
    session_id: Optional[str] = "session-default"
    query: str
    state_id: Optional[str] = "AP"
    district_id: Optional[str] = "AP-NTR"
    mandal_name: Optional[str] = "Vijayawada Urban"
    selected_answers: Optional[Dict[str, str]] = None

class FollowUpQuestion(BaseModel):
    field: str
    question: str
    options: List[str]

class CandidateSuggestion(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None

class AINavigationResponse(BaseModel):
    mode: str = "CONVERSATIONAL"  # CONVERSATIONAL | GENERAL_AI | GOVERNMENT_GROUNDED
    source_status: Optional[str] = None  # VERIFIED | VERIFICATION_PENDING | NOT_FOUND | null
    sources: List[Dict[str, Any]] = []
    service: Optional[SubServiceOut] = None
    intent: str
    confidence: float = 1.0
    confidence_status: str = "VERIFIED"  # VERIFIED | VERIFICATION_PENDING | NOT_FOUND | SUPERSEDED
    explanation: str
    needs_follow_up: bool = False
    questions: List[FollowUpQuestion] = []
    resolved_sub_service: Optional[SubServiceOut] = None
    resolved_information_record: Optional[InformationRecordOut] = None
    historical_superseded_notice: Optional[Dict[str, Any]] = None
    candidate_suggestions: List[CandidateSuggestion] = []
    documents: List[Dict[str, Any]] = []
    eligibility: List[str] = []
    official_fee: float = 0.0
    source_last_verified: Optional[str] = "2026-08-21"
    warnings: List[str] = []

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

class TrainingCourseOut(BaseModel):
    id: str
    certification_code: str
    title: str
    category: str
    description: str
    modules_json: List[Dict[str, Any]]
    passing_score: int

    class Config:
        from_attributes = True

# --- SERVICE REQUEST & LEAD SCHEMAS ---
class RequestNoteOut(BaseModel):
    id: int
    author_name: str
    author_role: str
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceRequestOut(BaseModel):
    id: int
    citizen_id: int
    sub_service_id: Optional[str] = None
    partner_id: Optional[int] = None
    staff_id: Optional[int] = None
    assistance_tier: str
    status: str
    citizen_location_str: str
    official_application_no: Optional[str] = None
    notes: Optional[str] = None
    callback_requested: bool
    scheduled_callback_time: Optional[str] = None
    official_statutory_fee: float
    gsp_assistance_fee: float
    partner_commission: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    sub_service: Optional[SubServiceOut] = None
    partner: Optional[PartnerProfileOut] = None
    notes_history: List[RequestNoteOut] = []

    class Config:
        from_attributes = True

class ServiceRequestCreate(BaseModel):
    sub_service_id: Optional[str] = None
    information_record_id: Optional[str] = None
    assistance_tier: str = "LEVEL_B_FORM_HELP"
    citizen_location_str: str
    notes: Optional[str] = None
    callback_requested: bool = True

class CallbackRequestCreate(BaseModel):
    citizen_name: str
    phone: str
    service_needed: Optional[str] = "General Government Service Guidance"
    preferred_time: Optional[str] = "Within 30 Minutes"
    location_str: Optional[str] = "Vijayawada, NTR District (AP)"
    requirement_notes: Optional[str] = None

class LeadStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    official_application_no: Optional[str] = None
    partner_id: Optional[int] = None
