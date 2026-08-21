from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import models

# Strict Trust Hierarchy Definitions
TRUST_TIER_1_PRIMARY_OFFICIAL = 1  # State / Central Govt, UIDAI, Parivahan, Income Tax, MeeSeva
TRUST_TIER_2_GOVT_AGGREGATORS = 2  # India.gov.in, National Portals
TRUST_TIER_3_ORG_OFFICIAL = 3     # LIC, Corporate Foundations, Universities, NGOs
TRUST_TIER_4_DISCOVERY_NEWS = 4   # News & Unofficial discovery feeds

def get_active_sources(db: Session, tier_filter: Optional[int] = None) -> List[models.InformationSource]:
    """
    Returns active registered information sources, optionally filtered by trust tier.
    """
    query = db.query(models.InformationSource).filter(models.InformationSource.active == True)
    if tier_filter is not None:
        query = query.filter(models.InformationSource.trust_tier == tier_filter)
    return query.all()

def register_information_source(
    source_id: str,
    name: str,
    organization: str,
    source_type: str,
    source_priority: str,
    trust_tier: int,
    base_url: str,
    official_url: str,
    state_scope: str,
    department: str,
    db: Session,
    check_frequency_hours: int = 24,
    robots_allowed: bool = True
) -> models.InformationSource:
    """
    Registers or updates an official Information Source with strict trust classification.
    """
    existing = db.query(models.InformationSource).filter(models.InformationSource.id == source_id).first()
    if existing:
        existing.name = name
        existing.organization = organization
        existing.source_type = source_type
        existing.source_priority = source_priority
        existing.trust_tier = trust_tier
        existing.base_url = base_url
        existing.official_url = official_url
        existing.state_scope = state_scope
        existing.department = department
        existing.check_frequency_hours = check_frequency_hours
        existing.robots_allowed = robots_allowed
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    new_source = models.InformationSource(
        id=source_id,
        name=name,
        organization=organization,
        source_type=source_type,
        source_priority=source_priority,
        trust_tier=trust_tier,
        base_url=base_url,
        official_url=official_url,
        state_scope=state_scope,
        department=department,
        active=True,
        last_checked=datetime.utcnow().strftime("%Y-%m-%d"),
        last_successful_fetch=datetime.utcnow().strftime("%Y-%m-%d"),
        check_frequency_hours=check_frequency_hours,
        robots_allowed=robots_allowed
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source
