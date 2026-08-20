import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
from service_resolution_engine import resolve_citizen_query

def run_section_27_acceptance_test():
    """
    SECTION 27 ACCEPTANCE TEST:
    Proves that adding a BRAND NEW service to the database makes it instantly searchable
    and AI discoverable WITHOUT modifying a single line of AI / engine code!
    """
    db = SessionLocal()
    try:
        print("=== RUNNING SECTION 27 & 38 UNIVERSAL ENGINE ACCEPTANCE TESTS ===")

        # 1. SECTION 27 ZERO-CODE MODIFICATION TEST FOR BRAND NEW SERVICE (Passport)
        print("\n--- Test 1: Zero-Code Modification Test for Brand New DB Service (Passport) ---")
        new_passport_service = models.Service(
            id="srv-passport-test",
            official_name="Passport Seva Services (MEA)",
            category="Travel & Identity",
            department="Ministry of External Affairs (MEA)",
            description="Fresh passport application, reissue, renewal, and Tatkal passport services.",
            state_scope="NAT",
            district_scope="ALL",
            aliases=["passport", "tatkal passport", "indian passport", "passport seva"],
            keywords=["passport", "travel", "external affairs", "visa"],
            verification_status="VERIFIED"
        )
        db.add(new_passport_service)
        db.commit()

        sub_passport_renew = models.SubService(
            id="sub-passport-renew-test",
            service_id=new_passport_service.id,
            sub_service_name="Renew Expired Indian Passport Online",
            action_type="Passport Renewal",
            aliases=["i need to renew my passport", "renew passport", "expired passport renewal"],
            keywords=["passport renewal", "expired passport"],
            official_fee=1500.0,
            processing_time="15 Working Days",
            application_method="Passport Seva Portal",
            physical_presence_requirement="REQUIRED",
            physical_presence_reason="Police verification and Passport Seva Kendra (PSK) appointment.",
            official_portal_url="https://passportindia.gov.in",
            official_source_url="https://passportindia.gov.in",
            confidence_status="VERIFIED"
        )
        db.add(sub_passport_renew)
        db.commit()

        # Query dynamic new service without modifying code
        res_passport = resolve_citizen_query("test-sess-1", "I need to renew my passport", db=db)
        assert res_passport.resolved_sub_service is not None, "Failed Section 27: New service was not resolved!"
        assert res_passport.resolved_sub_service.id == "sub-passport-renew-test", f"Failed Section 27: Expected sub-passport-renew-test, got {res_passport.resolved_sub_service.id}"
        print("PASS: Brand new service 'Passport Seva Services' resolved via alias 'I need to renew my passport' without code modification!")

        # 2. PAN CARD TEST
        print("\n--- Test 2: PAN Card Query Resolution ---")
        res_pan = resolve_citizen_query("test-sess-2", "pan card", db=db)
        assert res_pan.resolved_sub_service is not None or res_pan.needs_follow_up, "Failed PAN query resolution!"
        print(f"PASS: 'pan card' query recognized intent: {res_pan.intent}")

        # 3. DRIVING LICENCE RENEWAL TEST
        print("\n--- Test 3: Driving Licence Renewal Resolution ---")
        res_dl = resolve_citizen_query("test-sess-3", "I want to renew my driving licence", db=db)
        assert res_dl.resolved_sub_service is not None and res_dl.resolved_sub_service.id == "sub-dl-renewal", "Failed DL renewal query!"
        print("PASS: 'I want to renew my driving licence' resolved to sub-dl-renewal!")

        # 4. RATION CARD MEMBER ADDITION TEST
        print("\n--- Test 4: Ration Card Member Addition Resolution ---")
        res_ration = resolve_citizen_query("test-sess-4", "my ration card member addition", db=db)
        assert res_ration.resolved_sub_service is not None and res_ration.resolved_sub_service.id == "sub-ration-member-add", "Failed Ration Card query!"
        print("PASS: 'my ration card member addition' resolved to sub-ration-member-add!")

        # 5. BIRTH CERTIFICATE FATHER NAME CORRECTION TEST
        print("\n--- Test 5: Birth Certificate Father Name Correction Resolution ---")
        res_birth = resolve_citizen_query("test-sess-5", "father name wrong in birth certificate", db=db)
        assert res_birth.resolved_sub_service is not None and res_birth.resolved_sub_service.id == "sub-birth-father-corr", "Failed Birth Cert query!"
        print("PASS: 'father name wrong in birth certificate' resolved to sub-birth-father-corr!")

        # Clean up test entry
        db.delete(sub_passport_renew)
        db.delete(new_passport_service)
        db.commit()

        print("\nALL SECTION 27 & 38 UNIVERSAL ENGINE ACCEPTANCE TESTS PASSED 100%!")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    run_section_27_acceptance_test()
