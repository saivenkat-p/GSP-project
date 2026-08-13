from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# --- AUTH SCHEMAS ---
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str = "citizen"  # citizen, partner, admin
    phone: Optional[str] = None
    district: Optional[str] = "NTR / Vijayawada"
    state: str = "Andhra Pradesh"

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# --- SERVICE SCHEMAS ---
class ServiceOut(BaseModel):
    id: str
    official_name: str
    state: str
    district: Optional[str] = None
    department: str
    category: str
    description: str
    eligibility_criteria: List[str]
    required_documents: List[Dict[str, Any]]
    diy_steps: List[str]
    official_fee: float
    processing_time: str
    application_method: str
    official_url: str
    source_url: str
    source_last_verified: str
    is_demo_data: bool
    status: str
    key_terms: List[str]

    class Config:
        from_attributes = True

# --- STRICT AI NAVIGATION SCHEMA (Feedback Item #5) ---
class FollowUpQuestion(BaseModel):
    field: str
    question: str
    options: Optional[List[str]] = None

class AIQueryRequest(BaseModel):
    query: str
    state: Optional[str] = "Andhra Pradesh"
    district: Optional[str] = None
    selected_answers: Optional[Dict[str, str]] = Field(default_factory=dict)

class AINavigationResponse(BaseModel):
    intent: str
    confidence: float
    needs_follow_up: bool
    questions: List[FollowUpQuestion] = []
    service: Optional[ServiceOut] = None
    eligibility: List[str] = []
    documents: List[Dict[str, Any]] = []
    official_fee: Optional[float] = None
    processing_time: Optional[str] = None
    official_source: Optional[str] = None
    source_last_verified: Optional[str] = None
    source_status: str = "verified" # "verified" | "demo_data" | "not_found"
    explanation: str
    warnings: List[str] = []

# --- PARTNER SCHEMAS ---
class PartnerOut(BaseModel):
    id: int
    business_name: str
    center_type: str
    verification_status: str
    phone: str
    address: str
    district: str
    state: str
    distance_km: float
    rating: float
    reviews_count: int
    badge_label: str
    partner_assistance_fee: float
    supported_service_ids: List[str]

    class Config:
        from_attributes = True

# --- SERVICE REQUEST & STATUS TIMELINE SCHEMAS ---
class ServiceRequestCreate(BaseModel):
    service_id: str
    partner_id: Optional[int] = None
    notes: Optional[str] = None

class ServiceRequestOut(BaseModel):
    id: int
    citizen_id: int
    service_id: str
    partner_id: Optional[int]
    status: str
    status_notes: Optional[str]
    official_application_no: Optional[str]
    citizen_district: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    service: Optional[ServiceOut]
    partner: Optional[PartnerOut]

    class Config:
        from_attributes = True

# --- REJECTION DIAGNOSTIC SCHEMAS ---
class RejectionDiagnosticOut(BaseModel):
    id: int
    service_request_id: int
    rejection_reason: str
    simple_explanation: str
    what_went_wrong: str
    corrective_actions: List[str]
    required_replacement_documents: List[str]
    can_reapply: bool
    needs_legal_help: bool
    official_reapplication_url: Optional[str]
    verified_info: str

    class Config:
        from_attributes = True
