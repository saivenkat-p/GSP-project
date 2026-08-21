import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import SessionLocal, engine, Base
import models
import schemas
from service_resolution_engine import resolve_citizen_query, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestLLMRAGArchitecture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        seed_database()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_conversational_turn_no_rag(self):
        """Conversational greetings: natural answer, no government card, source_status is None."""
        res = resolve_citizen_query("test-chat-1", "hi", db=self.db)
        self.assertEqual(res.mode, "CONVERSATIONAL")
        self.assertIsNone(res.source_status)
        self.assertIsNone(res.resolved_sub_service)
        self.assertIsNone(res.resolved_information_record)
        self.assertIn("Hello", res.explanation)

    def test_02_general_ai_turn(self):
        """General AI question: natural answer, no government card, source_status is None."""
        res = resolve_citizen_query("test-chat-2", "what is artificial intelligence", db=self.db)
        self.assertEqual(res.mode, "GENERAL_AI")
        self.assertIsNone(res.source_status)
        self.assertIn("intelligence", res.explanation.lower())

    def test_03_lost_aadhaar_not_address_update(self):
        """Unseen Tanglish lost Aadhaar queries must return Lost Aadhaar retrieval, NEVER Address Update."""
        queries = [
            "actually na aadhar poyindhi can i get that",
            "anna na card kanapadakunda poyindi malli ela techukovali",
            "aadhar card ekkado poyindi",
            "na aadhaar miss ayyindi online lo vastada"
        ]
        for q in queries:
            sid = f"test-lost-{hash(q)}"
            res = resolve_citizen_query(sid, q, db=self.db)
            self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
            self.assertEqual(res.source_status, "VERIFIED")
            self.assertIsNotNone(res.resolved_sub_service)
            self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-lost")
            self.assertNotEqual(res.resolved_sub_service.id, "sub-aadhaar-address", f"Failed on query: {q}")
            self.assertIn("myaadhaar.uidai.gov.in", res.explanation)

    def test_04_fresh_aadhaar_enrolment(self):
        """Applying for new Aadhaar must resolve to fresh enrolment, NOT Address Update."""
        res = resolve_citizen_query("test-enrol-1", "aadhar ela appply cheyali", db=self.db)
        self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
        self.assertEqual(res.source_status, "VERIFIED")
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-aadhaar-enrolment")
        self.assertNotEqual(res.resolved_sub_service.id, "sub-aadhaar-address")

    def test_05_personal_student_scholarship_situation(self):
        """Personal citizen situation about student/degree/engineering financial assistance."""
        unseen_queries = [
            "ma abbai engineering chestunnadu fees ki govt help emaina undha",
            "scholership kavali kani em undho telidu",
            "government nundi students ki emaina money vastunda"
        ]
        for q in unseen_queries:
            sid = f"test-sch-{hash(q)}"
            res = resolve_citizen_query(sid, q, db=self.db)
            self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
            self.assertEqual(res.source_status, "VERIFIED")
            self.assertTrue(
                (res.resolved_information_record and ("SCHOLARSHIP" in res.resolved_information_record.information_type or "Higher Education" in res.resolved_information_record.category))
                or (res.resolved_sub_service is not None)
            )

    def test_06_driving_licence_renewal(self):
        """Driving licence expired inquiry."""
        res = resolve_citizen_query("test-dl-1", "license aipoyindi ippudu em cheyyali", db=self.db)
        self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
        self.assertEqual(res.source_status, "VERIFIED")
        self.assertIsNotNone(res.resolved_sub_service)
        self.assertEqual(res.resolved_sub_service.id, "sub-dl-renewal")
        self.assertIn("sarathi.parivahan.gov.in", res.explanation)

    def test_07_multi_turn_and_topic_switching(self):
        """Multi-turn dialogue maintains context until user switches topic."""
        session_id = "test-session-multiturn"
        if session_id in SESSION_CONTEXT_STORE:
            del SESSION_CONTEXT_STORE[session_id]

        # Turn 1: Personal context
        r1 = resolve_citizen_query(session_id, "My son is doing B.Tech.", db=self.db)
        self.assertEqual(r1.mode, "GOVERNMENT_GROUNDED")

        # Turn 2: Scholarship inquiry
        r2 = resolve_citizen_query(session_id, "Any scholarship?", db=self.db)
        self.assertEqual(r2.mode, "GOVERNMENT_GROUNDED")
        self.assertEqual(r2.source_status, "VERIFIED")

        # Turn 3: Topic Switch to Ration Card
        r3 = resolve_citizen_query(session_id, "Actually my ration card has a wrong name", db=self.db)
        self.assertEqual(r3.mode, "GOVERNMENT_GROUNDED")
        self.assertIsNotNone(r3.resolved_sub_service)
        self.assertEqual(r3.resolved_sub_service.id, "sub-ration-member-add")
        self.assertNotIn("scholarship", r3.explanation.lower())

if __name__ == '__main__':
    unittest.main()
