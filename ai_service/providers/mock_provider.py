"""
Deterministic mock provider for offline hackathon testing and fallback.
Ensures zero-crash development when external API keys or network are not available.
"""

from typing import Any, Dict, List, Optional
from ..schemas import VerifiedExcerpt


class MockProvider:
    """Provides contract-compliant mock responses for Kerala Accessibility Assistant."""

    def generate(
        self,
        user_text: str,
        module: str,
        language: str,
        verified_context: Optional[List[VerifiedExcerpt]] = None,
    ) -> Dict[str, Any]:
        is_ml = language == "ml"
        user_lower = user_text.lower()

        # Check for hazardous everyday tasks
        hazardous_keywords = [
            "gas", "wire", "electric", "climb", "roof", "medicine", "pill",
            "തീ", "ഗ്യാസ്", "വൈദ്യുതി", "ഷോക്ക്", "മരുന്ന്"
        ]
        is_hazardous = any(k in user_lower for k in hazardous_keywords)

        if module == "government_services":
            if verified_context:
                used_ids = [v.id for v in verified_context[:2]]
                context_summary = " ".join([v.text[:80] for v in verified_context[:2]])
                if is_ml:
                    return {
                        "language": "ml",
                        "module": "government_services",
                        "reply": f"ലഭ്യമായ വിവരങ്ങൾ പ്രകാരം: {context_summary}...",
                        "steps": ["കൂടുതൽ വിവരങ്ങൾക്ക് അടുത്തുള്ള അക്ഷയ കേന്ദ്രം സന്ദർശിക്കുക."],
                        "warnings": [],
                        "source_refs": used_ids,
                        "needs_human_help": False,
                        "follow_up_question": "അപേക്ഷാ സമർപ്പണത്തിൽ സഹായം ആവശ്യമുണ്ടോ?",
                    }
                else:
                    return {
                        "language": "en",
                        "module": "government_services",
                        "reply": f"According to verified government records: {context_summary}...",
                        "steps": ["Visit your nearest Akshaya Centre or Grama Panchayat office for formal verification."],
                        "warnings": [],
                        "source_refs": used_ids,
                        "needs_human_help": False,
                        "follow_up_question": "Would you like help locating your nearest Akshaya Centre?",
                    }
            else:
                if is_ml:
                    return {
                        "language": "ml",
                        "module": "government_services",
                        "reply": "ഈ സേവനത്തെക്കുറിച്ചുള്ള ഔദ്യോഗിക വിവരങ്ങൾ നിലവിൽ സ്ഥിരീകരിക്കാൻ കഴിഞ്ഞിട്ടില്ല. കൃത്യത ഉറപ്പാക്കാൻ ദയവായി അക്ഷയ കേന്ദ്രവുമായോ ബന്ധപ്പെട്ട ഓഫീസുമായോ സംസാരിക്കുക.",
                        "steps": ["അടുത്തുള്ള അക്ഷയ കേന്ദ്രം സന്ദർശിക്കുക അല്ലെങ്കിൽ ഔദ്യോഗിക ഹെൽപ്പ്‌ലൈനിൽ വിളിക്കുക."],
                        "warnings": ["സ്ഥിരീകരിച്ച രേഖകൾ ലഭ്യമല്ലാത്തതിനാൽ സ്വന്തമായി നടപടികൾ സ്വീകരിക്കരുത്."],
                        "source_refs": [],
                        "needs_human_help": True,
                        "follow_up_question": None,
                    }
                else:
                    return {
                        "language": "en",
                        "module": "government_services",
                        "reply": "The exact details for this government service cannot be confirmed at this moment without verified records. Please check with an official service or trusted human.",
                        "steps": ["Visit your nearest Akshaya Centre or contact your local Grama Panchayat."],
                        "warnings": ["Details could not be independently verified from official government excerpts."],
                        "source_refs": [],
                        "needs_human_help": True,
                        "follow_up_question": None,
                    }

        elif module == "digital_safety":
            if is_ml:
                return {
                    "language": "ml",
                    "module": "digital_safety",
                    "reply": "ഈ സന്ദേശത്തിൽ തിടുക്കം കൂട്ടുന്നതും സംശയാസ്പദവുമായ ലക്ഷണങ്ങൾ കാണുന്നുണ്ട്. ഒടിപി, പാസ്‌വേഡ്, അല്ലെങ്കിൽ ബാങ്ക് വിവരങ്ങൾ ഒരിക്കലും ആരുമായും പങ്കുവെക്കരുത്.",
                    "steps": [
                        "അപരിചിത ലിങ്കുകളിൽ ക്ലിക്ക് ചെയ്യരുത്.",
                        "സംശയമുണ്ടെങ്കിൽ ബാങ്കിന്റെ ഔദ്യോഗിക ശാഖയുമായി നേരിട്ട് ബന്ധപ്പെടുക.",
                        "സാമ്പത്തിക തട്ടിപ്പ് സംശയിക്കുന്നുവെങ്കിൽ 1930 എന്ന സൈബർ ഹെൽപ്പ്‌ലൈനിൽ വിളിക്കുക."
                    ],
                    "warnings": ["ഇത് വ്യാജമാണോ അല്ലയോ എന്ന് ഉറപ്പിച്ചു പറയാൻ കഴിയില്ല; ജാഗ്രത പാലിക്കുക."],
                    "source_refs": [],
                    "needs_human_help": False,
                    "follow_up_question": "ഈ സന്ദേശം എവിടെ നിന്നാണ് ലഭിച്ചത്?",
                }
            else:
                return {
                    "language": "en",
                    "module": "digital_safety",
                    "reply": "This message displays common warning signs of an unverified request. Never share an OTP, password, PIN, or banking credentials with anyone.",
                    "steps": [
                        "Do not click on links sent from unknown numbers.",
                        "Verify directly with your official bank branch or customer service number.",
                        "If you suspect fraud, call the National Cyber Crime Helpline at 1930."
                    ],
                    "warnings": ["This message cannot be verified as genuine; please proceed with caution."],
                    "source_refs": [],
                    "needs_human_help": False,
                    "follow_up_question": "Did this message ask you to transfer money or share a code?",
                }

        elif module == "everyday_tasks":
            if is_hazardous:
                if is_ml:
                    return {
                        "language": "ml",
                        "module": "everyday_tasks",
                        "reply": "ഇത് അപകടനടപടിക്ക് സാധ്യതയുള്ള കാര്യമായതിനാൽ ദയവായി സ്വയം ചെയ്യാൻ ശ്രമിക്കരുത്. വിശ്വസ്തനായ ഒരു കുടുംബാംഗത്തിന്റെയോ ടെക്നീഷ്യന്റെയോ സഹായം തേടാൻ നിർദ്ദേശിക്കുന്നു.",
                        "steps": ["ഉപകരണം സ്വിച്ച് ഓഫ് ചെയ്യുക.", "വിശ്വസ്തനായ ഒരു സഹായിയെ വിളിക്കുക."],
                        "warnings": ["സ്വയം റിപ്പയർ ചെയ്യാൻ ശ്രമിക്കുന്നത് സുരക്ഷിതമല്ല."],
                        "source_refs": [],
                        "needs_human_help": True,
                        "follow_up_question": None,
                    }
                else:
                    return {
                        "language": "en",
                        "module": "everyday_tasks",
                        "reply": "Because this task involves potential hazards, please pause and do not attempt it alone. We recommend asking a trusted family member or certified professional.",
                        "steps": ["Step back safely from the appliance or area.", "Contact a trusted family member or qualified technician."],
                        "warnings": ["Attempting hazardous tasks without assistance carries risk."],
                        "source_refs": [],
                        "needs_human_help": True,
                        "follow_up_question": None,
                    }
            else:
                if is_ml:
                    return {
                        "language": "ml",
                        "module": "everyday_tasks",
                        "reply": "നിങ്ങളുടെ ചോദ്യത്തിന് ലളിതമായ നിർദ്ദേശങ്ങൾ താഴെ നൽകുന്നു.",
                        "steps": [
                            "ആദ്യം നിങ്ങളുടെ ഫോൺ അല്ലെങ്കിൽ ഉപകരണം ഓൺ ചെയ്യുക.",
                            "തുടർന്ന് ആവശ്യമായ ആപ്പ് തുറക്കുക."
                        ],
                        "warnings": [],
                        "source_refs": [],
                        "needs_human_help": False,
                        "follow_up_question": "അടുത്ത പടി കാണിച്ചു തരേണ്ടതുണ്ടോ?",
                    }
                else:
                    return {
                        "language": "en",
                        "module": "everyday_tasks",
                        "reply": "Here are simple, step-by-step instructions for your request.",
                        "steps": [
                            "Turn on your device screen.",
                            "Locate and tap the required application icon."
                        ],
                        "warnings": [],
                        "source_refs": [],
                        "needs_human_help": False,
                        "follow_up_question": "Would you like help with the next step?",
                    }

        elif module == "family_support":
            if is_ml:
                return {
                    "language": "ml",
                    "module": "family_support",
                    "reply": "കുടുംബാംഗങ്ങളുമായി ബന്ധപ്പെടാനും സുരക്ഷിതമായിരിക്കാനും സഹായിക്കുന്ന വിവരങ്ങൾ താഴെ നൽകുന്നു.",
                    "steps": [
                        "മരുന്ന് കഴിക്കുന്ന സമയം മുൻകൂട്ടി നിശ്ചയിക്കുക.",
                        "അത്യാവശ്യ ഫോൺ നമ്പറുകൾ എളുപ്പത്തിൽ എടുക്കാവുന്നിടത്ത് സൂക്ഷിക്കുക."
                    ],
                    "warnings": [],
                    "source_refs": [],
                    "needs_human_help": False,
                    "follow_up_question": "കുടുംബാംഗങ്ങൾക്ക് സന്ദേശം അയക്കാൻ സഹായിക്കണോ?",
                }
            else:
                return {
                    "language": "en",
                    "module": "family_support",
                    "reply": "Here is gentle guidance to help keep you and your family caregivers connected.",
                    "steps": [
                        "Keep your essential emergency contact numbers written near the phone.",
                        "Set daily check-in times with your family or caregiver."
                    ],
                    "warnings": [],
                    "source_refs": [],
                    "needs_human_help": False,
                    "follow_up_question": "Would you like to compose a quick message to your family member?",
                }

        else:  # human_help
            if is_ml:
                return {
                    "language": "ml",
                    "module": "human_help",
                    "reply": "സഹായത്തിനായി അടുത്തുള്ള വിശ്വസ്തനായ ഒരു വളണ്ടിയറുമായോ കുടുംബാംഗവുമായോ ബന്ധപ്പെടാൻ നിർദ്ദേശിക്കുന്നു.",
                    "steps": [
                        "അടുത്തുള്ള വാർഡ് മെമ്പറെയോ കുടുംബശ്രീ പ്രവർത്തകരെയോ വിളിക്കാം.",
                        "സഹായത്തിനായി 1077 / 1056 ഹെൽപ്പ്‌ലൈൻ ഉപയോഗിക്കാം."
                    ],
                    "warnings": [],
                    "source_refs": [],
                    "needs_human_help": True,
                    "follow_up_question": None,
                }
            else:
                return {
                    "language": "en",
                    "module": "human_help",
                    "reply": "If you wish, you can connect with a trusted local helper or family member. Assistance is readily available.",
                    "steps": [
                        "You may contact your local Kudumbashree volunteer or Ward member.",
                        "For emergency state assistance, call the official helpline."
                    ],
                    "warnings": [],
                    "source_refs": [],
                    "needs_human_help": True,
                    "follow_up_question": None,
                }

