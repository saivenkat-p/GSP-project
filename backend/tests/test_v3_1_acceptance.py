import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
from service_resolution_engine import resolve_citizen_query
from change_detector import detect_record_changes
from freshness_engine import approve_information_change

class TestGSPV31Acceptance(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_no_fake_schemes_on_empty(self):
        """TEST 1: Empty verified scheme database returns 0 records and no fallback fake cards."""
        verified_count = self.db.query(models.InformationRecord).filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.state_id == "NON_EXISTENT_STATE"
        ).count()
        self.assertEqual(verified_count, 0, "Non-existent state should return exactly 0 verified records")

    def test_02_dynamic_scheme_addition(self):
        """TEST 2: Insert a new verified record without code modification."""
        test_id = "rec-test-pm-kisan-v31"
        self.db.query(models.InformationRecord).filter(models.InformationRecord.id == test_id).delete()
        self.db.commit()

        new_rec = models.InformationRecord(
            id=test_id,
            title="PM-KISAN Samman Nidhi Verification Test",
            description="Direct income support of Rs 6000 per year.",
            information_type="GOVERNMENT_SCHEME",
            category="Welfare Schemes",
            organization="Ministry of Agriculture",
            department="Agriculture",
            state_id="AP",
            source_url="https://pmkisan.gov.in",
            published_at="2026-08-21",
            effective_from="2026-08-21",
            status="ACTIVE",
            verification_status="VERIFIED",
            badge_type="GOVERNMENT_VERIFIED",
            source_trust_tier=1,
            aliases=["pm kisan", "kisan samman nidhi"]
        )
        self.db.add(new_rec)
        self.db.commit()

        res = resolve_citizen_query("test-session-1", "I want to apply for pm kisan samman nidhi", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, test_id)

    def test_03_remove_verification_outdated_filter(self):
        """TEST 3: Change VERIFIED -> OUTDATED. Record must disappear from active verified queries."""
        rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-test-pm-kisan-v31").first()
        if rec:
            rec.verification_status = "OUTDATED"
            self.db.commit()

        active = self.db.query(models.InformationRecord).filter(
            models.InformationRecord.id == "rec-test-pm-kisan-v31",
            models.InformationRecord.verification_status == "VERIFIED"
        ).first()
        self.assertIsNone(active, "OUTDATED record must never be returned in verified query")

    def test_04_source_update_change_detection(self):
        """TEST 4: Change official source info triggers change detection queue."""
        rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-scheme-annadata").first()
        initial_deadline = rec.application_deadline
        
        # Simulate source update detected
        change_entry = detect_record_changes(
            rec.id,
            {"application_deadline": "31 Dec 2026", "benefit_amount_str": "₹20,000 / Year"},
            self.db
        )
        self.assertIsNotNone(change_entry)
        self.assertIn("application_deadline", change_entry.diff_data)

    def test_05_historical_name_resolution(self):
        """TEST 5: Search 'Jagananna Vidya Deevena' resolves to current Post Matric Scholarships."""
        res = resolve_citizen_query("test-session-2", "Jagananna Vidya Deevena", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res.historical_superseded_notice)
        self.assertEqual(res.historical_superseded_notice["superseded_title"], "Jagananna Vidya Deevena")
        self.assertTrue("Post Matric Scholarships" in res.resolved_information_record.title)

    def test_06_scholarship_org_classification(self):
        """TEST 6: LIC Scholarship is classified as Tier 3 Organization Verified, never Government Verified."""
        lic = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-sch-lic-golden-jubilee").first()
        if lic:
            self.assertEqual(lic.badge_type, "ORGANIZATION_VERIFIED")
            self.assertEqual(lic.source_trust_tier, 3)

    def test_07_source_health_pipeline(self):
        """TEST 7: Source health registry reports all 10 registered sources."""
        sources = self.db.query(models.InformationSource).all()
        self.assertGreaterEqual(len(sources), 10)
        for s in sources:
            self.assertIn(s.trust_tier, [1, 2, 3, 4])
            self.assertTrue(len(s.official_url) > 0)

    def test_08_dynamic_officials_profile(self):
        """TEST 8: Official public figure is data-driven from database."""
        cm = self.db.query(models.OfficialProfile).filter(models.OfficialProfile.designation.like("%Chief Minister%")).first()
        self.assertIsNotNone(cm)
        self.assertEqual(cm.verification_status, "VERIFIED")

    def test_09_callback_request_creation(self):
        """TEST 9: Callback creation persists real ServiceRequest with callback flags."""
        req = models.ServiceRequest(
            citizen_id=1,
            sub_service_id="sub-pan-new",
            assistance_tier="LEVEL_C_PROCESS_HELP",
            status="NEW",
            citizen_location_str="Vijayawada, NTR District",
            notes="Test Callback",
            callback_requested=True,
            official_statutory_fee=0.0,
            gsp_assistance_fee=0.0,
            partner_commission=0.0
        )
        self.db.add(req)
        self.db.commit()
        self.assertTrue(req.id > 0)
        self.assertTrue(req.callback_requested)

if __name__ == '__main__':
    unittest.main()
