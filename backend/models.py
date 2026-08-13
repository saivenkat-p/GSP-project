from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="citizen")  # "citizen", "partner", "admin"
    phone = Column(String, nullable=True)
    district = Column(String, nullable=True, default="NTR / Vijayawada")
    state = Column(String, nullable=False, default="Andhra Pradesh")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    partner_profile = relationship("Partner", back_populates="user", uselist=False)
    service_requests = relationship("ServiceRequest", back_populates="citizen")

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True, index=True)  # e.g., "ap-income-certificate"
    official_name = Column(String, nullable=False)
    state = Column(String, nullable=False, default="Andhra Pradesh")
    district = Column(String, nullable=True)  # Null if state-wide
    department = Column(String, nullable=False)
    category = Column(String, nullable=False)  # "Revenue", "Civil Supplies", "Transport", "Land Records", "Social Welfare"
    description = Column(Text, nullable=False)
    eligibility_criteria = Column(JSON, nullable=False)  # List of strings
    required_documents = Column(JSON, nullable=False)    # List of document requirement objects
    diy_steps = Column(JSON, nullable=False)             # List of step-by-step DIY guide strings
    official_fee = Column(Float, nullable=False, default=50.0)
    processing_time = Column(String, nullable=False, default="7 Working Days")
    application_method = Column(String, nullable=False, default="Online via MeeSeva Portal / Village Secretariat")
    official_url = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    source_last_verified = Column(String, nullable=False)  # e.g., "2026-08-10"
    is_demo_data = Column(Boolean, default=False)
    status = Column(String, default="active")              # "active", "under_review"
    key_terms = Column(JSON, nullable=False)               # List of keywords for search & intent matching

class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False)
    center_type = Column(String, nullable=False) # e.g. "MeeSeva Authorized Center", "CSC Digital Seva Kendra"
    verification_status = Column(String, default="verified") # "verified", "pending", "rejected"
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    district = Column(String, nullable=False, default="NTR / Vijayawada")
    state = Column(String, nullable=False, default="Andhra Pradesh")
    distance_km = Column(Float, default=1.2)
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=34)
    badge_label = Column(String, default="Verified Partner 🛡️")
    partner_assistance_fee = Column(Float, default=100.0)
    supported_service_ids = Column(JSON, nullable=False) # List of service IDs handled

    user = relationship("User", back_populates="partner_profile")
    service_requests = relationship("ServiceRequest", back_populates="partner")

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(String, ForeignKey("services.id"), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    status = Column(String, default="requirement_identified") 
    # Steps: "requirement_identified" -> "documents_prepared" -> "submitted_to_official_portal" -> "government_verification" -> "certificate_generated" | "rejected"
    status_notes = Column(Text, nullable=True)
    official_application_no = Column(String, nullable=True)
    citizen_district = Column(String, nullable=False, default="NTR / Vijayawada")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citizen = relationship("User", back_populates="service_requests")
    service = relationship("Service")
    partner = relationship("Partner", back_populates="service_requests")
    rejection_details = relationship("RejectionDiagnostic", back_populates="service_request", uselist=False)

class RejectionDiagnostic(Base):
    __tablename__ = "rejection_diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=False)
    rejection_reason = Column(Text, nullable=False)
    simple_explanation = Column(Text, nullable=False)
    what_went_wrong = Column(Text, nullable=False)
    corrective_actions = Column(JSON, nullable=False) # List of steps
    required_replacement_documents = Column(JSON, nullable=False) # List of documents
    can_reapply = Column(Boolean, default=True)
    needs_legal_help = Column(Boolean, default=False)
    official_reapplication_url = Column(String, nullable=True)
    verified_info = Column(Text, nullable=False)

    service_request = relationship("ServiceRequest", back_populates="rejection_details")
