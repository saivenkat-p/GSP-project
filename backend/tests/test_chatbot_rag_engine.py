import unittest
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestGSPChatbotRAGEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_greeting_hi(self):
        """TEST 1: 'hi' -> GREETING intent, greeting response, NO database retrieval."""
        res = resolve_citizen_query("test-greet-1", "hi", db=self.db)
        self.assertEqual(res.intent, "GREETING")
        self.assertIn("Hello! I'm your GSP Grounded AI Assistant", res.explanation)
        self.assertIsNone(res.resolved_information_record, "Greeting should NOT retrieve a government scheme!")
        self.assertIsNone(res.resolved_sub_service, "Greeting should NOT retrieve a sub-service!")

    def test_02_greeting_hello(self):
        """TEST 2: 'hello' -> GREETING intent only."""
        res = resolve_citizen_query("test-greet-2", "hello", db=self.db)
        self.assertEqual(res.intent, "GREETING")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)

    def test_03_scheme_updates(self):
        """TEST 3: 'what are new scheme updates' -> returns recent schemes/updates, NOT unrelated services like Aadhaar Address."""
        res = resolve_citizen_query("test-upd-1", "what are new scheme updates", db=self.db)
        self.assertEqual(res.intent, "SCHEME_UPDATES")
        self.assertIn("Latest Verified Government Scheme Updates", res.explanation)
        self.assertIsNotNone(res.resolved_information_record)
        # Must be a scheme/benefit/update record, NOT a statutory sub-service
        self.assertIsNone(res.resolved_sub_service)
        self.assertTrue("SCHEME" in res.resolved_information_record.information_type or "UPDATE" in res.resolved_information_record.information_type or "BENEFIT" in res.resolved_information_record.information_type)

    def test_04_new_scholarships(self):
        """TEST 4: 'any new scholarships?' -> returns verified scholarships."""
        res = resolve_citizen_query("test-sch-1", "any new scholarships?", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertTrue("SCHOLARSHIP" in res.resolved_information_record.information_type or "Higher Education" in res.resolved_information_record.category)

    def test_05_pm_kisan_information(self):
        """TEST 5: 'what is PM-KISAN?' -> returns PM-KISAN / Annadata Sukhibhava info."""
        res = resolve_citizen_query("test-kisan-1", "what is PM-KISAN?", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertTrue("Annadata Sukhibhava" in res.resolved_information_record.title or "PM-KISAN" in res.resolved_information_record.title)
        self.assertIn("Official Source", res.explanation)

    def test_06_pm_kisan_eligibility(self):
        """TEST 6: 'am I eligible for PM-KISAN?' -> returns PM-KISAN eligibility criteria."""
        res = resolve_citizen_query("test-kisan-elig", "am I eligible for PM-KISAN?", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertIn("Eligibility Criteria", res.explanation)
        self.assertTrue(len(res.eligibility) > 0)

    def test_07_contextual_documents_followup(self):
        """
        TEST 7: Multi-turn context.
        Turn 1: 'Tell me about Post Matric Scholarship'
        Turn 2: 'am I eligible?' (Contextually refers to Post Matric Scholarship)
        Turn 3: 'what documents are required?' (Contextually refers to Post Matric Scholarship)
        """
        session_id = "test-session-multi-context-scholarship"
        
        # Turn 1
        res1 = resolve_citizen_query(session_id, "Tell me about Post Matric Scholarship", db=self.db)
        self.assertIsNotNone(res1.resolved_information_record)
        self.assertTrue("Post Matric" in res1.resolved_information_record.title)

        # Turn 2: 'am I eligible?'
        res2 = resolve_citizen_query(session_id, "am I eligible?", db=self.db)
        self.assertIn(res2.intent, ["CONTEXT_ELIGIBILITY", "CONTEXTUAL_ELIGIBILITY"])
        self.assertIn("Post Matric Scholarships", res2.explanation)
        self.assertIn("Eligibility", res2.explanation)

        # Turn 3: 'what documents are required?'
        res3 = resolve_citizen_query(session_id, "what documents are required?", db=self.db)
        self.assertIn(res3.intent, ["CONTEXT_DOCUMENTS_INQUIRY", "CONTEXT_DOCUMENT_REQUIREMENTS", "CONTEXTUAL_DOCUMENT_REQUIREMENTS"])
        self.assertIn("Post Matric Scholarships", res3.explanation)
        self.assertTrue(len(res3.documents) > 0)

    def test_08_birth_certificate_correction(self):
        """TEST 8: 'father name wrong in birth certificate' -> CERTIFICATE_CORRECTION, resolves to sub-birth-father-corr."""
        res = resolve_citizen_query("test-birth-corr", "father name wrong in birth certificate", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-birth-father-corr")

    def test_09_driving_licence_renewal(self):
        """TEST 9: 'renew my driving licence' -> LICENCE_RENEWAL, resolves to sub-dl-renewal."""
        res = resolve_citizen_query("test-dl-renew", "renew my driving licence", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-dl-renewal")

    def test_10_voter_card_lost(self):
        """TEST 10: 'I lost my voter card' -> resolves to replacement voter card."""
        res = resolve_citizen_query("test-voter-lost", "I lost my voter card", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-voter-lost")

    def test_11_broad_government_schemes_clarification(self):
        """TEST 11: 'government schemes' -> broad discovery clarification, NOT a single random record."""
        res = resolve_citizen_query("test-broad-scheme", "government schemes", db=self.db)
        self.assertEqual(res.intent, "BROAD_SCHEME_DISCOVERY")
        self.assertTrue(res.needs_follow_up)
        self.assertIsNone(res.resolved_information_record, "Broad query should prompt for sector rather than picking a single random scheme")

    def test_12_random_unrelated_question_no_forced_record(self):
        """TEST 12: 'random unrelated question' -> UNKNOWN, doesn't force a random government record."""
        res = resolve_citizen_query("test-unrelated", "can you tell me a joke or cook pizza", db=self.db)
        self.assertEqual(res.confidence_status, "NOT_FOUND")
        self.assertEqual(res.confidence, 0.0)
        self.assertIsNone(res.resolved_information_record, "Must not force a scheme record on unrelated queries!")
        self.assertIsNone(res.resolved_sub_service, "Must not force a service record on unrelated queries!")
        self.assertIn("couldn't find a verified government record", res.explanation.lower())

    def test_13_thanks_courtesy(self):
        """TEST 13: 'thanks' -> COURTESY intent, polite conversational response, NO retrieval."""
        res = resolve_citizen_query("test-thanks", "thanks", db=self.db)
        self.assertEqual(res.intent, "COURTESY")
        self.assertIn("welcome", res.explanation.lower())
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)

if __name__ == '__main__':
    unittest.main()
