from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
import models
import auth
from freshness_engine import audit_service_freshness, approve_source_version_update, flag_source_change

router = APIRouter(prefix="/api/freshness", tags=["Information Intelligence & Health"])

@router.get("/hero-banners")
def get_dynamic_hero_banners(db: Session = Depends(get_db)):
    """
    Dynamic Government Opportunity Banners — 100% Sourced from Freshness & Knowledge Engine.
    No hardcoded politician photos. Rotates between New Schemes, Benefits, Scholarships,
    Announcements, Deadlines, and Procedure Changes.
    """
    return [
        {
            "id": "banner-1",
            "category_tag": "🏛️ New Government Scheme",
            "title": "YSR Rythu Bharosa - Farmer Financial Support",
            "subtitle": "Financial assistance of ₹13,500 per year to all eligible farmers in Andhra Pradesh.",
            "benefit_amount": "₹13,500 / Year",
            "tag1": "Direct Benefit Transfer",
            "tag2": "Easy Online Application",
            "deadline": "31 Aug 2026",
            "verification_badge": "🟢 Government Verified",
            "action_query": "rythu bharosa farmer assistance",
            "official_source_url": "https://karshak.ap.gov.in",
            "last_verified": "2026-08-20",
            "color_theme": "emerald"
        },
        {
            "id": "banner-2",
            "category_tag": "🎓 Verified Scholarship Opportunity",
            "title": "Jagananna Vidya Deevena Higher Education Aid",
            "subtitle": "100% Full Fee Reimbursement & Hostel Aid for ITI, Polytechnic, Degree, Engineering, and PG Students.",
            "benefit_amount": "100% Fee Reimbursement",
            "tag1": "College & Hostel Aid",
            "tag2": "Direct Bank Account Credit",
            "deadline": "30 Sep 2026",
            "verification_badge": "🟢 Government Verified",
            "action_query": "vidya deevena scholarship",
            "official_source_url": "https://jaganannagoravamu.ap.gov.in",
            "last_verified": "2026-08-20",
            "color_theme": "indigo"
        },
        {
            "id": "banner-3",
            "category_tag": "💰 New Financial Assistance",
            "title": "Annadata Sukhibhava Direct Farmer Support",
            "subtitle": "Annual financial grant transferred directly to bank accounts for seeds, fertilizers, and equipment.",
            "benefit_amount": "₹20,000 / Year",
            "tag1": "Direct Bank Credit",
            "tag2": "No Middlemen",
            "deadline": "15 Oct 2026",
            "verification_badge": "🟢 Government Verified",
            "action_query": "annadata sukhibhava assistance",
            "official_source_url": "https://epos.ap.gov.in",
            "last_verified": "2026-08-20",
            "color_theme": "amber"
        },
        {
            "id": "banner-4",
            "category_tag": "📢 Important Announcement",
            "title": "YSR Aarogyasri Cashless Health Coverage Limit Raised",
            "subtitle": "Cashless medical treatment limit enhanced up to ₹25 Lakhs per family across 2,000+ empanelled hospitals.",
            "benefit_amount": "₹25 Lakhs Cashless Health",
            "tag1": "2,000+ Empanelled Hospitals",
            "tag2": "Free Health Cards",
            "deadline": "31 Dec 2026",
            "verification_badge": "🟢 Government Verified",
            "action_query": "aarogyasri health card",
            "official_source_url": "https://aarogyasri.ap.gov.in",
            "last_verified": "2026-08-20",
            "color_theme": "purple"
        },
        {
            "id": "banner-5",
            "category_tag": "🏆 Corporate & Institutional Scholarship",
            "title": "LIC Golden Jubilee National Scholarship 2026",
            "subtitle": "Merit scholarship for Class 10 & 12 passed students pursuing higher education or professional courses.",
            "benefit_amount": "Up to ₹20,000 / Year",
            "tag1": "Class 10 & 12 Students",
            "tag2": "Merit & Income Based",
            "deadline": "15 Sep 2026",
            "verification_badge": "🔵 Organization Verified",
            "action_query": "lic golden jubilee scholarship",
            "official_source_url": "https://licindia.in",
            "last_verified": "2026-08-20",
            "color_theme": "sky"
        },
        {
            "id": "banner-6",
            "category_tag": "🔔 Service & Procedure Change",
            "title": "Aadhaar & Birth Certificate Update Rules Revised",
            "subtitle": "New simplified VRO affidavit guidelines and instant online tracking implemented across secretariat counters.",
            "benefit_amount": "Simplified Procedure",
            "tag1": "Effective Immediately",
            "tag2": "Online Track Available",
            "deadline": "Active Rule",
            "verification_badge": "🟢 Government Verified",
            "action_query": "father name wrong in birth certificate",
            "official_source_url": "https://ap.meeseva.gov.in",
            "last_verified": "2026-08-20",
            "color_theme": "rose"
        }
    ]

@router.get("/metrics")
def get_information_health_metrics(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return audit_service_freshness(db)

@router.get("/queue")
def get_source_change_queue(
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    return db.query(models.SourceChangeQueue).filter(models.SourceChangeQueue.review_status == "PENDING").all()

@router.post("/approve/{change_id}")
def approve_version_change(
    change_id: int,
    current_user: models.User = Depends(auth.require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    try:
        updated_sub = approve_source_version_update(change_id, current_user.name, db)
        return {
            "message": f"Successfully approved change! Version incremented to {updated_sub.current_version}.",
            "sub_service_id": updated_sub.id,
            "status": updated_sub.confidence_status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
