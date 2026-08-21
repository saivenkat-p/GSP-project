import unittest
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal
from service_resolution_engine import resolve_citizen_query, SESSION_CONTEXT_STORE
from seed_data import seed_database

class TestGSPChatbotRAGPipelineFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()
        seed_database()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_greeting_bypass_with_name_extraction(self):
        """1. Greeting Loop Fix: 'hi my name is sai' returns natural greeting with zero DB dump."""
        sid = "test-greeting-name"
        res = resolve_citizen_query(sid, "hi my name is sai", db=self.db)
        self.assertEqual(res.mode, "CONVERSATIONAL")
        self.assertIn("Sai", res.explanation)
        self.assertIn("Grounded AI Assistant", res.explanation)
        self.assertIsNone(res.resolved_information_record)
        self.assertIsNone(res.resolved_sub_service)

    def test_02_telglish_query_rewriting_latest_schemes(self):
        """2. Telglish Rewriting: 'latest government schemes explian chestara' resolves to scheme updates."""
        sid = "test-telglish-schemes"
        res = resolve_citizen_query(sid, "latest government schemes explian chestara", db=self.db)
        self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
        self.assertEqual(res.source_status, "VERIFIED")
        self.assertIn("Official Source", res.explanation)

    def test_03_telglish_scholarship_query(self):
        """2b. Telglish Rewriting: 'na son ki scholarship undha' resolves to Post Matric Scholarship."""
        sid = "test-telglish-sch"
        res = resolve_citizen_query(sid, "na son ki scholarship undha", db=self.db)
        self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
        self.assertIsNotNone(res.resolved_information_record)
        self.assertEqual(res.resolved_information_record.id, "rec-sch-post-matric-ap")

    def test_04_broad_query_featured_schemes_fallback(self):
        """3. Broad Query Fallback: 'tell me schemes gurinchi' returns featured active schemes list."""
        sid = "test-broad-fallback"
        res = resolve_citizen_query(sid, "tell me schemes gurinchi", db=self.db)
        self.assertEqual(res.mode, "GOVERNMENT_GROUNDED")
        self.assertTrue(res.needs_follow_up or res.resolved_information_record is not None)

    def test_05_multi_turn_session_memory(self):
        """4. Multi-Turn Session Memory: remembers user name and topic across turns."""
        sid = "test-session-mem"
        res1 = resolve_citizen_query(sid, "hi my name is Ramesh", db=self.db)
        self.assertIn("Ramesh", res1.explanation)

        res2 = resolve_citizen_query(sid, "how are you", db=self.db)
        self.assertEqual(res2.mode, "CONVERSATIONAL")

        res3 = resolve_citizen_query(sid, "actually my aadhaar card is lost", db=self.db)
        self.assertEqual(res3.mode, "GOVERNMENT_GROUNDED")
        self.assertIsNotNone(res3.resolved_sub_service)
        self.assertEqual(res3.resolved_sub_service.id, "sub-aadhaar-lost")

if __name__ == '__main__':
    unittest.main()
