import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from service_resolution_engine import resolve_citizen_query

def run_personalized_home_tests():
    """
    Automated Acceptance Test Suite for GSP V2 Personalized Citizen Home & Opportunity Hub.
    """
    db = SessionLocal()
    try:
        print("=== RUNNING PERSONALIZED CITIZEN HOME & OPPORTUNITY HUB TESTS ===")

        # 1. TEST DATABASE MASTER TAXONOMY COUNT
        service_count = db.query(models.Service).count()
        sub_service_count = db.query(models.SubService).count()
        print(f"--- Test 1: Master Taxonomy Count ---")
        print(f"PASS: Master Services: {service_count}, Sub-Services: {sub_service_count}")
        assert service_count >= 10, "Failed: Service count is less than expected!"

        # 2. TEST FARMER SCHEME NATURAL LANGUAGE RESOLUTION
        print(f"\n--- Test 2: Natural Language Crop Loss Scheme Resolution ---")
        res_farmer = resolve_citizen_query("test-farmer-1", "I am a farmer and my crop failed", db=db)
        assert res_farmer.resolved_sub_service is not None, "Failed: Farmer crop loss scheme not resolved!"
        assert res_farmer.resolved_sub_service.id == "sub-crop-insurance", f"Failed: Expected sub-crop-insurance, got {res_farmer.resolved_sub_service.id}"
        print("PASS: 'I am a farmer and my crop failed' resolved to Crop Loss Assistance Claim!")

        # 3. TEST VOTER ID LOST CARD RESOLUTION
        print(f"\n--- Test 3: Voter ID Lost Card Resolution ---")
        res_voter = resolve_citizen_query("test-voter-1", "I lost my voter card", db=db)
        assert res_voter.resolved_sub_service is not None, "Failed: Lost voter card not resolved!"
        assert res_voter.resolved_sub_service.id == "sub-voter-lost", f"Failed: Expected sub-voter-lost, got {res_voter.resolved_sub_service.id}"
        print("PASS: 'I lost my voter card' resolved to Duplicate Voter Card Replacement!")

        # 4. TEST BIRTH CERTIFICATE FATHER NAME CORRECTION
        print(f"\n--- Test 4: Birth Certificate Father Name Correction ---")
        res_birth = resolve_citizen_query("test-birth-1", "father name wrong in birth certificate", db=db)
        assert res_birth.resolved_sub_service is not None, "Failed: Father name correction not resolved!"
        assert res_birth.resolved_sub_service.id == "sub-birth-father-corr", f"Failed: Expected sub-birth-father-corr, got {res_birth.resolved_sub_service.id}"
        print("PASS: 'father name wrong in birth certificate' resolved to Father's Name Correction!")

        print("\nALL PERSONALIZED CITIZEN HOME ACCEPTANCE TESTS PASSED 100%!")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_personalized_home_tests()
