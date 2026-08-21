import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query, extract_user_goal, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestUniversalActionUnderstanding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_download_aadhaar(self):
        res = resolve_citizen_query("test-univ-1", "How do I download my Aadhaar?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")
        self.assertIn("Download", res.explanation)
        self.assertIn("https://myaadhaar.uidai.gov.in", res.explanation)

    def test_02_context_vs_goal_separation_aadhaar(self):
        res = resolve_citizen_query("test-univ-2", "I updated my mobile number in Aadhaar. How do I download the updated Aadhaar?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")

    def test_03_birth_certificate_correction(self):
        res = resolve_citizen_query("test-univ-3", "my father's name is wrong on my birth certificate", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-birth-father-corr")

    def test_04_driving_licence_renewal_direct(self):
        res = resolve_citizen_query("test-univ-4", "How do I renew my driving licence?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-dl-renewal")

    def test_05_driving_licence_expiring_natural_language(self):
        res = resolve_citizen_query("test-univ-5", "my licence is going to expire, what should I do?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-dl-renewal")

    def test_06_voter_card_lost_replace(self):
        res = resolve_citizen_query("test-univ-6", "I lost my voter card", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-voter-lost")

    def test_07_caste_certificate_apply(self):
        res = resolve_citizen_query("test-univ-7", "How do I apply for a caste certificate?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-caste-integrated")

    def test_08_caste_certificate_duplicate_copy(self):
        res = resolve_citizen_query("test-univ-8", "how can I get another copy of my caste certificate?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-caste-duplicate")

    def test_09_income_certificate_document_requirements(self):
        res = resolve_citizen_query("test-univ-9", "What documents do I need for income certificate?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-income-new")
        self.assertIn("Required Documents", res.explanation)

    def test_10_contextual_scholarship_eligibility(self):
        sid = "test-ctx-sch-elig"
        res1 = resolve_citizen_query(sid, "Tell me about Post Matric Scholarship", db=self.db)
        self.assertIsNotNone(res1.resolved_information_record)
        res2 = resolve_citizen_query(sid, "can I get this scholarship?", db=self.db)
        self.assertIn(res2.intent, ["CONTEXT_ELIGIBILITY", "CONTEXTUAL_ELIGIBILITY"])
        self.assertIn("Eligibility Criteria", res2.explanation)

    def test_11_contextual_cost_inquiry(self):
        sid = "test-ctx-fee-inq"
        res1 = resolve_citizen_query(sid, "I need to renew my driving licence", db=self.db)
        self.assertIsNotNone(res1.resolved_sub_service)
        res2 = resolve_citizen_query(sid, "How much does this service cost?", db=self.db)
        self.assertEqual(res2.intent, "CONTEXT_FEE_INQUIRY")
        self.assertIn("₹200.00", res2.explanation)

    def test_12_contextual_processing_time(self):
        sid = "test-ctx-time-inq"
        res1 = resolve_citizen_query(sid, "Father name wrong in birth certificate", db=self.db)
        self.assertIsNotNone(res1.resolved_sub_service)
        res2 = resolve_citizen_query(sid, "How long does this take?", db=self.db)
        self.assertEqual(res2.intent, "CONTEXT_PROCESSING_TIME")
        self.assertIn("15 Working Days", res2.explanation)

    def test_13_contextual_official_website(self):
        sid = "test-ctx-web-inq"
        res1 = resolve_citizen_query(sid, "What is PM-KISAN?", db=self.db)
        self.assertIsNotNone(res1.resolved_information_record)
        res2 = resolve_citizen_query(sid, "Where is the official website?", db=self.db)
        self.assertIn("https://karshak.ap.gov.in", res2.explanation)

    def test_14_topic_switching(self):
        sid = "test-topic-switch"
        res1 = resolve_citizen_query(sid, "How do I renew my driving licence?", db=self.db)
        self.assertEqual(res1.resolved_sub_service.id, "sub-dl-renewal")
        res2 = resolve_citizen_query(sid, "What documents are required?", db=self.db)
        self.assertEqual(res2.intent, "CONTEXT_DOCUMENTS_INQUIRY")
        self.assertIn("Driving Licence Renewal", res2.explanation)
        res3 = resolve_citizen_query(sid, "Actually, I lost my voter card.", db=self.db)
        self.assertIsNotNone(res3.resolved_sub_service)
        self.assertEqual(res3.resolved_sub_service.id, "sub-voter-lost")
        res4 = resolve_citizen_query(sid, "Where is the official website?", db=self.db)
        self.assertIn("https://voters.eci.gov.in", res4.explanation)

if __name__ == '__main__':
    unittest.main()
