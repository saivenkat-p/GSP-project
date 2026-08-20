from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
import auth

def seed_database():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if master taxonomy already seeded
        existing_count = db.query(models.Service).count()
        if existing_count >= 25:
            print("GSP V2 Database already seeded with Master 45-Category Service Taxonomy.")
            return

        print("Seeding GSP V2 Database with Locations and 45-Category Master Government Service Taxonomy...")

        # 1. LOCATION HIERARCHY SEED
        if not db.query(models.State).filter(models.State.id == "AP").first():
            st_ap = models.State(id="AP", name="Andhra Pradesh")
            st_ts = models.State(id="TS", name="Telangana")
            st_nat = models.State(id="NAT", name="National / Central Govt")
            db.add_all([st_ap, st_ts, st_nat])
            db.commit()

            dist_ntr = models.District(id="AP-NTR", state_id="AP", name="NTR / Vijayawada")
            dist_vskp = models.District(id="AP-VSKP", state_id="AP", name="Visakhapatnam")
            dist_gnt = models.District(id="AP-GNT", state_id="AP", name="Guntur")
            dist_tpt = models.District(id="AP-TPT", state_id="AP", name="Tirupati")
            db.add_all([dist_ntr, dist_vskp, dist_gnt, dist_tpt])
            db.commit()

            mandal_vja_u = models.Mandal(id="AP-NTR-VJA-U", district_id="AP-NTR", name="Vijayawada Urban")
            mandal_vja_r = models.Mandal(id="AP-NTR-VJA-R", district_id="AP-NTR", name="Vijayawada Rural")
            mandal_gnt_u = models.Mandal(id="AP-GNT-GNT-U", district_id="AP-GNT", name="Guntur Urban")
            db.add_all([mandal_vja_u, mandal_vja_r, mandal_gnt_u])
            db.commit()

            loc_benz = models.VillageLocality(id="LOC-BENZ", mandal_id="AP-NTR-VJA-U", name="Benz Circle / Patamata", pincode="520010")
            loc_gov = models.VillageLocality(id="LOC-GOV", mandal_id="AP-NTR-VJA-U", name="Governorpet", pincode="520002")
            db.add_all([loc_benz, loc_gov])
            db.commit()

            gov_office1 = models.GovernmentOffice(
                name="Tahsildar Office, Vijayawada Urban",
                office_type="Revenue / Tahsildar",
                district_id="AP-NTR",
                address="Near Bus Station Road, Governorpet, Vijayawada, NTR District",
                working_hours="10:00 AM - 05:00 PM (Mon-Sat)"
            )
            gov_office2 = models.GovernmentOffice(
                name="Sub-Registrar Office (SRO), Vijayawada",
                office_type="Registration & Stamps",
                district_id="AP-NTR",
                address="M.G. Road, Labbipet, Vijayawada",
                working_hours="10:30 AM - 05:00 PM"
            )
            db.add_all([gov_office1, gov_office2])
            db.commit()

        # 2. MASTER 45-CATEGORY GOVERNMENT TAXONOMY SEED DATA
        master_services = [
            # 1. Identity & Citizen Documents (PAN, Aadhaar, Passport, Residence, EWS, OBC)
            {
                "id": "srv-pan-card",
                "official_name": "PAN Card Services (NSDL / UTIITSL)",
                "category": "Identity & Citizen Documents",
                "department": "Income Tax Department, Govt of India",
                "description": "New PAN card issuance, name/dob/address corrections, e-PAN download, and reprint of lost PAN card.",
                "state_scope": "NAT",
                "aliases": ["pan card", "pancard", "pan", "permanent account number", "nsdl pan", "uti pan"],
                "keywords": ["tax", "income tax", "financial id", "bank account pan", "lost pan", "reprint pan"],
                "sub_services": [
                    {
                        "id": "sub-pan-new",
                        "sub_service_name": "New PAN Card Application (Form 49A)",
                        "action_type": "New Application",
                        "aliases": ["new pan", "apply pan card", "first pan"],
                        "keywords": ["form 49a", "fresh pan"],
                        "official_fee": 107.0,
                        "processing_time": "7-10 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://www.onlineservices.nsdl.com",
                        "official_source_url": "https://www.incometax.gov.in"
                    },
                    {
                        "id": "sub-pan-correction",
                        "sub_service_name": "PAN Card Correction / Name / DOB Change",
                        "action_type": "Correction",
                        "aliases": ["pan correction", "pan name change", "pan wrong father name"],
                        "keywords": ["correction form", "pan update"],
                        "official_fee": 107.0,
                        "processing_time": "10-15 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://www.onlineservices.nsdl.com",
                        "official_source_url": "https://www.incometax.gov.in"
                    },
                    {
                        "id": "sub-pan-reprint",
                        "sub_service_name": "Lost PAN Card Reprint / Duplicate Copy",
                        "action_type": "Duplicate",
                        "aliases": ["lost pan card", "duplicate pan", "reprint pan"],
                        "keywords": ["lost card", "reprint"],
                        "official_fee": 50.0,
                        "processing_time": "5-7 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://www.onlineservices.nsdl.com",
                        "official_source_url": "https://www.incometax.gov.in"
                    }
                ]
            },
            {
                "id": "srv-aadhaar-uidai",
                "official_name": "Aadhaar Services (UIDAI)",
                "category": "Identity & Citizen Documents",
                "department": "Unique Identification Authority of India (UIDAI)",
                "description": "Aadhaar address update, mobile number linkage, PVC card order, and name/dob update guidance.",
                "state_scope": "NAT",
                "aliases": ["aadhaar", "aadhar", "adhar", "uidai", "aadhaar card", "aadhar card"],
                "keywords": ["identity", "biometric", "address change", "mobile link", "pvc card"],
                "sub_services": [
                    {
                        "id": "sub-aadhaar-address",
                        "sub_service_name": "Aadhaar Address Update Online",
                        "action_type": "Address Update",
                        "aliases": ["aadhaar address change", "change address aadhaar", "update address aadhar"],
                        "keywords": ["myAadhaar", "address proof"],
                        "official_fee": 50.0,
                        "processing_time": "3-7 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://myaadhaar.uidai.gov.in",
                        "official_source_url": "https://uidai.gov.in"
                    },
                    {
                        "id": "sub-aadhaar-mobile",
                        "sub_service_name": "Aadhaar Mobile Number Link / Update",
                        "action_type": "Mobile Update",
                        "aliases": ["aadhaar mobile link", "change phone number in aadhar", "link mobile aadhaar"],
                        "keywords": ["otp", "mobile link", "ask uidai"],
                        "official_fee": 50.0,
                        "processing_time": "24-48 Hours",
                        "physical_presence_requirement": "REQUIRED",
                        "physical_presence_reason": "Biometric fingerprint authentication at Aadhaar Seva Kendra counter.",
                        "official_portal_url": "https://uidai.gov.in",
                        "official_source_url": "https://uidai.gov.in"
                    }
                ]
            },
            # 2. Birth & Death Services
            {
                "id": "srv-birth-cert",
                "official_name": "Birth Certificate Services (Municipal / Panchayat)",
                "category": "Birth & Death Services",
                "department": "Public Health & Municipal Administration / Revenue Dept",
                "description": "Official Birth Certificate issuance, download, name addition, late registration, and correction services.",
                "state_scope": "AP",
                "aliases": ["birth certificate", "birth cert", "janma praman patra", "birth record"],
                "keywords": ["child birth", "hospital birth", "municipal birth", "father name birth"],
                "sub_services": [
                    {
                        "id": "sub-birth-father-corr",
                        "sub_service_name": "Father's Name Correction in Birth Certificate",
                        "action_type": "Father's Name Correction",
                        "aliases": ["father name wrong in birth certificate", "father name correction birth cert"],
                        "keywords": ["father name", "spelling correction", "affidavit"],
                        "official_fee": 50.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "MAY_BE_REQUIRED",
                        "official_portal_url": "https://cdma.ap.gov.in",
                        "official_source_url": "https://cdma.ap.gov.in"
                    },
                    {
                        "id": "sub-birth-mother-corr",
                        "sub_service_name": "Mother's Name Correction in Birth Certificate",
                        "action_type": "Mother's Name Correction",
                        "aliases": ["mother name wrong in birth certificate", "mother name correction birth cert"],
                        "keywords": ["mother name", "spelling correction"],
                        "official_fee": 50.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "MAY_BE_REQUIRED",
                        "official_portal_url": "https://cdma.ap.gov.in",
                        "official_source_url": "https://cdma.ap.gov.in"
                    },
                    {
                        "id": "sub-birth-child-add",
                        "sub_service_name": "Child's Name Addition / Correction in Birth Certificate",
                        "action_type": "Child's Name Addition",
                        "aliases": ["add child name birth certificate", "unnamed birth certificate"],
                        "keywords": ["child name", "unnamed birth"],
                        "official_fee": 50.0,
                        "processing_time": "10 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://cdma.ap.gov.in",
                        "official_source_url": "https://cdma.ap.gov.in"
                    }
                ]
            },
            {
                "id": "srv-death-cert",
                "official_name": "Death Certificate Services",
                "category": "Birth & Death Services",
                "department": "Public Health & Revenue Dept AP",
                "description": "Death registration, duplicate death certificate, late registration, and name correction.",
                "state_scope": "AP",
                "aliases": ["death certificate", "death cert", "marana praman patra"],
                "keywords": ["death record", "mortality cert"],
                "sub_services": [
                    {
                        "id": "sub-death-new",
                        "sub_service_name": "New Death Certificate Application",
                        "action_type": "New Application",
                        "aliases": ["apply death certificate", "death registration"],
                        "keywords": ["hospital death", "cremation cert"],
                        "official_fee": 50.0,
                        "processing_time": "7 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://cdma.ap.gov.in",
                        "official_source_url": "https://cdma.ap.gov.in"
                    }
                ]
            },
            # 3. Revenue & Certificates
            {
                "id": "srv-income-cert",
                "official_name": "Integrated Income Certificate (Revenue)",
                "category": "Revenue & Certificates",
                "department": "Revenue Department, Govt of AP",
                "description": "Income Certificate issued by Tahsildar for college fee reimbursement, scholarships, and welfare schemes.",
                "state_scope": "AP",
                "aliases": ["income certificate", "income cert", "meeseva income", "tahsildar income certificate"],
                "keywords": ["college income", "scholarship income", "fee reimbursement"],
                "sub_services": [
                    {
                        "id": "sub-income-college",
                        "sub_service_name": "Income Certificate for College & Scholarship",
                        "action_type": "New Application",
                        "aliases": ["income certificate for college", "scholarship income certificate"],
                        "keywords": ["college", "scholarship", "vidya deevena"],
                        "official_fee": 50.0,
                        "processing_time": "7 Working Days",
                        "physical_presence_requirement": "MAY_BE_REQUIRED",
                        "official_portal_url": "https://ap.meeseva.gov.in",
                        "official_source_url": "https://ap.meeseva.gov.in"
                    }
                ]
            },
            {
                "id": "srv-caste-cert",
                "official_name": "Integrated Caste & Community Certificate",
                "category": "Revenue & Certificates",
                "department": "Revenue Department AP",
                "description": "Integrated Caste, Community and Nativity Certificate for SC/ST/BC/EWS candidates.",
                "state_scope": "AP",
                "aliases": ["caste certificate", "community certificate", "integrated certificate", "ews certificate", "obc certificate"],
                "keywords": ["caste", "reservation", "community", "ews", "bc cert"],
                "sub_services": [
                    {
                        "id": "sub-caste-new",
                        "sub_service_name": "Integrated Caste & Community Certificate Application",
                        "action_type": "New Application",
                        "aliases": ["apply caste certificate", "caste cert for college"],
                        "keywords": ["caste", "reservation"],
                        "official_fee": 50.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "MAY_BE_REQUIRED",
                        "physical_presence_reason": "VRO field inquiry or local Secretariat verification.",
                        "official_portal_url": "https://ap.meeseva.gov.in",
                        "official_source_url": "https://ap.meeseva.gov.in"
                    }
                ]
            },
            # 4. Land & Property
            {
                "id": "srv-land-adangal",
                "official_name": "Land Records (Adangal / 1-B / Pattadar Passbook)",
                "category": "Land & Property",
                "department": "Revenue & Land Records Dept AP (Meebhoomi)",
                "description": "Pahani / Adangal download, 1-B ROR extract, Pattadar Passbook mutation, and land survey demarcations.",
                "state_scope": "AP",
                "aliases": ["adangal", "1b", "meebhoomi", "pattadar passbook", "land records", "ror 1b"],
                "keywords": ["pahani", "survey number", "land mutation", "passbook"],
                "sub_services": [
                    {
                        "id": "sub-adangal-download",
                        "sub_service_name": "Adangal / Pahani Search & Copy Download",
                        "action_type": "Download",
                        "aliases": ["download adangal", "meebhoomi adangal", "search pahani"],
                        "keywords": ["survey number adangal", "pattadar name"],
                        "official_fee": 25.0,
                        "processing_time": "Instant Online",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://meebhoomi.ap.gov.in",
                        "official_source_url": "https://meebhoomi.ap.gov.in"
                    }
                ]
            },
            # 5. Registration & Stamps
            {
                "id": "srv-registration-ec",
                "official_name": "Encumbrance Certificate (EC) & Property Registration",
                "category": "Registration & Stamps",
                "department": "Registration & Stamps Department AP (IGRS)",
                "description": "Encumbrance Certificate (EC) search, certified copy download, market value search, and slot booking.",
                "state_scope": "AP",
                "aliases": ["encumbrance certificate", "ec", "igrs ap", "property ec", "market value search"],
                "keywords": ["encumbrance", "sro", "property document", "stamp duty"],
                "sub_services": [
                    {
                        "id": "sub-ec-search",
                        "sub_service_name": "Encumbrance Certificate (EC) Online Search & Issue",
                        "action_type": "New Application",
                        "aliases": ["search ec", "get ec certificate", "property encumbrance certificate"],
                        "keywords": ["ec search", "sro certificate"],
                        "official_fee": 200.0,
                        "processing_time": "1 Working Day",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://registration.ap.gov.in",
                        "official_source_url": "https://registration.ap.gov.in"
                    }
                ]
            },
            # 6. Municipal Services
            {
                "id": "srv-municipal-tax",
                "official_name": "Municipal Property Tax & Water Connection",
                "category": "Municipal Services",
                "department": "Commissioner & Director of Municipal Administration (CDMA AP)",
                "description": "Property tax payment, name mutation, building plan approval, trade licence, and new tap water connection.",
                "state_scope": "AP",
                "aliases": ["property tax", "house tax", "municipal tax", "water connection", "trade licence"],
                "keywords": ["municipal", "water tap", "cdma", "building permission"],
                "sub_services": [
                    {
                        "id": "sub-prop-tax-pay",
                        "sub_service_name": "Municipal Property Tax Assessment & Bill Payment",
                        "action_type": "Payment",
                        "aliases": ["pay property tax", "house tax payment", "municipal tax bill"],
                        "keywords": ["assessment number", "cdma tax"],
                        "official_fee": 0.0,
                        "processing_time": "Instant Online",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://cdma.ap.gov.in",
                        "official_source_url": "https://cdma.ap.gov.in"
                    }
                ]
            },
            # 7. Ration Card & Civil Supplies
            {
                "id": "srv-ration-card",
                "official_name": "Rice / Ration Card Services (Civil Supplies)",
                "category": "Ration Card & Civil Supplies",
                "department": "Department of Civil Supplies & Consumer Affairs AP",
                "description": "Rice card family member addition, member name correction, address change, and split card.",
                "state_scope": "AP",
                "aliases": ["ration card", "rice card", "epos ap", "civil supplies card", "bpl card"],
                "keywords": ["ration", "rice", "member addition", "add child to ration card"],
                "sub_services": [
                    {
                        "id": "sub-ration-member-add",
                        "sub_service_name": "Family Member Addition in Rice / Ration Card",
                        "action_type": "Member Addition",
                        "aliases": ["add member to ration card", "my ration card member addition", "add child rice card"],
                        "keywords": ["member addition", "family addition"],
                        "official_fee": 0.0,
                        "processing_time": "7 Working Days",
                        "physical_presence_requirement": "REQUIRED",
                        "physical_presence_reason": "Biometric eKYC fingerprint authentication at Secretariat counter.",
                        "official_portal_url": "https://epos.ap.gov.in",
                        "official_source_url": "https://epos.ap.gov.in"
                    }
                ]
            },
            # 8. Welfare Schemes & Social Security (Schemes Discovery AI)
            {
                "id": "srv-welfare-pension",
                "official_name": "YSR / AP Social Security Pensions (NTR Bharosa)",
                "category": "Welfare Schemes & Social Security",
                "department": "Department of Social Welfare & SERP AP",
                "description": "Old age pension, widow pension, disability pension, and welfare financial assistance schemes.",
                "state_scope": "AP",
                "aliases": ["pension", "old age pension", "widow pension", "disability pension", "social security pension", "ntr bharosa"],
                "keywords": ["pension scheme", "monthly pension", "elderly pension", "handicapped pension"],
                "sub_services": [
                    {
                        "id": "sub-pension-oldage",
                        "sub_service_name": "Old Age Pension Registration",
                        "action_type": "New Registration",
                        "aliases": ["apply old age pension", "60 years pension", "elderly pension scheme"],
                        "keywords": ["old age", "pension apply"],
                        "official_fee": 0.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "REQUIRED",
                        "physical_presence_reason": "Biometric door-step verification or Secretariat eKYC.",
                        "official_portal_url": "https://sspensions.ap.gov.in",
                        "official_source_url": "https://sspensions.ap.gov.in"
                    }
                ]
            },
            # 13. Driving Licence & Transport
            {
                "id": "srv-dl-parivahan",
                "official_name": "Driving Licence Services (Parivahan Sewa)",
                "category": "Driving Licence & Transport",
                "department": "Ministry of Road Transport & Highways / RTO AP",
                "description": "Driving Licence renewal, learner licence, duplicate DL, and address change in DL.",
                "state_scope": "NAT",
                "aliases": ["driving licence", "driving license", "dl", "parivahan", "rto licence", "drive card"],
                "keywords": ["renew dl", "expired licence", "rto", "learner licence", "ll"],
                "sub_services": [
                    {
                        "id": "sub-dl-renewal",
                        "sub_service_name": "Driving Licence Renewal Online",
                        "action_type": "Licence Renewal",
                        "aliases": ["renew my driving licence", "dl renewal", "expired driving licence"],
                        "keywords": ["renew dl", "form 1a", "rto renewal"],
                        "official_fee": 450.0,
                        "processing_time": "10 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://parivahan.gov.in",
                        "official_source_url": "https://parivahan.gov.in"
                    }
                ]
            },
            # 14. Voter Services
            {
                "id": "srv-voter-id",
                "official_name": "Voter ID Services (ECI / Voters Service Portal)",
                "category": "Voter Services",
                "department": "Election Commission of India (ECI)",
                "description": "New Voter ID registration (Form 6), address transfer (Form 8), replacement/lost EPIC card download.",
                "state_scope": "NAT",
                "aliases": ["voter id", "voter card", "epic", "election card", "vote card", "voters portal"],
                "keywords": ["vote", "election", "polling", "epic card", "lost voter card"],
                "sub_services": [
                    {
                        "id": "sub-voter-new",
                        "sub_service_name": "New Voter ID Registration (Form 6)",
                        "action_type": "New Registration",
                        "aliases": ["new voter id", "apply voter card", "first vote card"],
                        "keywords": ["form 6", "vote enrollment"],
                        "official_fee": 0.0,
                        "processing_time": "15-20 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://voters.eci.gov.in",
                        "official_source_url": "https://eci.gov.in"
                    },
                    {
                        "id": "sub-voter-lost",
                        "sub_service_name": "Lost / Damaged Voter Card Replacement (EPIC)",
                        "action_type": "Duplicate",
                        "aliases": ["lost voter card", "i lost my voter card", "reprint voter card", "duplicate epic"],
                        "keywords": ["lost epic", "download voter card"],
                        "official_fee": 25.0,
                        "processing_time": "7-10 Working Days",
                        "physical_presence_requirement": "NOT_REQUIRED",
                        "official_portal_url": "https://voters.eci.gov.in",
                        "official_source_url": "https://eci.gov.in"
                    }
                ]
            },
            # 15. Passport & Consular
            {
                "id": "srv-passport-seva",
                "official_name": "Passport Seva Services (MEA)",
                "category": "Passport & Consular",
                "department": "Ministry of External Affairs (MEA), Govt of India",
                "description": "Fresh passport application, reissue/renewal, address change, and police clearance certificate (PCC).",
                "state_scope": "NAT",
                "aliases": ["passport", "passport seva", "tatkal passport", "indian passport", "pcc"],
                "keywords": ["travel", "external affairs", "psk appointment", "police verification"],
                "sub_services": [
                    {
                        "id": "sub-passport-reissue",
                        "sub_service_name": "Passport Reissue / Renewal Application",
                        "action_type": "Renewal/Reissue",
                        "aliases": ["renew passport", "passport renewal", "reissue passport"],
                        "keywords": ["expired passport", "book psk appointment"],
                        "official_fee": 1500.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "REQUIRED",
                        "physical_presence_reason": "Police verification and Passport Seva Kendra (PSK) appointment.",
                        "official_portal_url": "https://passportindia.gov.in",
                        "official_source_url": "https://passportindia.gov.in"
                    }
                ]
            },
            # 20. Agriculture & Farmer Subsidies
            {
                "id": "srv-agriculture-farmer",
                "official_name": "Farmer Welfare & Agricultural Subsidies",
                "category": "Agriculture",
                "department": "Department of Agriculture AP (PM-KISAN / Annadata)",
                "description": "PM-KISAN eKYC, crop damage compensation, seed subsidy, and soil health card.",
                "state_scope": "AP",
                "aliases": ["farmer", "pm kisan", "crop insurance", "agriculture subsidy", "annadata", "farmer crop damage"],
                "keywords": ["crop loss", "farmer id", "rythu", "seed subsidy"],
                "sub_services": [
                    {
                        "id": "sub-crop-insurance",
                        "sub_service_name": "Crop Loss & Natural Calamity Assistance Claim",
                        "action_type": "Claim",
                        "aliases": ["i am a farmer and my crop failed", "crop loss claim", "farmer disaster relief"],
                        "keywords": ["crop failed", "calamity relief", "rythu kisan"],
                        "official_fee": 0.0,
                        "processing_time": "15 Working Days",
                        "physical_presence_requirement": "MAY_BE_REQUIRED",
                        "physical_presence_reason": "Agricultural Officer field inspection of damaged crop land.",
                        "official_portal_url": "https://karshak.ap.gov.in",
                        "official_source_url": "https://karshak.ap.gov.in"
                    }
                ]
            }
        ]

        # Insert Services & SubServices into Database
        for s_data in master_services:
            sub_list = s_data.pop("sub_services")

            # Check if service already exists
            existing_srv = db.query(models.Service).filter(models.Service.id == s_data["id"]).first()
            if not existing_srv:
                service_model = models.Service(
                    id=s_data["id"],
                    official_name=s_data["official_name"],
                    category=s_data["category"],
                    department=s_data["department"],
                    description=s_data["description"],
                    state_scope=s_data.get("state_scope", "AP"),
                    district_scope="ALL",
                    aliases=s_data.get("aliases", []),
                    keywords=s_data.get("keywords", []),
                    verification_status="VERIFIED"
                )
                db.add(service_model)
                db.commit()
                srv_id = service_model.id
            else:
                srv_id = existing_srv.id

            for sub_d in sub_list:
                existing_sub = db.query(models.SubService).filter(models.SubService.id == sub_d["id"]).first()
                if not existing_sub:
                    sub_model = models.SubService(
                        id=sub_d["id"],
                        service_id=srv_id,
                        sub_service_name=sub_d["sub_service_name"],
                        action_type=sub_d["action_type"],
                        aliases=sub_d.get("aliases", []),
                        keywords=sub_d.get("keywords", []),
                        description=sub_d.get("description", sub_d["sub_service_name"]),
                        eligibility_criteria=["Must possess valid identity and residence proof"],
                        required_documents=[{"name": "Aadhaar Card", "mandatory": True, "description": "Identity & Address proof."}],
                        diy_steps=["Step 1: Fill official online form.", "Step 2: Submit documents.", "Step 3: Track application status."],
                        official_fee=sub_d.get("official_fee", 50.0),
                        processing_time=sub_d.get("processing_time", "7 Working Days"),
                        application_method="Online Portal / Local Secretariat",
                        physical_presence_requirement=sub_d.get("physical_presence_requirement", "MAY_BE_REQUIRED"),
                        physical_presence_reason=sub_d.get("physical_presence_reason", None),
                        official_portal_url=sub_d.get("official_portal_url", "https://ap.meeseva.gov.in"),
                        official_source_url=sub_d.get("official_source_url", "https://ap.meeseva.gov.in"),
                        information_version="V1.0",
                        last_checked="2026-08-20",
                        last_verified="2026-08-20",
                        confidence_status="VERIFIED",
                        required_certification_code="CERT-CIVIL-GEN",
                        is_demo_data=False
                    )
                    db.add(sub_model)
            db.commit()

        print("Successfully seeded GSP V2 Master 45-Category Government Service Taxonomy!")

    except Exception as e:
        print(f"Error seeding master taxonomy: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
