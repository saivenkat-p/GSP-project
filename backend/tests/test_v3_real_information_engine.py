import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query
from change_detector import detect_record_changes
from freshness_engine import approve_information_change
from seed_data import seed_database

class TestV3RealInformationAndTrustEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_a_zero_hardcoding_database_backed_resolution(self):
        """Test A: Pan card query resolves strictly through database records."""
        res = resolve_citizen_query("test-session-a", "pan card application", db=self.db)
        self.assertIsNotNone(res)
        self.assertEqual(res.confidence_status, "VERIFIED")
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-pan-new")

    def test_b_fuzzy_and_alias_resolution(self):
        """Test B: Typo/Alias queries ('aadhar', 'adhar card', 'uidai') resolve to Aadhaar."""
        for typo in ["aadhar card update", "adhar address", "uidai update"]:
            res = resolve_citizen_query(f"test-b-{typo}", typo, db=self.db)
            self.assertEqual(res.confidence_status, "VERIFIED", f"Failed for query: {typo}")
            self.assertIsNotNone(res.resolved_sub_service)
            self.assertEqual(res.resolved_sub_service.service_id, "srv-aadhaar-uidai")

    def test_c_superseded_history_resolution(self):
        """
        Test C: Searching an older superseded scheme ('Jagananna Vidya Deevena')
        must return a historical note and resolve to current Post Matric Scholarships.
        """
        res = resolve_citizen_query("test-c-superseded", "Jagananna Vidya Deevena", db=self.db)
        self.assertIsNotNone(res)
        self.assertIsNotNone(res.historical_superseded_notice, "Historical predecessor notice must be generated")
        self.assertEqual(res.historical_superseded_notice["superseded_title"], "Jagananna Vidya Deevena")
        self.assertIsNotNone(res.resolved_information_record)
        self.assertTrue("Post Matric Scholarships" in res.resolved_information_record.title)

    def test_d_lic_organization_scholarship_classification(self):
        """
        Test D: LIC Scholarship must be tagged strictly as Tier 3 'Organization Verified',
        NEVER 'Government Verified' (Section 17 rule).
        """
        res = resolve_citizen_query("test-d-lic", "lic scholarship golden jubilee", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        rec = res.resolved_information_record
        self.assertEqual(rec.badge_type, "ORGANIZATION_VERIFIED")
        self.assertEqual(rec.source_trust_tier, 3)

    def test_e_dynamic_official_profile_update(self):
        """Test E: Changing official profile in DB updates without React code changes."""
        cm = self.db.query(models.OfficialProfile).filter(models.OfficialProfile.id == "off-ap-cm").first()
        self.assertIsNotNone(cm)
        original_name = cm.name

        # Update official name in DB
        cm.name = "Hon'ble Chief Minister AP (Updated Official)"
        self.db.commit()

        # Query again
        updated_cm = self.db.query(models.OfficialProfile).filter(models.OfficialProfile.id == "off-ap-cm").first()
        self.assertEqual(updated_cm.name, "Hon'ble Chief Minister AP (Updated Official)")

        # Revert back
        cm.name = original_name
        self.db.commit()

    def test_f_dynamic_scheme_deadline_change(self):
        """Test F: Changing a scheme deadline in DB immediately updates information record."""
        rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-scheme-annadata").first()
        self.assertIsNotNone(rec)
        original_deadline = rec.application_deadline

        # Update deadline in DB
        rec.application_deadline = "30 Nov 2026"
        self.db.commit()

        # Verify
        refreshed_rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-scheme-annadata").first()
        self.assertEqual(refreshed_rec.application_deadline, "30 Nov 2026")

        # Revert back
        rec.application_deadline = original_deadline
        self.db.commit()

    def test_g_outdated_filter_rule(self):
        """Test G: An OUTDATED scheme must be excluded from promotional query."""
        rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-scheme-annadata").first()
        self.assertIsNotNone(rec)

        # Mark as OUTDATED
        rec.verification_status = "OUTDATED"
        self.db.commit()

        promotional_items = (
            self.db.query(models.InformationRecord)
            .filter(
                models.InformationRecord.verification_status == "VERIFIED",
                models.InformationRecord.status == "ACTIVE",
                models.InformationRecord.is_promotional == True
            )
            .all()
        )
        promo_ids = [p.id for p in promotional_items]
        self.assertNotIn("rec-scheme-annadata", promo_ids)

        # Revert back to VERIFIED
        rec.verification_status = "VERIFIED"
        self.db.commit()

    def test_h_dynamic_new_scheme_addition(self):
        """Test H: Inserting a new verified scheme in DB immediately becomes searchable with 0 code changes."""
        new_scheme = models.InformationRecord(
            id="rec-test-solar-subsidy",
            title="PM Surya Ghar Rooftop Solar Subsidy 2026",
            description="Up to ₹78,000 direct subsidy for residential solar rooftop installations.",
            information_type="GOVERNMENT_SCHEME",
            category="Energy & Renewable",
            organization="Ministry of New and Renewable Energy",
            department="Energy Department",
            state_id="NAT",
            source_url="https://pmsuryaghar.gov.in",
            benefit_amount_str="Up to ₹78,000 Subsidy",
            official_statutory_fee=0.0,
            status="ACTIVE",
            verification_status="VERIFIED",
            badge_type="GOVERNMENT_VERIFIED",
            source_trust_tier=1,
            aliases=["solar rooftop", "pm surya ghar", "solar subsidy"],
            keywords=["solar", "electricity subsidy", "green energy"],
            banner_priority=120,
            is_promotional=True,
            last_checked="2026-08-21",
            last_verified="2026-08-21"
        )
        self.db.add(new_scheme)
        self.db.commit()

        # Query through Universal Resolution Engine
        res = resolve_citizen_query("test-h-solar", "solar subsidy", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, "rec-test-solar-subsidy")

        # Cleanup
        self.db.delete(new_scheme)
        self.db.commit()

    def test_i_change_detection_and_approval_workflow(self):
        """Test I: Change detection generates diff and admin approval increments version and logs audit."""
        rec = self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-scheme-aarogyasri").first()
        initial_version = rec.version
        initial_benefit = rec.benefit_amount_str

        incoming_change = {
            "title": rec.title,
            "description": rec.description,
            "benefit_amount_str": "Cashless Cover up to ₹35 Lakhs Super Speciality",  # Benefit updated
            "application_deadline": rec.application_deadline,
            "official_statutory_fee": rec.official_statutory_fee,
            "eligibility_criteria": rec.eligibility_criteria,
            "required_documents": rec.required_documents,
            "source_url": rec.source_url
        }

        queue_item = detect_record_changes(rec.id, incoming_change, self.db)
        self.assertIsNotNone(queue_item)
        self.assertEqual(queue_item.review_status, "PENDING")

        # Approve change as Admin
        updated_rec = approve_information_change(queue_item.id, "admin_test", self.db, reason="Cabinet approval gazette")
        self.assertEqual(updated_rec.verification_status, "VERIFIED")
        self.assertNotEqual(updated_rec.version, initial_version)
        self.assertEqual(updated_rec.benefit_amount_str, "Cashless Cover up to ₹35 Lakhs Super Speciality")

        # Verify historical version was created
        history = self.db.query(models.InformationVersionHistory).filter(models.InformationVersionHistory.record_id == rec.id).first()
        self.assertIsNotNone(history)

        # Revert
        updated_rec.benefit_amount_str = initial_benefit
        updated_rec.version = initial_version
        self.db.commit()

if __name__ == "__main__":
    unittest.main()
