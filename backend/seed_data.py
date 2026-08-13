from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
import auth

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if already seeded
        if db.query(models.Service).first():
            print("Database already seeded with verified government services.")
            return

        print("Seeding database with verified Andhra Pradesh & National government services...")

        # 1. USERS
        citizen_user = models.User(
            name="Sai Kumar Varma",
            email="citizen@govnav.in",
            password_hash=auth.get_password_hash("password123"),
            role="citizen",
            phone="+91 98765 43210",
            district="NTR / Vijayawada",
            state="Andhra Pradesh"
        )
        partner_user = models.User(
            name="Sri Rama MeeSeva Center (Vijayawada)",
            email="partner@meeseva-vijayawada.in",
            password_hash=auth.get_password_hash("password123"),
            role="partner",
            phone="+91 94400 12345",
            district="NTR / Vijayawada",
            state="Andhra Pradesh"
        )
        admin_user = models.User(
            name="AP Digital Governance Admin",
            email="admin@govnav.in",
            password_hash=auth.get_password_hash("password123"),
            role="admin",
            phone="+91 80080 00000",
            district="NTR / Vijayawada",
            state="Andhra Pradesh"
        )

        db.add_all([citizen_user, partner_user, admin_user])
        db.commit()
        db.refresh(citizen_user)
        db.refresh(partner_user)

        # 2. VERIFIED PARTNER PROFILE
        partner_profile = models.Partner(
            user_id=partner_user.id,
            business_name="Sri Rama MeeSeva & Facilitation Center",
            center_type="MeeSeva Franchise Authorized Operator",
            verification_status="verified",
            phone="+91 94400 12345",
            address="Door No. 10-2-4, Benz Circle Road, Vijayawada, NTR District",
            district="NTR / Vijayawada",
            state="Andhra Pradesh",
            distance_km=1.2,
            rating=4.9,
            reviews_count=48,
            badge_label="Verified MeeSeva Partner 🛡️",
            partner_assistance_fee=100.0,
            supported_service_ids=[
                "ap-income-certificate",
                "ap-caste-certificate",
                "ap-ews-certificate",
                "ap-encumbrance-certificate",
                "ap-adangal-1b",
                "ap-ration-card-modification",
                "national-driving-license-renewal"
            ]
        )
        db.add(partner_profile)
        db.commit()

        # 3. VERIFIED SERVICES KNOWLEDGE BASE
        services = [
            models.Service(
                id="ap-income-certificate",
                official_name="Integrated Income Certificate (MeeSeva)",
                state="Andhra Pradesh",
                district=None, # State-wide
                department="Revenue Department, Govt of AP",
                category="Revenue & Social Welfare",
                description="Official Income Certificate issued by the Tahsildar for college admissions, fee reimbursement (Jagananna Vidya Deevena), government schemes, and employment quotas.",
                eligibility_criteria=[
                    "Must be a permanent resident of Andhra Pradesh",
                    "Must hold valid Aadhaar card & Ration Card or self-declaration of annual family income",
                    "Required annual family income ceiling dependent on specific scheme applied (e.g. ₹2.5 Lakhs for scholarships)"
                ],
                required_documents=[
                    {
                        "name": "Application Form",
                        "mandatory": True,
                        "description": "Duly filled and signed Income Certificate application form (available on MeeSeva portal).",
                        "sample_url": "https://ap.meeseva.gov.in/downloads/income_app.pdf"
                    },
                    {
                        "name": "Aadhaar Card",
                        "mandatory": True,
                        "description": "Photocopy of Applicant's Aadhaar card with registered mobile linked.",
                        "sample_url": None
                    },
                    {
                        "name": "Rice Card / Ration Card or Voter ID",
                        "mandatory": True,
                        "description": "Proof of household residence & family composition.",
                        "sample_url": None
                    },
                    {
                        "name": "Income Proof / Salary Certificate / Self-Declaration",
                        "mandatory": True,
                        "description": "Salary slip from employer OR Form-16 OR notarized self-declaration affidavit signed by parent/head of household.",
                        "sample_url": "https://ap.meeseva.gov.in/downloads/self_declaration_income.pdf"
                    }
                ],
                diy_steps=[
                    "Step 1: Download and fill the official MeeSeva Income Certificate Application Form.",
                    "Step 2: Attach signed Self-Declaration affidavit and Aadhaar/Ration card copies.",
                    "Step 3: Visit your local Village Secretariat (Grama Sachivalayam) OR log in to AP Seva / MeeSeva portal (ap.meeseva.gov.in).",
                    "Step 4: Pay the official statutory fee of ₹50.",
                    "Step 5: Obtain acknowledgement slip with Application Number (e.g. IC012026xxxxxx).",
                    "Step 6: VRO (Village Revenue Officer) and RI (Revenue Inspector) conduct field verification within 5 working days.",
                    "Step 7: Download digitally signed certificate approved by Tahsildar."
                ],
                official_fee=50.0,
                processing_time="7 Working Days",
                application_method="Online via AP Seva Portal / Village Secretariat / MeeSeva",
                official_url="https://ap.meeseva.gov.in",
                source_url="https://ap.meeseva.gov.in/DeptPortal/UserInterface/LoginForm.aspx",
                source_last_verified="2026-08-10",
                is_demo_data=False,
                status="active",
                key_terms=["income", "college", "scholarship", "fee reimbursement", "tahsildar", "vidya deevena", "revenue", "meeseva", "ap"]
            ),

            models.Service(
                id="ap-caste-certificate",
                official_name="Integrated Community, Nativity & Date of Birth Certificate (Caste)",
                state="Andhra Pradesh",
                district=None,
                department="Revenue & Tribal Welfare Department",
                category="Revenue & Social Welfare",
                description="Integrated Certificate confirming Community (SC/ST/BC/OC), Nativity, and Date of Birth required for educational reservations, scholarships, and public sector employment.",
                eligibility_criteria=[
                    "Applicant or parents must belong to recognized SC / ST / BC category in Andhra Pradesh",
                    "Permanent resident of Andhra Pradesh",
                    "Land or school records establishing ancestral caste proof"
                ],
                required_documents=[
                    {
                        "name": "Applicant & Parent Aadhaar Cards",
                        "mandatory": True,
                        "description": "Valid Aadhaar proof for applicant and head of family.",
                        "sample_url": None
                    },
                    {
                        "name": "School Leaving Certificate / Transfer Certificate (TC)",
                        "mandatory": True,
                        "description": "Proof of Caste/Community entry in School Admission Register or SSC marks memo.",
                        "sample_url": None
                    },
                    {
                        "name": "Ration Card or AP Household Card",
                        "mandatory": True,
                        "description": "Proof of residence and family link.",
                        "sample_url": None
                    },
                    {
                        "name": "Caste Certificate of Parents or Blood Relatives",
                        "mandatory": True,
                        "description": "Previous verified caste certificate issued by Tahsildar to father, mother, or paternal uncle.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Collect Applicant's TC/SSC certificate indicating community.",
                    "Step 2: Submit application at nearest Grama/Ward Sachivalayam or MeeSeva Center.",
                    "Step 3: Pay official fee of ₹50.",
                    "Step 4: VRO & Revenue Inspector verify ancestral land/caste register entries.",
                    "Step 5: Tahsildar issues digitally signed Integrated Certificate upon approval."
                ],
                official_fee=50.0,
                processing_time="15 Working Days",
                application_method="Grama Sachivalayam / MeeSeva Portal",
                official_url="https://ap.meeseva.gov.in",
                source_url="https://ap.meeseva.gov.in/DeptPortal/UserInterface/LoginForm.aspx",
                source_last_verified="2026-08-10",
                is_demo_data=False,
                status="active",
                key_terms=["caste", "community", "sc", "st", "bc", "reservation", "nativity", "meeseva", "tahsildar"]
            ),

            models.Service(
                id="ap-ews-certificate",
                official_name="Economically Weaker Sections (EWS) Certificate for AP State Services",
                state="Andhra Pradesh",
                district=None,
                department="Revenue Department, Govt of AP",
                category="Revenue & Social Welfare",
                description="10% EWS Reservation Certificate for OC (Open Category / Non-Reserved) candidates whose family gross annual income is below ₹8 Lakhs and do not belong to SC/ST/BC categories.",
                eligibility_criteria=[
                    "Must belong to General Category / OC (Not covered under SC/ST/BC reservations)",
                    "Gross annual family income must be under ₹8 Lakhs per annum",
                    "Agricultural land held by family must be less than 5 Acres",
                    "Residential flat size under 1000 sq ft or plot under 100 sq yards in notified municipalities"
                ],
                required_documents=[
                    {
                        "name": "Aadhaar Card",
                        "mandatory": True,
                        "description": "Photocopy of applicant and family members' Aadhaar cards.",
                        "sample_url": None
                    },
                    {
                        "name": "Income Proof / IT Return / Form 16",
                        "mandatory": True,
                        "description": "IT Returns for past 3 years or notarized Affidavit of Income.",
                        "sample_url": None
                    },
                    {
                        "name": "Property & Land Ownership Proof",
                        "mandatory": True,
                        "description": "Pattadar Passbook or Property Tax Receipt demonstrating land/house bounds.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Verify EWS land and income ceiling eligibility.",
                    "Step 2: Submit application form with Income & Property declaration at Sachivalayam.",
                    "Step 3: Pay official fee of ₹50.",
                    "Step 4: Field inspection by Revenue Inspector.",
                    "Step 5: Certificate issued by Tahsildar valid for 1 Financial Year."
                ],
                official_fee=50.0,
                processing_time="10 Working Days",
                application_method="Grama Sachivalayam / MeeSeva Portal",
                official_url="https://ap.meeseva.gov.in",
                source_url="https://ap.meeseva.gov.in",
                source_last_verified="2026-08-10",
                is_demo_data=False,
                status="active",
                key_terms=["ews", "economically weaker", "10%", "reservation", "general category", "income limit", "tahsildar"]
            ),

            models.Service(
                id="ap-encumbrance-certificate",
                official_name="Encumbrance Certificate (EC) - Registration & Stamps Dept",
                state="Andhra Pradesh",
                district=None,
                department="Registration & Stamps Department, Govt of AP",
                category="Land Records & Property",
                description="Official document detailing all registered property transactions, mortgages, sales, or liabilities registered against a land or building over a specified search period (up to 30+ years).",
                eligibility_criteria=[
                    "Anyone with property location details (Survey Number, Door Number, Document Number, or Plot boundaries)",
                    "No restriction on applicant ownership"
                ],
                required_documents=[
                    {
                        "name": "Property Details / Sale Deed Copy",
                        "mandatory": True,
                        "description": "Survey No, Village name, SRO (Sub-Registrar Office) location, and prior registration document number.",
                        "sample_url": None
                    },
                    {
                        "name": "Applicant Identity Proof",
                        "mandatory": True,
                        "description": "Aadhaar Card or PAN Card of applicant requesting EC.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Access IGRS AP Portal (registration.ap.gov.in) OR visit nearest SRO / MeeSeva.",
                    "Step 2: Enter Survey Number, Boundary, or Document Number and select date range.",
                    "Step 3: Pay statutory search fee (₹20 to ₹500 based on years searched + user charge).",
                    "Step 4: Download digitally signed Encumbrance Certificate or collect physical certified copy from Sub-Registrar."
                ],
                official_fee=40.0,
                processing_time="Instant Online / 1 Day SRO Counter",
                application_method="Online via IGRS AP Portal (registration.ap.gov.in) / SRO Counter",
                official_url="https://registration.ap.gov.in",
                source_url="https://registration.ap.gov.in/igrs",
                source_last_verified="2026-08-08",
                is_demo_data=False,
                status="active",
                key_terms=["ec", "encumbrance", "land", "property", "sale deed", "mortgage", "registration", "igrs", "sub registrar", "survey number"]
            ),

            models.Service(
                id="ap-adangal-1b",
                official_name="Meebhoomi Adangal & 1-B Record of Rights (RoR)",
                state="Andhra Pradesh",
                district=None,
                department="Revenue & Land Records Department (Meebhoomi)",
                category="Land Records & Property",
                description="Certified extract of agricultural land tenancy record (Adangal) and Record of Rights (1-B) detailing land owner name, khata number, survey number, crop details, and extent of land.",
                eligibility_criteria=[
                    "Pattadar / land owner or interested party searching agricultural land records in AP"
                ],
                required_documents=[
                    {
                        "name": "Aadhaar Card or Khata Number / Survey Number",
                        "mandatory": True,
                        "description": "Pattadar Aadhaar number OR survey number with Village & Mandal name.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Visit Meebhoomi AP official portal (meebhoomi.ap.gov.in).",
                    "Step 2: Select District, Mandal, Village name, and enter Khata Number or Survey Number.",
                    "Step 3: View Adangal (crop/land detail) or 1-B (owner khata detail) on screen.",
                    "Step 4: For digitally signed certified printout, apply via MeeSeva/Sachivalayam by paying ₹35 official fee."
                ],
                official_fee=35.0,
                processing_time="Instant View / 1 Day Certified Copy",
                application_method="Meebhoomi AP Portal (meebhoomi.ap.gov.in) / Village Secretariat",
                official_url="http://meebhoomi.ap.gov.in",
                source_url="http://meebhoomi.ap.gov.in",
                source_last_verified="2026-08-05",
                is_demo_data=False,
                status="active",
                key_terms=["adangal", "1b", "meebhoomi", "land record", "pattadar", "survey number", "khata", "ror", "revenue"]
            ),

            models.Service(
                id="national-driving-license-renewal",
                official_name="Driving License (DL) Renewal - Parivahan Sewa",
                state="National / AP",
                district=None,
                department="Transport Department, Ministry of Road Transport & Highways (MoRTH)",
                category="Transport & Mobility",
                description="Renewal of expired Driving License within grace period or after expiration across Transport Offices (RTO) in India.",
                eligibility_criteria=[
                    "Existing valid or recently expired Driving License issued in India",
                    "Applicant over 40 years of age requires Form 1-A Medical Certificate signed by a registered MBBS Doctor"
                ],
                required_documents=[
                    {
                        "name": "Original Driving License",
                        "mandatory": True,
                        "description": "Physical DL card or original document details.",
                        "sample_url": None
                    },
                    {
                        "name": "Form 1-A Medical Certificate",
                        "mandatory": True,
                        "description": "Mandatory for applicants over 40 years old, signed by registered medical practitioner.",
                        "sample_url": "https://sarathi.parivahan.gov.in/sarathiservice/downloadForms.do"
                    },
                    {
                        "name": "Aadhaar Card (Address Proof)",
                        "mandatory": True,
                        "description": "Proof of current residence for Aadhaar-authenticated contactless renewal.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Visit Parivahan Sarathi Portal (sarathi.parivahan.gov.in).",
                    "Step 2: Select State (Andhra Pradesh) -> Apply for DL Renewal.",
                    "Step 3: Enter DL Number & Date of Birth.",
                    "Step 4: Upload Aadhaar card and Form 1-A Medical Certificate.",
                    "Step 5: Pay statutory renewal fee ₹400 (+ ₹150 late fee per year if expired > 1 year).",
                    "Step 6: Renewed DL sent to home address via Speed Post."
                ],
                official_fee=400.0,
                processing_time="7 to 10 Working Days",
                application_method="Online via Parivahan Sarathi Portal (sarathi.parivahan.gov.in)",
                official_url="https://sarathi.parivahan.gov.in",
                source_url="https://parivahan.gov.in",
                source_last_verified="2026-08-11",
                is_demo_data=False,
                status="active",
                key_terms=["dl", "driving license", "renewal", "rto", "transport", "parivahan", "medical certificate", "form 1a"]
            ),

            models.Service(
                id="ap-ration-card-modification",
                official_name="Rice Card / Ration Card Member Addition or Correction",
                state="Andhra Pradesh",
                district=None,
                department="Civil Supplies Department, Govt of AP",
                category="Civil Supplies & Food Security",
                description="Addition of newborn child/spouse name or correction of family member details in AP Rice Card for food security benefits and welfare schemes.",
                eligibility_criteria=[
                    "Existing active Rice Card / Ration Card in Andhra Pradesh",
                    "For new member addition: Birth certificate of child OR Marriage certificate/relinquishment for spouse"
                ],
                required_documents=[
                    {
                        "name": "Original Rice Card / Ration Card Copy",
                        "mandatory": True,
                        "description": "Current card number and household ID.",
                        "sample_url": None
                    },
                    {
                        "name": "Birth Certificate (for Newborn) OR Marriage Certificate",
                        "mandatory": True,
                        "description": "Proof of relationship for member addition.",
                        "sample_url": None
                    },
                    {
                        "name": "Aadhaar Card of New Member",
                        "mandatory": True,
                        "description": "Aadhaar with updated local address & mobile number.",
                        "sample_url": None
                    }
                ],
                diy_steps=[
                    "Step 1: Visit Village Secretariat (Grama Sachivalayam) Digital Assistant.",
                    "Step 2: Fill member addition form and submit e-KYC fingerprint authentication.",
                    "Step 3: Pay official fee ₹20.",
                    "Step 4: VRO/Tahsildar verification -> Name added to Digital Rice Card database."
                ],
                official_fee=20.0,
                processing_time="10 Working Days",
                application_method="Village Secretariat / Grama Sachivalayam Counter",
                official_url="https://epos.ap.gov.in",
                source_url="https://epos.ap.gov.in",
                source_last_verified="2026-08-01",
                is_demo_data=False,
                status="active",
                key_terms=["ration card", "rice card", "member addition", "civil supplies", "sachivalayam", "epos", "food security"]
            )
        ]

        db.add_all(services)
        db.commit()

        # 4. SAMPLE SERVICE REQUEST & REJECTION DIAGNOSTIC FOR DEMO
        demo_request = models.ServiceRequest(
            citizen_id=citizen_user.id,
            service_id="ap-income-certificate",
            partner_id=partner_profile.id,
            status="rejected",
            status_notes="Rejected by Tahsildar office due to missing notarized Income Affidavit & mismatched family name on Ration Card.",
            official_application_no="IC012026998877",
            citizen_district="NTR / Vijayawada",
            notes="Applied for engineering admission fee reimbursement."
        )
        db.add(demo_request)
        db.commit()
        db.refresh(demo_request)

        rejection_diag = models.RejectionDiagnostic(
            service_request_id=demo_request.id,
            rejection_reason="REJ-REV-402: Income proof document invalid. Notarized Self-Declaration Affidavit missing stamp seal and mother's maiden name on ration card differs from applicant Aadhaar record.",
            simple_explanation="Your Income Certificate application was declined because the income affidavit was missing an official notary seal, and your mother's name spelling on the Ration Card didn't exactly match her Aadhaar Card.",
            what_went_wrong="1. The uploaded self-declaration was signed on plain paper without a ₹20 Non-Judicial Stamp notary seal.\n2. Ration card name spelling mismatch ('Lakshmi' vs 'Laxmi Devi').",
            corrective_actions=[
                "Obtain a ₹20 Non-Judicial Stamp Paper from your local court vendor and get the Self-Declaration notarized.",
                "Submit a quick Name Spelling Correction request at Grama Sachivalayam OR attach a Name Discrepancy Affidavit signed by VRO.",
                "Upload the newly sealed affidavit and resubmit on AP Seva portal with Application No. IC012026998877."
            ],
            required_replacement_documents=[
                "Notarized Self-Declaration Affidavit on ₹20 Stamp Paper",
                "VRO Endorsement Letter / Name Discrepancy Affidavit"
            ],
            can_reapply=True,
            needs_legal_help=False,
            official_reapplication_url="https://ap.meeseva.gov.in",
            verified_info="Official Tahsildar Guidelines Section 4(B): Applications resubmitted within 30 days of rejection with rectified notarized affidavits require NO fresh official statutory fees."
        )
        db.add(rejection_diag)
        db.commit()

        print("Successfully seeded database with 7 verified services, 1 partner, demo citizen & rejection diagnostic record!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
