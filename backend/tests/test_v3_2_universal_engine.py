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

class TestGSPV32UniversalEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.query(models.InformationRecord).filter(models.InformationRecord.id == "rec-test-dynamic-scheme").delete()
        self.db.commit()
        self.db.close()

    def test_01_empty_database_safety(self):
        """TEST 1: Querying a non-existent state scope returns 0 records and no fake cards."""
        recs = self.db.query(models.InformationRecord).filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.state_id == "NON_EXISTENT"
        ).all()
        self.assertEqual(len(recs), 0)

    def test_02_dynamic_scheme_addition(self):
        """TEST 2: Inserting a new record into DB makes it immediately searchable with 0 code changes."""
        test_id = "rec-dynamic-solar-v32"
        self.db.query(models.InformationRecord).filter(models.InformationRecord.id == test_id).delete()
        self.db.commit()

        rec = models.InformationRecord(
            id=test_id,
            title="PM Surya Ghar Muft Bijli Rooftop Scheme",
            description="Up to 300 units of free electricity per month for 1 crore households.",
            information_type="GOVERNMENT_SCHEME",
            category="Energy & Power",
            organization="Ministry of New and Renewable Energy",
            department="Energy Department",
            state_id="NAT",
            source_url="https://pmsuryaghar.gov.in",
            published_at="2026-08-21",
            effective_from="2026-08-21",
            status="ACTIVE",
            verification_status="VERIFIED",
            badge_type="GOVERNMENT_VERIFIED",
            source_trust_tier=1,
            aliases=["muft bijli", "surya ghar", "solar rooftop"],
            keywords=["solar", "electricity grant"]
        )
        self.db.add(rec)
        self.db.commit()

        res = resolve_citizen_query("test-s-1", "I want to apply for solar rooftop muft bijli", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, test_id)

        # Cleanup
        self.db.delete(rec)
        self.db.commit()

    def test_03_outdated_status_exclusion(self):
        """TEST 3: Marking a record OUTDATED excludes it from active verified queries."""
        test_rec = models.InformationRecord(
            id="rec-test-outdated-filter",
            title="Temporary Outdated Test Scheme",
            description="Testing outdated status filtering",
            information_type="GOVERNMENT_SCHEME",
            category="Welfare Schemes",
            organization="Test Org",
            department="Test Dept",
            state_id="AP",
            source_url="https://example.gov.in",
            published_at="2026-08-21",
            effective_from="2026-08-21",
            status="ACTIVE",
            verification_status="OUTDATED",
            badge_type="GOVERNMENT_VERIFIED",
            source_trust_tier=1,
            aliases=["outdated test scheme"]
        )
        self.db.add(test_rec)
        self.db.commit()

        verified = self.db.query(models.InformationRecord).filter(
            models.InformationRecord.id == "rec-test-outdated-filter",
            models.InformationRecord.verification_status == "VERIFIED"
        ).first()
        self.assertIsNone(verified)

        self.db.delete(test_rec)
        self.db.commit()

    def test_04_generic_predecessor_resolution(self):
        """
        TEST 4: Generic Predecessor Resolution without hardcoded scheme names.
        Searching an older name resolves to the current record and produces a historical explanation notice.
        """
        # A. Aarogyasri -> Dr. NTR Vaidya Seva
        res1 = resolve_citizen_query("test-pred-1", "YSR Aarogyasri card", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res1.historical_superseded_notice)
        self.assertTrue("NTR Vaidya Seva" in res1.resolved_information_record.title)

        # B. Rythu Bharosa -> Annadata Sukhibhava / PM-KISAN
        res2 = resolve_citizen_query("test-pred-2", "YSR Rythu Bharosa apply", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res2.historical_superseded_notice)
        self.assertTrue("Annadata Sukhibhava" in res2.resolved_information_record.title)

        # C. Jagananna Vidya Deevena -> Post Matric Scholarships
        res3 = resolve_citizen_query("test-pred-3", "Jagananna Vidya Deevena reimbursement", "AP", "AP-NTR", db=self.db)
        self.assertIsNotNone(res3.historical_superseded_notice)
        self.assertTrue("Post Matric Scholarships" in res3.resolved_information_record.title)

    def test_05_service_count_intent(self):
        """TEST 5: 'how many services you have' returns actual database count dynamically."""
        res = resolve_citizen_query("test-count-1", "how many services you have", db=self.db)
        self.assertEqual(res.intent, "SERVICE_COUNT")
        self.assertEqual(res.confidence_status, "VERIFIED")
        expected_count = self.db.query(models.SubService).count()
        self.assertIn(str(expected_count), res.explanation)

    def test_06_scheme_count_intent(self):
        """TEST 6: 'how many schemes you have' returns actual verified schemes count."""
        res = resolve_citizen_query("test-count-2", "how many government schemes do you have?", db=self.db)
        self.assertEqual(res.intent, "SCHEME_COUNT")
        self.assertEqual(res.confidence_status, "VERIFIED")
        expected_schemes = self.db.query(models.InformationRecord).filter(
            models.InformationRecord.verification_status == "VERIFIED",
            models.InformationRecord.information_type.in_(["GOVERNMENT_SCHEME", "GOVERNMENT_BENEFIT"])
        ).count()
        self.assertIn(str(expected_schemes), res.explanation)

    def test_07_service_list_intent(self):
        """TEST 7: 'what services do you provide' lists actual database categories."""
        res = resolve_citizen_query("test-list-1", "what services do you provide?", db=self.db)
        self.assertEqual(res.intent, "SERVICE_LIST")
        self.assertIn("verified government categories", res.explanation.lower())

    def test_08_context_free_fee_and_deadline(self):
        """TEST 8: Asking 'what is the deadline' or 'how much' without context prompts user for the specific service."""
        res1 = resolve_citizen_query("test-no-ctx-1", "what is the deadline?", db=self.db)
        self.assertTrue(res1.needs_follow_up)
        self.assertIn("which", res1.explanation.lower())

        res2 = resolve_citizen_query("test-no-ctx-2", "how much is the fee?", db=self.db)
        self.assertTrue(res2.needs_follow_up)
        self.assertIn("which", res2.explanation.lower())

    def test_09_multi_turn_conversation_context(self):
        """
        TEST 9: Multi-turn session memory.
        Turn 1: 'Aadhaar update'
        Turn 2: 'how much?' -> answers fee for Aadhaar update in context.
        Turn 3: 'what documents?' -> answers documents for Aadhaar update in context.
        """
        session_id = "test-multi-turn-aadhaar"
        
        # Turn 1: Search Aadhaar Update
        res1 = resolve_citizen_query(session_id, "Aadhaar update", db=self.db)
        self.assertIsNotNone(res1.resolved_sub_service)
        self.assertEqual(res1.resolved_sub_service.service_id, "srv-aadhaar-uidai")

        # Turn 2: 'how much?' (Contextual fee inquiry)
        res2 = resolve_citizen_query(session_id, "how much?", db=self.db)
        self.assertEqual(res2.intent, "CONTEXT_FEE_INQUIRY")
        self.assertIn("₹50.00", res2.explanation)

        # Turn 3: 'what documents?' (Contextual document inquiry)
        res3 = resolve_citizen_query(session_id, "what documents are required?", db=self.db)
        self.assertIn(res3.intent, ["CONTEXT_DOCUMENTS_INQUIRY", "CONTEXT_DOCUMENT_REQUIREMENTS"])
        self.assertTrue(len(res3.documents) > 0)

    def test_10_national_service_availability_in_state_scope(self):
        """TEST 10: Central/National services (PAN, Aadhaar, Driving Licence) remain available when state_id='AP'."""
        from routers.services import get_services
        ap_services = get_services(state_id="AP", db=self.db)
        service_ids = [s.id for s in ap_services]
        self.assertIn("srv-aadhaar-uidai", service_ids)
        self.assertIn("srv-pan-card", service_ids)
        self.assertIn("srv-dl-parivahan", service_ids)

    def test_11_unknown_query_graceful_response(self):
        """TEST 11: Unknown query produces graceful low-confidence response without AI hallucination."""
        res = resolve_citizen_query("test-unk-1", "xyz random gibberish 9999", db=self.db)
        self.assertEqual(res.confidence_status, "NOT_FOUND")
        self.assertLessEqual(res.confidence, 0.4)
        self.assertIn("couldn't verify", res.explanation.lower())

if __name__ == '__main__':
    unittest.main()
