from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# --- LOCATION HIERARCHY MODELS ---
class State(Base):
    __tablename__ = "states"

    id = Column(String, primary_key=True, index=True)  # e.g., "AP", "TS", "NAT"
    name = Column(String, nullable=False, unique=True)
    districts = relationship("District", back_populates="state")

class District(Base):
    __tablename__ = "districts"

    id = Column(String, primary_key=True, index=True)  # e.g., "AP-NTR", "AP-VSKP"
    state_id = Column(String, ForeignKey("states.id"), nullable=False)
    name = Column(String, nullable=False)
    state = relationship("State", back_populates="districts")
    mandals = relationship("Mandal", back_populates="district")

class Mandal(Base):
    __tablename__ = "mandals"

    id = Column(String, primary_key=True, index=True)  # e.g., "AP-NTR-VJA"
    district_id = Column(String, ForeignKey("districts.id"), nullable=False)
    name = Column(String, nullable=False)
    district = relationship("District", back_populates="mandals")
    localities = relationship("VillageLocality", back_populates="mandal")

class VillageLocality(Base):
    __tablename__ = "village_localities"

    id = Column(String, primary_key=True, index=True)
    mandal_id = Column(String, ForeignKey("mandals.id"), nullable=False)
    name = Column(String, nullable=False)
    pincode = Column(String, nullable=True)
    mandal = relationship("Mandal", back_populates="localities")

class GovernmentOffice(Base):
    __tablename__ = "government_offices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g. "Tahsildar Office, Vijayawada Central"
    office_type = Column(String, nullable=False)  # e.g. "Tahsildar / Revenue", "MeeSeva Center", "Sub-Registrar (SRO)", "RTO Office"
    district_id = Column(String, ForeignKey("districts.id"), nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    working_hours = Column(String, default="10:00 AM - 05:00 PM (Mon-Sat)")


# --- USER & ROLE MODELS ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="CITIZEN")  # "CITIZEN", "PARTNER", "STAFF", "ADMIN"
    phone = Column(String, nullable=True)
    state_id = Column(String, nullable=False, default="AP")
    district_id = Column(String, nullable=False, default="AP-NTR")
    mandal_name = Column(String, nullable=True, default="Vijayawada Urban")
    created_at = Column(DateTime, default=datetime.utcnow)

    partner_profile = relationship("PartnerProfile", back_populates="user", uselist=False)
    staff_profile = relationship("StaffProfile", back_populates="user", uselist=False)
    service_requests = relationship("ServiceRequest", back_populates="citizen", foreign_keys="[ServiceRequest.citizen_id]")


# --- SERVICE INTELLIGENCE KNOWLEDGE BASE MODELS ---
class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, index=True)  # e.g. "srv-birth-cert"
    official_name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # "Certificates", "Revenue", "Land Records", "Transport", "Civil Supplies", "Identity"
    department = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    # Location Scope
    state_scope = Column(String, ForeignKey("states.id"), nullable=False, default="AP")
    district_scope = Column(String, nullable=False, default="ALL")
    
    # Aliases & Keywords JSON Array (Data-Driven Search Engine)
    aliases = Column(JSON, nullable=False, default=[])
    keywords = Column(JSON, nullable=False, default=[])

    # Governance & Verification Status
    verification_status = Column(String, nullable=False, default="VERIFIED") # VERIFIED | VERIFICATION_PENDING | UNVERIFIED_DEMO
    last_verified = Column(String, nullable=False, default="2026-08-20")

    # Sub-services relationship
    sub_services = relationship("SubService", back_populates="parent_service")

class SubService(Base):
    __tablename__ = "sub_services"

    id = Column(String, primary_key=True, index=True)  # e.g. "srv-birth-father-name-correction"
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    sub_service_name = Column(String, nullable=False)  # e.g. "Father's Name Correction"
    action_type = Column(String, nullable=False)  # "Correction", "New Application", "Renewal", "Duplicate", "Download"
    
    # Data-Driven Search Aliases & Keywords
    aliases = Column(JSON, nullable=False, default=[])
    keywords = Column(JSON, nullable=False, default=[])
    description = Column(Text, nullable=True)

    # Service Intelligence Attributes
    eligibility_criteria = Column(JSON, nullable=False, default=[])  # List of eligibility rules
    required_documents = Column(JSON, nullable=False, default=[])    # List of document requirement objects
    diy_steps = Column(JSON, nullable=False, default=[])             # Step-by-step procedure strings
    official_fee = Column(Float, nullable=False, default=50.0)
    processing_time = Column(String, nullable=False, default="7 Working Days")
    application_method = Column(String, nullable=False, default="Online via Official Portal / Local Secretariat")
    
    # Physical Presence Requirement: "NOT_REQUIRED" | "MAY_BE_REQUIRED" | "REQUIRED"
    physical_presence_requirement = Column(String, nullable=False, default="MAY_BE_REQUIRED")
    physical_presence_reason = Column(Text, nullable=True)
    
    official_portal_url = Column(String, nullable=False, default="https://ap.meeseva.gov.in")
    official_source_url = Column(String, nullable=False, default="https://ap.meeseva.gov.in")
    
    # Freshness, Versioning & Verification Status
    information_version = Column(String, nullable=False, default="V1.0")
    last_checked = Column(String, nullable=False, default="2026-08-20")
    last_verified = Column(String, nullable=False, default="2026-08-20")
    confidence_status = Column(String, nullable=False, default="VERIFIED")  # "VERIFIED" | "VERIFICATION_PENDING" | "OUTDATED"
    
    # Required Partner Certification ID to handle this sub-service
    required_certification_code = Column(String, nullable=False, default="CERT-CIVIL-GEN")
    
    is_demo_data = Column(Boolean, default=False)

    parent_service = relationship("Service", back_populates="sub_services")
    service_requests = relationship("ServiceRequest", back_populates="sub_service")
    version_history = relationship("ServiceVersion", back_populates="sub_service")

