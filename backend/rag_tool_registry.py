from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
import re
import models

STOP_WORDS = {"a", "an", "the", "in", "on", "at", "for", "to", "of", "is", "and", "or"}

def clean_query_terms(query: str) -> List[str]:
    """Extract and normalize meaningful alphanumeric keywords."""
    tokens = re.findall(r'[a-zA-Z0-9]+', query.lower())
    cleaned = []
    for t in tokens:
        if t in STOP_WORDS or len(t) < 2:
            continue
        if "scholership" in t:
            cleaned.append("scholarship")
        else:
            cleaned.append(t)
    return cleaned

def get_verified_sub_service(db: Session, sub_service_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single SubService record by ID and returns structured evidence."""
    sub = db.query(models.SubService).filter(models.SubService.id == sub_service_id).first()
    if not sub:
        return None
    parent = sub.parent_service
    return {
        "id": sub.id,
        "service_id": sub.service_id,
        "service_name": parent.official_name if parent else "",
        "sub_service_name": sub.sub_service_name,
        "action_type": sub.action_type,
        "category": parent.category if parent else "",
        "department": parent.department if parent else "",
        "description": sub.description or (parent.description if parent else ""),
        "eligibility": sub.eligibility_criteria or [],
        "documents": sub.required_documents or [],
        "diy_steps": sub.diy_steps or [],
        "official_fee": sub.official_fee,
        "processing_time": sub.processing_time,
        "application_method": sub.application_method,
        "physical_presence": sub.physical_presence_requirement,
        "official_portal_url": sub.official_portal_url,
        "official_source_url": sub.official_source_url,
        "verification_status": sub.confidence_status,
        "last_verified": sub.last_verified,
        "type": "STATUTORY_SERVICE"
    }

def get_verified_information_record(db: Session, record_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single InformationRecord by ID and returns structured evidence."""
    rec = db.query(models.InformationRecord).filter(models.InformationRecord.id == record_id).first()
    if not rec:
        return None
    source = rec.source
    return {
        "id": rec.id,
        "title": rec.title,
        "previous_title": rec.previous_title,
        "historical_names": rec.historical_names or [],
        "description": rec.description,
        "information_type": rec.information_type,
        "category": rec.category,
        "organization": rec.organization,
        "department": rec.department,
        "benefit_amount": rec.benefit_amount_str,
        "application_deadline": rec.application_deadline,
        "eligibility": rec.eligibility_criteria or [],
        "documents": rec.required_documents or [],
        "diy_steps": rec.diy_steps or [],
        "official_fee": rec.official_statutory_fee,
        "official_portal_url": rec.source_url,
        "official_source_url": rec.source_url,
        "source_url": rec.source_url,
        "source_name": source.name if source else rec.organization,
        "source_trust_tier": rec.source_trust_tier,
        "badge_type": rec.badge_type,
        "verification_status": rec.verification_status,
        "last_verified": rec.last_verified,
        "type": "GOVERNMENT_INFORMATION"
    }

def search_verified_services(
    db: Session,
    query: str,
    state_id: str = "AP",
    category: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Searches statutory services and sub-services matching keywords/aliases.
    Deterministic database filtering with state scoping and trust validation.
    """
    q_lower = query.lower()
    q_terms = clean_query_terms(query)
    if not q_terms:
        return []

    sub_services = (
        db.query(models.SubService)
        .join(models.Service)
        .filter(
            or_(
                models.Service.state_scope == "NAT",
                models.Service.state_scope == state_id
            )
        )
        .all()
    )

    scored_results: List[tuple[float, models.SubService]] = []
    for sub in sub_services:
        score = 0.0
        parent = sub.parent_service
        searchable_text = " ".join([
            sub.sub_service_name or "",
            sub.action_type or "",
            parent.official_name or "",
            parent.category or "",
            parent.department or "",
            sub.description or "",
            " ".join(sub.aliases or []),
            " ".join(sub.keywords or []),
            " ".join(parent.aliases or []),
            " ".join(parent.keywords or [])
        ]).lower()

        # Goal specific boosts to disambiguate identical parent services
        if "aadhaar" in searchable_text or "aadhar" in searchable_text:
            if any(w in q_lower for w in ["poyindhi", "poyindi", "lost", "missing", "kanapadakunda", "miss ayyindi", "miss ayindi"]):
                if sub.id == "sub-aadhaar-lost":
                    score += 200.0
            elif any(w in q_lower for w in ["download", "eaadhaar", "pdf copy", "print", "tiskovali"]):
                if sub.id == "sub-aadhaar-download":
                    score += 180.0
            elif any(w in q_lower for w in ["apply", "enrolment", "fresh", "first time", "appply", "kavali"]):
                if sub.id == "sub-aadhaar-enrolment":
                    score += 150.0
            elif any(w in q_lower for w in ["address", "update", "change", "correction"]):
                if sub.id == "sub-aadhaar-address":
                    score += 120.0

        if "driving" in q_lower or "licence" in q_lower or "license" in q_lower or "dl" in q_lower:
            if sub.id == "sub-dl-renewal":
                score += 120.0

        if "voter" in q_lower:
            if sub.id == "sub-voter-lost":
                score += 120.0

        if "pan" in q_lower:
            if any(w in q_lower for w in ["correction", "update", "reprint", "change"]):
                if sub.id == "sub-pan-correction":
                    score += 120.0
            elif sub.id == "sub-pan-new":
                score += 90.0

        if "caste" in q_lower or "community" in q_lower:
            if any(w in q_lower for w in ["duplicate", "download", "copy", "another"]):
                if sub.id == "sub-caste-duplicate":
                    score += 120.0
            elif sub.id == "sub-caste-integrated":
                score += 90.0

        if ("income" in q_lower or "aadhaya" in q_lower) and sub.id == "sub-income-new":
            score += 120.0

        if ("ration" in q_lower or "rice card" in q_lower or "biyyapu" in q_lower) and sub.id == "sub-ration-member-add":
            score += 120.0

        if ("birth" in q_lower or "father" in q_lower) and sub.id == "sub-birth-father-corr":
            score += 120.0

        for term in q_terms:
            if term in searchable_text:
                score += 10.0
                if term in (sub.sub_service_name or "").lower():
                    score += 15.0
                if any(term in str(alias).lower() for alias in (sub.aliases or [])):
                    score += 20.0

        if category and parent and parent.category.lower() == category.lower():
            score += 25.0

        if score > 0:
            scored_results.append((score, sub))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    evidence_list = []
    for _, sub in scored_results[:limit]:
        item = get_verified_sub_service(db, sub.id)
        if item:
            evidence_list.append(item)
    return evidence_list

def search_verified_schemes(
    db: Session,
    query: str,
    state_id: str = "AP",
    category: Optional[str] = None,
    information_type: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Searches government welfare schemes, notifications, benefits, and updates.
    """
    q_lower = query.lower()
    q_terms = clean_query_terms(query)
    
    query_builder = db.query(models.InformationRecord).filter(
        models.InformationRecord.status == "ACTIVE",
        models.InformationRecord.verification_status == "VERIFIED",
        or_(
            models.InformationRecord.state_id == "NAT",
            models.InformationRecord.state_id == state_id
        )
    )

    if information_type:
        query_builder = query_builder.filter(models.InformationRecord.information_type == information_type)
    if category:
        query_builder = query_builder.filter(models.InformationRecord.category == category)

    all_records = query_builder.all()
    if not q_terms:
        return [get_verified_information_record(db, r.id) for r in all_records[:limit] if r]

    scored_records: List[tuple[float, models.InformationRecord, Optional[Dict[str, Any]]]] = []
    for rec in all_records:
        score = 0.0
        predecessor_notice = None
        searchable_text = " ".join([
            rec.title or "",
            rec.previous_title or "",
            rec.description or "",
            rec.category or "",
            rec.organization or "",
            rec.department or "",
            rec.benefit_amount_str or "",
            " ".join(rec.aliases or []),
            " ".join(rec.keywords or []),
            " ".join(rec.historical_names or [])
        ]).lower()

        # Check historical / superseded name match
        hist_names = [rec.previous_title] if rec.previous_title else []
        hist_names.extend(rec.historical_names or [])
        for hname in hist_names:
            if not hname:
                continue
            h_lower = hname.lower()
            if h_lower in q_lower:
                score += 300.0
                predecessor_notice = {
                    "superseded_title": hname,
                    "successor_title": rec.title,
                    "note": f"'{hname}' has been transitioned/superseded by '{rec.title}'."
                }
                break
            elif any(w in h_lower and w in q_lower for w in ["aarogyasri", "rythu bharosa", "vidya deevena", "sunna vaddi", "vasathi deevena"]):
                score += 250.0
                predecessor_notice = {
                    "superseded_title": hname,
                    "successor_title": rec.title,
                    "note": f"'{hname}' has been transitioned/superseded by '{rec.title}'."
                }
                break

        # Check direct alias phrase match
        q_clean_str = re.sub(r'[-/]', ' ', q_lower)
        for alias in (rec.aliases or []):
            al_str = str(alias).lower()
            if al_str in q_clean_str:
                score += 150.0 + 50.0 * len(al_str.split())

        for term in q_terms:
            if term in searchable_text:
                score += 10.0
                if term in (rec.title or "").lower() or (rec.previous_title and term in rec.previous_title.lower()):
                    score += 20.0
                if any(term in str(alias).lower() for alias in (rec.aliases or [])):
                    score += 15.0

        if score > 0:
            scored_records.append((score, rec, predecessor_notice))

    scored_records.sort(key=lambda x: x[0], reverse=True)

    evidence_list = []
    for _, rec, pred in scored_records[:limit]:
        item = get_verified_information_record(db, rec.id)
        if item:
            if pred:
                item["predecessor_notice"] = pred
            evidence_list.append(item)
    return evidence_list

def search_verified_scholarships(
    db: Session,
    query: str,
    state_id: str = "AP",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Specialized retrieval for scholarships across government and corporate sponsors."""
    return search_verified_schemes(
        db=db,
        query=query,
        state_id=state_id,
        category="Higher Education",
        limit=limit
    )

def search_verified_updates(
    db: Session,
    state_id: str = "AP",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Retrieves the latest verified scheme and service updates."""
    records = (
        db.query(models.InformationRecord)
        .filter(
            models.InformationRecord.status == "ACTIVE",
            models.InformationRecord.verification_status == "VERIFIED",
            or_(
                models.InformationRecord.state_id == "NAT",
                models.InformationRecord.state_id == state_id
            )
        )
        .order_by(desc(models.InformationRecord.published_at))
        .limit(limit)
        .all()
    )
    return [get_verified_information_record(db, r.id) for r in records if r]
