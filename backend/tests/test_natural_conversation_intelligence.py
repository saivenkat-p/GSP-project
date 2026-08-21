import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestNaturalConversationIntelligence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_aadhaar_apply_then_lost_conversation_flow(self):
        """
        Multi-turn Dynamic Context Test:
        Turn 1: 'aadhar ela appply cheyyali' -> Aadhaar enrolment / apply (NOT address update)
        Turn 2: 'actuvally na aadhar poyindhi, can i get that' -> Lost Aadhaar retrieval (NOT address update)
        """
        session_id = "test-aadhaar-convo-flow"
        if session_id in SESSION_CONTEXT_STORE:
            del SESSION_CONTEXT_STORE[session_id]

        # Turn 1
        res1 = resolve_citizen_query(session_id, "aadhar ela appply cheyyali", db=self.db)
        self.assertIsNotNone(res1.resolved_sub_service)
        self.assertEqual(res1.resolved_sub_service.id, "sub-aadhaar-enrolment")
        self.assertNotIn("Aadhaar Address Update", res1.explanation)
        self.assertIn("Enrolment", res1.explanation)

        # Turn 2 (Overriding intent from Apply to Lost/Retrieve)
        res2 = resolve_citizen_query(session_id, "actuvally na aadhar poyindhi, can i get that", db=self.db)
        self.assertIsNotNone(res2.resolved_sub_service)
        self.assertEqual(res2.resolved_sub_service.id, "sub-aadhaar-lost")
        self.assertNotIn("Aadhaar Address Update", res2.explanation)
        self.assertTrue("retrieve" in res2.explanation.lower() or "recovery" in res2.explanation.lower() or "myaadhaar" in res2.explanation.lower())

    def test_02_hello_andi_no_govt_record_dump(self):
        """User: 'hello andi' -> friendly greeting, zero government RAG"""
        res = resolve_citizen_query("test-hello-andi", "hello andi", db=self.db)
        self.assertEqual(res.intent, "GREETING")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertNotIn("Authority / Department", res.explanation)

    def test_03_sir_doubt_no_govt_record_dump(self):
        """User: 'sir naaku oka doubt undi' -> conversational readiness, zero government RAG"""
        res = resolve_citizen_query("test-doubt", "sir naaku oka doubt undi", db=self.db)
        self.assertEqual(res.intent, "CASUAL_CHAT")
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)
        self.assertNotIn("Authority / Department", res.explanation)

    def test_04_son_degree_scholarship_natural_response(self):
        """User: 'na son degree chaduvutunnadu govt nundi emaina scholarship undha' -> natural explanation of degree scholarship"""
        res = resolve_citizen_query("test-son-deg", "na son degree chaduvutunnadu govt nundi emaina scholarship undha", db=self.db)
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, "rec-sch-post-matric-ap")
        self.assertIn("jnanabhumi", res.explanation.lower())
        self.assertNotIn("Overview:", res.explanation)  # Not a raw dump

    def test_05_ration_card_name_correction(self):
        """User: 'ration card lo peru tappu undi em cheyali' -> natural correction guidance"""
        res = resolve_citizen_query("test-ration-corr", "ration card lo peru tappu undi em cheyali", db=self.db)
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-ration-member-add")
        self.assertIn("MeeSeva", res.explanation)

if __name__ == '__main__':
    unittest.main()
