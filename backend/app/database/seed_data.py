from datetime import datetime
import json
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.family import FamilyMember, EmergencyContact
from app.models.consent import UserConsent
from app.models.government import GovernmentScheme
from app.models.human_help import Helper


def seed_database_if_empty(db: Session) -> None:
    """Populates essential initial data: verified Kerala government schemes, verified helpers, and demo user."""
    
    # 1. Seed Government Schemes
    existing_schemes = db.query(GovernmentScheme).first()
    if not existing_schemes:
        schemes = [
            GovernmentScheme(
                id="kerala-old-age-pension",
                name="Indira Gandhi National Old Age Pension Scheme (IGNOAPS / Sevana)",
                name_ml="ഇന്ദിരാഗാന്ധി ദേശീയ വാർദ്ധക്യകാല പെൻഷൻ (സേവന പെൻഷൻ)",
                category="Senior Citizen",
                description="Monthly financial assistance provided by the Government of Kerala to destitute senior citizens aged 60 and above.",
                description_ml="60 വയസോ അതിൽ കൂടുതലോ പ്രായമുള്ള അർഹരായ മുതിർന്ന പൗരന്മാർക്ക് കേരള സർക്കാർ നൽകുന്ന പ്രതിമാസ ധനസഹായം (പ്രതിമാസം ₹1,600).",
                eligibility_criteria="Applicant must be 60 years or above, permanent resident of Kerala for past 2 years, family income under BPL ceiling (below ₹1,00,000 per year), not receiving any other social welfare pension.",
                benefits="Direct bank transfer of ₹1,600 per month directly credited to the beneficiary's bank account or delivered via primary cooperative societies.",
                required_documents="Aadhaar Card, Proof of Age (Electoral ID / School Certificate), BPL Ration Card / Income Certificate from Village Officer, Bank Account Passbook copy.",
                application_procedure="Apply online via Sevana Welfare Pension portal or submit application offline at the Local Self Government (Grama Panchayat / Municipality / Corporation) office.",
                official_portal_url="https://welfarepension.kerala.gov.in/",
                department="Social Justice Department & Local Self Government Department, Govt of Kerala",
                is_verified=True,
                verified_source_reference="Kerala Social Security Pension Limited (KSSPL) - official portal",
                last_verified_at=datetime.utcnow()
            ),
            GovernmentScheme(
                id="kerala-disability-pension",
                name="Disability Pension (Differently Abled Pension)",
                name_ml="വികലാംഗ പെൻഷൻ (ഭിന്നശേഷി പെൻഷൻ)",
                category="Disability",
                description="State pension scheme for persons with disability of 40% or more who are in financial need.",
                description_ml="40 ശതമാനമോ അതിൽ കൂടുതലോ വൈകല്യമുള്ള അർഹരായ ഭിന്നശേഷിക്കാർക്കായി നൽകുന്ന പ്രതിമാസ പെൻഷൻ (പ്രതിമാസം ₹1,600).",
                eligibility_criteria="Person with disability of 40% or more certified by Medical Board, annual family income should not exceed ₹1,00,000, resident of Kerala.",
                benefits="Monthly pension of ₹1,600 with free access to assistive aids and priority social security benefits.",
                required_documents="Medical Board Disability Certificate, UDID Card, Aadhaar Card, Income Certificate, Bank Passbook, Passport size photograph.",
                application_procedure="Submit application at the respective Village Office or Grama Panchayat / Urban Local Body with Medical Board Certificate.",
                official_portal_url="https://welfarepension.kerala.gov.in/",
                department="Social Justice Department, Govt of Kerala",
                is_verified=True,
                verified_source_reference="Directorate of Social Justice, Government of Kerala",
                last_verified_at=datetime.utcnow()
            ),
            GovernmentScheme(
                id="kerala-vayo-amrutham",
                name="Vayo Amrutham Scheme",
                name_ml="വായോ അമൃതം പദ്ധതി",
                category="Healthcare",
                description="Holistic Ayurvedic health care, regular medical checkups, and medicines for senior citizens in old age homes and local panchayats.",
                description_ml="വൃദ്ധസദനങ്ങളിലെയും തദ്ദേശസ്വയംഭരണ സ്ഥാപനങ്ങളിലെയും മുതിർന്ന പൗരന്മാർക്ക് സൗജന്യ ആയുർവേദ ചികിത്സയും ആരോഗ്യ പരിചരണവും നൽകുന്ന പദ്ധതി.",
                eligibility_criteria="Senior citizens residing in Kerala, with priority for elderly in government care homes and rural communities.",
                benefits="Free Ayurvedic medical consultations, regular health monitoring, herbal medicines for age-related ailments, and lifestyle support.",
                required_documents="Aadhaar Card, Senior Citizen ID card or Age proof.",
                application_procedure="Available at nearest Govt Ayurveda Dispensaries/Hospitals and through Grama Panchayat special health camps.",
                official_portal_url="http://sjd.kerala.gov.in/scheme-info.php?id=MQ==",
                department="Department of Social Justice & Department of AYUSH, Govt of Kerala",
                is_verified=True,
                verified_source_reference="Social Justice Department Portal (sjd.kerala.gov.in)",
                last_verified_at=datetime.utcnow()
            ),
            GovernmentScheme(
                id="kerala-kasp-insurance",
                name="Karunya Arogya Suraksha Padhathi (KASP)",
                name_ml="കാരുണ്യ ആരോഗ്യ സുരക്ഷാ പദ്ധതി (KASP)",
                category="Healthcare",
                description="Comprehensive health insurance cover of up to ₹5 Lakhs per family per year for secondary and tertiary hospitalization care.",
                description_ml="കുടുംബത്തിന് പ്രതിവർഷം ₹5 ലക്ഷം രൂപ വരെയുള്ള കിടത്തിച്ചികിത്സാ പരിരക്ഷ നൽകുന്ന സമഗ്ര സൗജന്യ ആരോഗ്യ ഇൻഷുറൻസ് പദ്ധതി.",
                eligibility_criteria="BPL families, Antyodaya Anna Yojana (AAY) ration cardholders, Priority Household (PHH) cardholders, and enrolled vulnerable groups in Kerala.",
                benefits="Cashless treatment up to ₹5,00,000 annually per family across empanelled government and private hospitals in Kerala.",
                required_documents="Ration Card (Yellow/Pink), Aadhaar Card of family members, KASP Beneficiary ID Card if previously issued.",
                application_procedure="Enrollment facilitated at Akshaya Centers, Taluk Hospitals, and District Hospitals via KASP Kiosk.",
                official_portal_url="https://sha.kerala.gov.in/",
                department="State Health Agency (SHA), Govt of Kerala",
                is_verified=True,
                verified_source_reference="State Health Agency Kerala - official guidelines",
                last_verified_at=datetime.utcnow()
            ),
            GovernmentScheme(
                id="swavlamban-udid-card",
                name="Unique Disability ID (UDID) / Swavlamban",
                name_ml="യുണിക് ഡിസെബിലിറ്റി ഐഡി (UDID) കാർഡ്",
                category="Disability",
                description="National unified identity card for persons with disabilities, enabling transparent access to government concessions and assistive devices.",
                description_ml="ഭിന്നശേഷിക്കാർക്കുള്ള ദേശീയ ഏകീകൃത തിരിച്ചറിയൽ കാർഡ്. സർക്കാർ ആനുകൂല്യങ്ങളും യാത്രാ ഇളവുകളും ലഭിക്കാൻ സഹായിക്കുന്നു.",
                eligibility_criteria="Any Indian citizen with benchmark disability (40% or more) as defined under RPwD Act 2016.",
                benefits="Universal single-document recognition for travel concessions (KSRTC, Railways), assistive aids, pensions, and educational reservations.",
                required_documents="Disability Certificate from Medical Authority, Proof of Identity (Aadhaar), Proof of Address, Passport Photograph, Signature/Thumb impression.",
                application_procedure="Apply online at www.swavlambancard.gov.in or via nearest Akshaya e-Center.",
                official_portal_url="https://www.swavlambancard.gov.in/",
                department="Department of Empowerment of Persons with Disabilities, Govt of India / Social Justice Dept Kerala",
                is_verified=True,
                verified_source_reference="Swavlamban Portal - Ministry of Social Justice and Empowerment",
                last_verified_at=datetime.utcnow()
            ),
            GovernmentScheme(
                id="kerala-vayomadhuram",
                name="Vayomadhuram Scheme",
                name_ml="വയോമധുരം പദ്ധതി",
                category="Senior Citizen",
                description="Supply of free digital glucometers and testing strips to elderly diabetic patients belonging to BPL families in Kerala.",
                description_ml="ബി.പി.എൽ വിഭാഗത്തിലെ പ്രമേഹബാധിതരായ മുതിർന്ന പൗരന്മാർക്ക് സൗജന്യ ഗ്ലൂക്കോമീറ്ററും സ്ട്രിപ്പുകളും നൽകുന്ന പദ്ധതി.",
                eligibility_criteria="Senior citizens aged 60 and above, belonging to BPL category, diagnosed with diabetes mellitus.",
                benefits="Free digital glucometer device along with testing strips for regular home blood sugar monitoring.",
                required_documents="Aadhaar Card, BPL Ration Card, Medical prescription/Doctor's certificate showing diabetes diagnosis.",
                application_procedure="Submit application through the nearest District Social Justice Office (DSJO) or via Suneethi portal.",
                official_portal_url="http://sjd.kerala.gov.in/scheme-info.php?id=Mzc=",
                department="Social Justice Department, Govt of Kerala",
                is_verified=True,
                verified_source_reference="Social Justice Department Kerala - Vayomadhuram guidelines",
                last_verified_at=datetime.utcnow()
            ),
        ]
        db.add_all(schemes)
        db.commit()

    # 2. Seed Verified Helpers
    existing_helpers = db.query(Helper).first()
    if not existing_helpers:
        helpers = [
            Helper(
                id="helper-tvm-01",
                name="Anitha S. Nair",
                phone_number="+91-9847012345",
                email="anitha.kudumbashree@example.com",
                district="Thiruvananthapuram",
                panchayat_or_locality="Pattom / Kazhakkoottam",
                category="Kudumbashree Volunteer",
                skills=json.dumps(["Malayalam Native", "Wheelchair Support", "Govt Office Escort", "Medicine Delivery"]),
                is_verified=True,
                verification_badge="Kudumbashree Verified CDS-TVM",
                rating=4.95,
                completed_tasks_count=34,
                is_available=True
            ),
            Helper(
                id="helper-ekm-02",
                name="Rahul V. Kurup",
                phone_number="+91-9847023456",
                email="rahul.nss@example.com",
                district="Ernakulam",
                panchayat_or_locality="Kakkanad / Edappally",
                category="NSS Volunteer",
                skills=json.dumps(["Malayalam Native", "Smartphone & Digital App Help", "Hospital Navigation", "Bank Visit Support"]),
                is_verified=True,
                verification_badge="NSS Kerala State Cell Verified",
                rating=4.88,
                completed_tasks_count=21,
                is_available=True
            ),
            Helper(
                id="helper-clt-03",
                name="Fathima Zahra",
                phone_number="+91-9847034567",
                email="fathima.vol@example.com",
                district="Kozhikode",
                panchayat_or_locality="Mananchira / Beypore",
                category="Healthcare Worker",
                skills=json.dumps(["Malayalam Native", "Basic First Aid", "Geriatric Care", "Doctor Appointment Escort"]),
                is_verified=True,
                verification_badge="Kerala Health Mission Volunteer",
                rating=4.92,
                completed_tasks_count=42,
                is_available=True
            ),
            Helper(
                id="helper-tsr-04",
                name="M. Vishnu Prasad",
                phone_number="+91-9847045678",
                email="vishnu.tsr@example.com",
                district="Thrissur",
                panchayat_or_locality="Round North / Ollur",
                category="Volunteer",
                skills=json.dumps(["Malayalam Native", "Ration Shop & Grocery Help", "Pension Office Escort"]),
                is_verified=True,
                verification_badge="District Social Justice Registry Verified",
                rating=4.79,
                completed_tasks_count=18,
                is_available=True
            )
        ]
        db.add_all(helpers)
        db.commit()

    # 3. Seed Demo User & Family / Emergency Contacts
    existing_user = db.query(User).filter(User.phone_number == "+91-9447100000").first()
    if not existing_user:
        demo_user = User(
            id="demo-user-kerala-01",
            full_name="K. Madhavan Nair",
            phone_number="+91-9447100000",
            preferred_language="ml",
            district="Thiruvananthapuram",
            panchayat_or_municipality="Neyyattinkara",
            is_senior_citizen=True,
            is_differently_abled=False,
            disability_type=None,
            accessibility_notes="Prefers large Malayalam audio voice prompts and high contrast buttons."
        )
        db.add(demo_user)
        db.commit()

        # Add Family Member (Son)
        family_member = FamilyMember(
            id="family-praveen-01",
            user_id=demo_user.id,
            name="Praveen Nair",
            relationship="Son",
            phone_number="+91-9847111222",
            email="praveen.nair@example.com",
            is_primary_caregiver=True,
            can_view_activity=False,  # Privacy default: NO access without consent!
            can_manage_requests=True
        )
        db.add(family_member)

        # Add Emergency Contact (Daughter - Doctor)
        emergency_contact = EmergencyContact(
            id="emg-radhika-01",
            user_id=demo_user.id,
            name="Dr. Radhika Nair",
            relationship="Daughter",
            phone_number="+91-9847333444",
            priority_order=1,
            is_sos_active=True
        )
        db.add(emergency_contact)

        # Add explicitly granted consent for emergency assistance
        emergency_consent = UserConsent(
            id="consent-emg-01",
            user_id=demo_user.id,
            grantee_id=family_member.id,
            grantee_type="family_member",
            scope="manage_requests",
            is_granted=True,
            granted_at=datetime.utcnow(),
            notes="Authorized son Praveen to request helper and transport assistance on behalf of user."
        )
        db.add(emergency_consent)
        db.commit()