class ServiceVersion(Base):
    __tablename__ = "service_versions"

    id = Column(Integer, primary_key=True, index=True)
    sub_service_id = Column(String, ForeignKey("sub_services.id"), nullable=False)
    version_code = Column(String, nullable=False)  # "V1.0", "V2.0"
    changes_summary = Column(Text, nullable=False)
    snapshot_json = Column(JSON, nullable=False)
    approved_by_admin = Column(String, nullable=False, default="System Admin")
    created_at = Column(DateTime, default=datetime.utcnow)

    sub_service = relationship("SubService", back_populates="version_history")

class SourceChangeQueue(Base):
    __tablename__ = "source_change_queue"

    id = Column(Integer, primary_key=True, index=True)
    sub_service_id = Column(String, ForeignKey("sub_services.id"), nullable=False)
    source_url = Column(String, nullable=False)
    detected_change_summary = Column(Text, nullable=False)
    diff_data = Column(JSON, nullable=False)
    review_status = Column(String, default="PENDING")  # "PENDING", "APPROVED", "REJECTED"
    created_at = Column(DateTime, default=datetime.utcnow)


# --- PARTNER & TRAINING CERTIFICATION MODELS ---
class PartnerProfile(Base):
    __tablename__ = "partner_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False)
    center_type = Column(String, nullable=False)  # "MeeSeva Authorized Partner", "CSC Kendra Operator"
    verification_status = Column(String, default="VERIFIED")  # "VERIFIED", "PENDING", "REJECTED"
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    district_id = Column(String, nullable=False, default="AP-NTR")
    mandal_name = Column(String, nullable=False, default="Vijayawada Urban")
    distance_km = Column(Float, default=1.2)
    rating = Column(Float, default=4.9)
    reviews_count = Column(Integer, default=32)
    badge_label = Column(String, default="GSP Verified Partner 🛡️")
    partner_assistance_fee = Column(Float, default=100.0)

    user = relationship("User", back_populates="partner_profile")
    certifications = relationship("PartnerCertification", back_populates="partner")
    assigned_requests = relationship("ServiceRequest", back_populates="partner")

class TrainingCourse(Base):
    __tablename__ = "training_courses"

    id = Column(String, primary_key=True, index=True)
    certification_code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    modules_json = Column(JSON, nullable=False)
    passing_score = Column(Integer, default=80)

class PartnerCertification(Base):
    __tablename__ = "partner_certifications"

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey("partner_profiles.id"), nullable=False)
    certification_code = Column(String, nullable=False)
    passed_at = Column(DateTime, default=datetime.utcnow)
    score = Column(Integer, nullable=False, default=90)

    partner = relationship("PartnerProfile", back_populates="certifications")


# --- STAFF & LEAD / SERVICE REQUEST MODELS ---
class StaffProfile(Base):
    __tablename__ = "staff_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_code = Column(String, nullable=False, unique=True)
    department_assigned = Column(String, default="Citizen Assistance Desk")

    user = relationship("User", back_populates="staff_profile")

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sub_service_id = Column(String, ForeignKey("sub_services.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partner_profiles.id"), nullable=True)
    staff_id = Column(Integer, ForeignKey("staff_profiles.id"), nullable=True)
    
    # Assistance Tier: "LEVEL_A_DIY" | "LEVEL_B_FORM_HELP" | "LEVEL_C_PROCESS_HELP" | "LEVEL_D_FULL_HELP"
    assistance_tier = Column(String, default="LEVEL_B_FORM_HELP")
    
    # 14 Lead Statuses Workflow:
    status = Column(String, default="NEW")
    
    citizen_location_str = Column(String, nullable=False, default="Vijayawada, NTR District (AP)")
    official_application_no = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    callback_requested = Column(Boolean, default=True)
    scheduled_callback_time = Column(String, nullable=True)
    
    # Fees Breakdown
    official_statutory_fee = Column(Float, default=50.0)
    gsp_assistance_fee = Column(Float, default=100.0)
    partner_commission = Column(Float, default=70.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citizen = relationship("User", back_populates="service_requests", foreign_keys=[citizen_id])
    sub_service = relationship("SubService", back_populates="service_requests")
    partner = relationship("PartnerProfile", back_populates="assigned_requests")
    rejection_details = relationship("RejectionDiagnostic", back_populates="service_request", uselist=False)
    notes_history = relationship("RequestNote", back_populates="service_request")

class RequestNote(Base):
    __tablename__ = "request_notes"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    author_name = Column(String, nullable=False)
    author_role = Column(String, nullable=False)  # "STAFF", "PARTNER", "CITIZEN"
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    service_request = relationship("ServiceRequest", back_populates="notes_history")

class RejectionDiagnostic(Base):
    __tablename__ = "rejection_diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    rejection_reason = Column(Text, nullable=False)
    simple_explanation = Column(Text, nullable=False)
    what_went_wrong = Column(Text, nullable=False)
    corrective_actions = Column(JSON, nullable=False)
    required_replacement_documents = Column(JSON, nullable=False)
    can_reapply = Column(Boolean, default=True)
    needs_legal_help = Column(Boolean, default=False)
    verified_info = Column(Text, nullable=False)

    service_request = relationship("ServiceRequest", back_populates="rejection_details")
