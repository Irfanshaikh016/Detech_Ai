import uuid
from typing import Dict, Any

MOCK_CASES = {
    "Easy": {
        "id": "case_easy_101",
        "title": "The Vanishing Ruby at Blackwood Manor",
        "crime_type": "Theft",
        "difficulty": "Easy",
        "summary": "During Lord Blackwood's 60th birthday gala, a priceless 50-carat ruby vanished from the vault inside his study. The security system was bypassed without alarm.",
        "victim": {
            "name": "Lord Reginald Blackwood",
            "occupation": "Art Collector & Billionaire",
            "background": "Wealthy industrialist who bought the Crimson Heart Ruby at auction 2 weeks ago."
        },
        "ground_truth": {
            "criminal_id": "suspect_1",
            "criminal_name": "Arthur Pendelton",
            "motive": "Facing bankruptcy due to illegal gambling debts; needed the ruby to pay off syndicate loans.",
            "how_it_was_done": "Used stolen vault keycard during the toast speeches when the study was left unattended for 15 minutes.",
            "smoking_gun_evidence": "ev_2" # CCTV showing cufflink drop
        },
        "locations": [
            {
                "id": "loc_1",
                "name": "The Grand Study & Vault",
                "description": "A high-ceilinged room lined with old leather books. The heavy steel vault sits wide open.",
                "evidence_ids": ["ev_1", "ev_2"]
            },
            {
                "id": "loc_2",
                "name": "Gala Ballroom",
                "description": "Lively hall filled with crystal chandeliers, half-filled champagne glasses, and silver platters.",
                "evidence_ids": ["ev_3"]
            },
            {
                "id": "loc_3",
                "name": "Garden Terrace",
                "description": "Dark stone walkway overlooking the fog-covered estate grounds.",
                "evidence_ids": ["ev_4", "ev_5"]
            }
        ],
        "evidence": [
            {
                "id": "ev_1",
                "name": "Bypassed Electronic Vault Keypad",
                "category": "Cybercrime / Access Logs",
                "location": "The Grand Study & Vault",
                "description": "Keycard log shows access granted at 9:14 PM using Security Manager Arthur Pendelton's master card.",
                "relevance": "Key evidence linking vault entry to Arthur."
            },
            {
                "id": "ev_2",
                "name": "Engraved Monogrammed Cufflink",
                "category": "Fingerprints / Physical",
                "location": "The Grand Study & Vault",
                "description": "A silver cufflink with initials 'A.P.' discovered under the vault cabinet door.",
                "relevance": "Smoking gun evidence left by the thief!"
            },
            {
                "id": "ev_3",
                "name": "Champagne Service Schedule",
                "category": "Witness Statements",
                "location": "Gala Ballroom",
                "description": "Head waiter states Arthur disappeared from the main hall between 9:10 PM and 9:25 PM.",
                "relevance": "Breaks Arthur's alibi of being at the bar continuously."
            },
            {
                "id": "ev_4",
                "name": "Overheard Phone Conversation Log",
                "category": "Phone Call Logs",
                "location": "Garden Terrace",
                "description": "Audio snippet of a man whispering: 'I've got the rock... wire the funds to Cayman now.'",
                "relevance": "Confirms financial desperation motive."
            },
            {
                "id": "ev_5",
                "name": "Muddy Boot Prints",
                "category": "Fingerprints / Footprints",
                "location": "Garden Terrace",
                "description": "Size 11 boot prints leading from the terrace toward the side alley exit.",
                "relevance": "Matches Arthur Pendelton's boot size."
            }
        ],
        "suspects": [
            {
                "id": "suspect_1",
                "name": "Arthur Pendelton",
                "occupation": "Head Security Manager",
                "relationship": "Employee / Trusted Security Chief",
                "personality": "Nervous, overly formal, sweating profusely when pressed on timing.",
                "alibi": "Claims he was supervising the open bar in the Ballroom all evening.",
                "secret": "Owes $500,000 to loan sharks after a ruined casino trip in Macau.",
                "motive": "Stole ruby to sell on the black market to pay off life-threatening debts.",
                "stress_level": "Nervous"
            },
            {
                "id": "suspect_2",
                "name": "Evelyn Vance",
                "occupation": "Lead Curator & Antique Dealer",
                "relationship": "Business partner who brokered the ruby purchase",
                "personality": "Sharp, haughty, defensive of her professional reputation.",
                "alibi": "Claims she was giving a lecture on gemstone history to guests in the lounge.",
                "secret": "Appraised the ruby for 20% less than true value to get a cut.",
                "motive": "Resented Lord Blackwood for underpaying her commission.",
                "stress_level": "Calm"
            },
            {
                "id": "suspect_3",
                "name": "Julian Blackwood",
                "occupation": "Victim's Estranged Son",
                "relationship": "Disinherited Heir",
                "personality": "Cynical, rebellious, sarcastic.",
                "alibi": "Was drinking heavily out on the Garden Terrace.",
                "secret": "Attempted to cut out off-duty security wires earlier that morning.",
                "motive": "Wants his inheritance before his father cut him out of the will completely.",
                "stress_level": "Defensive"
            }
        ],
        "hints": [
            "Hint 1: Check the electronic keycard access logs in the Grand Study & Vault.",
            "Hint 2: Compare Arthur Pendelton's alibi about staying at the bar against the waiter's champagne service log.",
            "Hint 3: Look for physical evidence left behind near the vault cabinet door matching someone's initials."
        ]
    }
}

def get_mock_case(difficulty: str, crime_type: str) -> Dict[str, Any]:
    """Offline fallback used only when the Gemini API call fails.

    NOTE: only an "Easy" template currently exists, so Medium/Hard requests
    fall back to this same story. It used to also silently relabel that case
    as the requested difficulty, which was misleading — now it's stamped
    honestly as "Easy" so the UI never lies about how many suspects/clues to
    expect. Once GEMINI_API_KEY is valid, real per-difficulty generation
    takes over automatically and this fallback isn't used.
    """
    base = MOCK_CASES.get(difficulty, MOCK_CASES["Easy"])
    case_copy = json_deepcopy(base)
    case_copy["id"] = f"case_{uuid.uuid4().hex[:8]}"
    case_copy["difficulty"] = "Easy" if difficulty not in MOCK_CASES else difficulty
    case_copy["is_fallback"] = True
    if crime_type and crime_type != "Any":
        case_copy["crime_type"] = crime_type
    return case_copy

def json_deepcopy(d):
    import json
    return json.loads(json.dumps(d))
