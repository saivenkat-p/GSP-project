import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestConversationalIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_casual_hi(self):
        """User: hi -> normal conversation, zero RAG retrieval"""
        res = resolve_citizen_query("test-conv-1", "hi", db=self.db)
        self.assertEqual(res.intent, "GREETING")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertIn("Hello! I'm your GSP Grounded AI Assistant", res.explanation)

    def test_02_casual_how_are_you(self):
        """User: how are you -> normal conversation, zero RAG retrieval"""
        res = resolve_citizen_query("test-conv-2", "how are you", db=self.db)
        self.assertEqual(res.intent, "CASUAL_CHAT")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertIn("doing well", res.explanation.lower())

    def test_03_conversational_doubt_sir(self):
        """User: sir naaku oka doubt undi -> polite conversational readiness, zero RAG retrieval"""
        res = resolve_citizen_query("test-conv-3", "sir naaku oka doubt undi", db=self.db)
        self.assertEqual(res.intent, "CASUAL_CHAT")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertTrue("doubt" in res.explanation.lower() or "help" in res.explanation.lower())

    def test_04_general_knowledge_what_is_ai(self):
        """User: what is AI -> normal general explanation, not government RAG"""
        res = resolve_citizen_query("test-conv-4", "what is AI", db=self.db)
        self.assertEqual(res.intent, "GENERAL_KNOWLEDGE")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertIn("Artificial Intelligence", res.explanation)

    def test_05_career_degree_govt_jobs(self):
        """User: degree ayyaka govt jobs em vastai -> career guidance for degree holders"""
        res = resolve_citizen_query("test-conv-5", "degree ayyaka govt jobs em vastai", db=self.db)
        self.assertEqual(res.intent, "GENERAL_KNOWLEDGE")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertIn("UPSC", res.explanation)
        self.assertIn("SSC CGL", res.explanation)

    def test_06_tanglish_aadhaar_download(self):
        """User: aadhar card ela download cheyali -> Aadhaar Download"""
        res = resolve_citizen_query("test-conv-6", "aadhar card ela download cheyali", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")
        self.assertIn("https://myaadhaar.uidai.gov.in", res.explanation)

    def test_07_tanglish_aadhaar_updated_what_to_do(self):
        """User: aadhar updte chesanu ippudu em cheyali -> Goal: Download updated card"""
        res = resolve_citizen_query("test-conv-7", "aadhar updte chesanu ippudu em cheyali", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")

    def test_08_tanglish_aadhaar_card_ela_vastadi(self):
        """User: aadhar updte chesanu card ela vastadi -> Goal: Download updated card"""
        res = resolve_citizen_query("test-conv-8", "aadhar updte chesanu card ela vastadi", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")

    def test_09_tanglish_son_scholarship_general(self):
        """User: na son ki scholarship undha -> Understands student scholarship request"""
        res = resolve_citizen_query("test-conv-9", "na son ki scholarship undha", db=self.db)
        self.assertTrue(res.resolved_information_record is not None or res.needs_follow_up)

    def test_10_tanglish_son_degree_scholarship(self):
        """User: na son degree chaduvutunnadu govt nundi emaina help undha -> Post Matric Scholarships"""
        res = resolve_citizen_query("test-conv-10", "na son degree chaduvutunnadu govt nundi emaina help undha", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, "rec-sch-post-matric-ap")
        self.assertIn("https://jnanabhumi.ap.gov.in", res.explanation)

    def test_11_broad_govt_help_clarification(self):
        """User: naaku govt nundi emaina help undha -> Broad clarification prompt without crashing"""
        res = resolve_citizen_query("test-conv-11", "naaku govt nundi emaina help undha", db=self.db)
        self.assertEqual(res.intent, "BROAD_GOVT_HELP")
        self.assertTrue(res.needs_follow_up)
        self.assertIn("Education", res.explanation)

    def test_12_tanglish_license_expired(self):
        """User: license expire ayindi em cheyali -> Driving Licence Renewal"""
        res = resolve_citizen_query("test-conv-12", "license expire ayindi em cheyali", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-dl-renewal")
        self.assertIn("parivahan.gov.in", res.explanation)

    def test_13_tanglish_ration_card_name_correction(self):
        """User: ration card lo peru tappu undi -> Ration Card correction / Member update"""
        res = resolve_citizen_query("test-conv-13", "ration card lo peru tappu undi", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-ration-member-add")

    def test_14_typo_scholership_kavali(self):
        """User: scholership kavali -> Understands scholarship typo and prompts or returns scholarships"""
        res = resolve_citizen_query("test-conv-14", "scholership kavali", db=self.db)
        self.assertTrue(res.resolved_information_record is not None or res.intent == "BROAD_SCHOLARSHIP_DISCOVERY")

    def test_15_what_are_new_government_schemes(self):
        """User: what are new government schemes -> Latest verified updates"""
        res = resolve_citizen_query("test-conv-15", "what are new government schemes", db=self.db)
        self.assertEqual(res.intent, "SCHEME_UPDATES")
        self.assertIn("Official Sources", res.explanation)

    def test_16_english_updated_aadhaar_download(self):
        """User: I updated Aadhaar, how do I download it? -> Aadhaar download"""
        res = resolve_citizen_query("test-conv-16", "I updated Aadhaar, how do I download it?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")

    def test_17_telugu_unicode_aadhaar_download(self):
        """User: నా ఆధార్ కార్డు ఎలా డౌన్లోడ్ చేసుకోవాలి? -> Telugu response + UIDAI portal"""
        res = resolve_citizen_query("test-conv-17", "నా ఆధార్ కార్డు ఎలా డౌన్లోడ్ చేసుకోవాలి?", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-download")
        self.assertIn("https://myaadhaar.uidai.gov.in", res.explanation)

if __name__ == '__main__':
    unittest.main()
