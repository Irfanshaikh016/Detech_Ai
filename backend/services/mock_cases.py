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
    },
    "Medium": {
        "id": "case_med_202",
        "title": "The Midnight Cyanide Protocol",
        "crime_type": "Murder",
        "difficulty": "Medium",
        "summary": "Dr. Alistair Vance, lead biochemist at Veloce Therapeutics, was discovered slumped over his workstation at 11:30 PM. Toxicological analysis confirmed lethal potassium cyanide introduced into his personal espresso mug.",
        "victim": {
            "name": "Dr. Alistair Vance",
            "occupation": "Lead Biochemical Researcher",
            "background": "Pioneered a breakthrough cancer immunotherapy drug worth billions; notorious for taking sole credit."
        },
        "ground_truth": {
            "criminal_id": "suspect_1",
            "criminal_name": "Dr. Elena Rostova",
            "motive": "Vance was filing for a sole patent on the immunotherapy formula, stealing 5 years of Rostova's primary research.",
            "how_it_was_done": "Acquired potassium cyanide from the chemical cold vault at 10:45 PM and laced Vance's personal coffee canister during the team coffee break.",
            "smoking_gun_evidence": "ev_6"
        },
        "locations": [
            {
                "id": "loc_1",
                "name": "High-Containment Bio Lab 4",
                "description": "Humming centrifuge units, sealed glass fume hoods, and Dr. Vance's desk with a half-drunk espresso mug.",
                "image_type": "office",
                "evidence_ids": ["ev_1", "ev_2"]
            },
            {
                "id": "loc_2",
                "name": "Chemical Cold Storage Vault",
                "description": "Sub-zero refrigerated vault requiring biometrics and logbook signatures to withdraw hazardous compounds.",
                "image_type": "warehouse",
                "evidence_ids": ["ev_3", "ev_6"]
            },
            {
                "id": "loc_3",
                "name": "Executive Lounge & Coffee Station",
                "description": "Staff relaxation area featuring espresso makers, pantry lockers, and shredded internal memos.",
                "image_type": "cafe",
                "evidence_ids": ["ev_4", "ev_5"]
            }
        ],
        "evidence": [
            {
                "id": "ev_1",
                "name": "Cyanide-Laced Espresso Mug",
                "category": "Chemical / Toxicology",
                "location": "High-Containment Bio Lab 4",
                "description": "Residue in ceramic mug contains 350mg of lab-grade potassium cyanide crystal powder.",
                "relevance": "Direct murder weapon.",
                "importance": "Critical",
                "stars": 5
            },
            {
                "id": "ev_2",
                "name": "Patent Dissemination Draft",
                "category": "Financial Records",
                "location": "High-Containment Bio Lab 4",
                "description": "Internal document listing Dr. Vance as 100% sole inventor, removing Dr. Rostova's name completely.",
                "relevance": "Strong motive of professional and financial ruin for Elena Rostova.",
                "importance": "Critical",
                "stars": 4
            },
            {
                "id": "ev_3",
                "name": "Cold Storage Electronic Access Log",
                "category": "Cybercrime / Access Logs",
                "location": "Chemical Cold Storage Vault",
                "description": "Keycard badge reader shows Dr. Elena Rostova accessed chemical locker C-12 at 10:45 PM.",
                "relevance": "Places Elena inside the poison storage minutes before Vance drank his coffee.",
                "importance": "Critical",
                "stars": 4
            },
            {
                "id": "ev_4",
                "name": "Security Turnstile Discrepancy",
                "category": "Witness Statements",
                "location": "Executive Lounge & Coffee Station",
                "description": "Security Chief Marcus Kane logged a 20-minute patrol gap between 10:40 PM and 11:00 PM.",
                "relevance": "Explains how the perpetrator moved between rooms unmonitored.",
                "importance": "Medium",
                "stars": 3
            },
            {
                "id": "ev_5",
                "name": "Junior Associate Lab Notebook",
                "category": "Witness Statements",
                "location": "Executive Lounge & Coffee Station",
                "description": "Notes from Chloe Bennett detailing a fierce shouting match between Vance and Rostova at 5:15 PM.",
                "relevance": "Proves intense prior hostility between the victim and suspect.",
                "importance": "Medium",
                "stars": 3
            },
            {
                "id": "ev_6",
                "name": "Torn Nitrile Glove with Chemical Residue",
                "category": "Fingerprints / Physical",
                "location": "Chemical Cold Storage Vault",
                "description": "Discarded blue glove recovered from biohazard bin testing positive for cyanide and Dr. Rostova's epithelial DNA.",
                "relevance": "Smoking gun linking Elena Rostova directly to handling the lethal compound!",
                "importance": "Critical",
                "stars": 5
            }
        ],
        "suspects": [
            {
                "id": "suspect_1",
                "name": "Dr. Elena Rostova",
                "occupation": "Deputy Lead Biochemist",
                "relationship": "Research Partner & Co-Founder",
                "personality": "Calculated, intellectual, icy composure that cracks when confronted with evidence.",
                "alibi": "Claims she left the building at 10:00 PM and went straight to her apartment.",
                "secret": "Was actively interviewing at a competitor firm and smuggled raw trial data.",
                "motive": "Vance was erasing her from the patent, stealing billions and destroying her life's work.",
                "stress_level": "Defensive",
                "suspicion_score": 85
            },
            {
                "id": "suspect_2",
                "name": "Marcus Kane",
                "occupation": "Facilities Security Director",
                "relationship": "Colleague & Ex-Military Contractor",
                "personality": "Gruff, evasive, defensive about camera blind spots.",
                "alibi": "Claims he was conducting perimeter walkarounds on the north gate.",
                "secret": "Took cash bribes to overlook unauthorized after-hours lab visitors.",
                "motive": "Vance threatened to report Kane's bribe-taking to executive board.",
                "stress_level": "Nervous",
                "suspicion_score": 50
            },
            {
                "id": "suspect_3",
                "name": "Chloe Bennett",
                "occupation": "Junior Research Fellow",
                "relationship": "PhD Student under Vance",
                "personality": "Timid, overwhelmed, highly observant.",
                "alibi": "Was running PCR test sequences in Lab 2 until 11:15 PM.",
                "secret": "Discovered falsified data in Vance's early trial publications.",
                "motive": "Feared Vance would fail her dissertation to protect his research fraud.",
                "stress_level": "Calm",
                "suspicion_score": 35
            },
            {
                "id": "suspect_4",
                "name": "Vincent Sterling",
                "occupation": "Venture Capital Managing Partner",
                "relationship": "Lead Investor in Veloce",
                "personality": "Arrogant, polished, impatient with police procedure.",
                "alibi": "Was in a late teleconference with Tokyo investors from his penthouse.",
                "secret": "Veloce's cash reserves were nearly exhausted due to reckless clinical spending.",
                "motive": "Wanted to replace Vance with compliant management to force a pharma buyout.",
                "stress_level": "Calm",
                "suspicion_score": 40
            }
        ],
        "hints": [
            "Hint 1: Review the electronic access records in the Chemical Cold Storage Vault.",
            "Hint 2: Read the patent dissemination draft to discover who had their life's work stolen.",
            "Hint 3: Test the forensic residue and DNA on the torn nitrile glove found in the biohazard bin."
        ]
    },
    "Hard": {
        "id": "case_hard_303",
        "title": "The Apex Grid Ransomware Blackout",
        "crime_type": "Cybercrime",
        "difficulty": "Hard",
        "summary": "At 02:14 AM, the metropolitan power grid suffered a cascading blackout when polymorphic ransomware 'DarkVolt' infected the SCADA substation relays. A 500 BTC ransom demand was broadcast across all operator terminals.",
        "victim": {
            "name": "David Zheng",
            "occupation": "Chief Infrastructure Security Architect",
            "background": "Pioneered the city's smart-grid automation; discovered an internal exploit weeks before the attack."
        },
        "ground_truth": {
            "criminal_id": "suspect_1",
            "criminal_name": "Kira Novak",
            "motive": "Disillusioned security engineer protesting government cover-ups of critical grid safety vulnerabilities.",
            "how_it_was_done": "Injected the DarkVolt payload via an infected USB Rubber Ducky device plugged directly into the air-gapped Master Terminal 01.",
            "smoking_gun_evidence": "ev_6"
        },
        "locations": [
            {
                "id": "loc_1",
                "name": "Master SCADA Dispatch Center",
                "description": "Floor-to-ceiling diagnostic monitors flashing red emergency failover warnings and encrypted terminal prompts.",
                "image_type": "office",
                "evidence_ids": ["ev_1", "ev_2"]
            },
            {
                "id": "loc_2",
                "name": "Sub-Basement Server Vault",
                "description": "Rows of air-gapped server racks chilled to 15°C with physical access requiring dual-custody keycards.",
                "image_type": "warehouse",
                "evidence_ids": ["ev_3", "ev_4"]
            },
            {
                "id": "loc_3",
                "name": "Security Operations Center (SOC)",
                "description": "Surveillance workstations, network intrusion detection consoles, and personal lockers.",
                "image_type": "apartment",
                "evidence_ids": ["ev_5", "ev_6"]
            }
        ],
        "evidence": [
            {
                "id": "ev_1",
                "name": "DarkVolt Ransomware Binary Header",
                "category": "Cybercrime / Access Logs",
                "location": "Master SCADA Dispatch Center",
                "description": "Disassembled code contains internal function names matching Kira Novak's private developer framework.",
                "relevance": "Code authorship links the payload directly to Kira.",
                "importance": "Critical",
                "stars": 4
            },
            {
                "id": "ev_2",
                "name": "Hardcoded SSH Key Fingerprint",
                "category": "Cybercrime / Access Logs",
                "location": "Master SCADA Dispatch Center",
                "description": "SSH public key extracted from controller memory matches Kira Novak's verified development workstation.",
                "relevance": "Proves Kira's cryptographic credentials compiled the deployable malware.",
                "importance": "Critical",
                "stars": 4
            },
            {
                "id": "ev_3",
                "name": "Tor Exit Node Proxy Tunnel Logs",
                "category": "Phone Call Logs",
                "location": "Sub-Basement Server Vault",
                "description": "Network traffic reveals outbound encrypted heartbeat signals directed to an anonymized onion address.",
                "relevance": "Shows remote trigger channel used to detonate ransomware.",
                "importance": "Medium",
                "stars": 3
            },
            {
                "id": "ev_4",
                "name": "Unsent Whistleblower Regulatory Dossier",
                "category": "Emails / Communications",
                "location": "Sub-Basement Server Vault",
                "description": "Draft letter addressed to Federal Energy Commission warning of catastrophic flaws that executive leadership ignored.",
                "relevance": "Establishes ideological revenge motive rather than simple extortion.",
                "importance": "Medium",
                "stars": 3
            },
            {
                "id": "ev_5",
                "name": "Bitcoin Mixer Wallet Address",
                "category": "Financial Records",
                "location": "Security Operations Center (SOC)",
                "description": "Notepad entry listing an encrypted seed phrase for the 500 BTC ransom payout destination wallet.",
                "relevance": "Financial trace matching the ransom note.",
                "importance": "Medium",
                "stars": 3
            },
            {
                "id": "ev_6",
                "name": "Custom Hardware USB Rubber Ducky Keystroke Injector",
                "category": "Physical / Hardware",
                "location": "Security Operations Center (SOC)",
                "description": "Miniature flash drive hidden in Kira Novak's locker preloaded with the Master Terminal zero-day payload script.",
                "relevance": "Smoking gun physical tool used to bridge the air-gapped system!",
                "importance": "Critical",
                "stars": 5
            }
        ],
        "suspects": [
            {
                "id": "suspect_1",
                "name": "Kira Novak",
                "occupation": "Lead Network Security Engineer",
                "relationship": "Trusted System Administrator",
                "personality": "Quiet, fiercely ideological, hyper-competent in cybersecurity.",
                "alibi": "Claims she was monitoring false positives remotely from her home laptop.",
                "secret": "Spent 6 months crafting the exploit payload to expose grid vulnerability to the public.",
                "motive": "To force a complete teardown of corrupt leadership by crippling the grid infrastructure.",
                "stress_level": "Defensive",
                "suspicion_score": 88
            },
            {
                "id": "suspect_2",
                "name": "Roman Cruz",
                "occupation": "Penetration Testing Contractor",
                "relationship": "Third-Party Security Auditor",
                "personality": "Showy, cynical, driven by high bug bounty payouts.",
                "alibi": "Was submitting his final audit report from an offsite hotel room.",
                "secret": "Sold an unpatched vulnerability on a private darknet broker market.",
                "motive": "Could profit heavily by charging millions to remediate the attack.",
                "stress_level": "Nervous",
                "suspicion_score": 55
            },
            {
                "id": "suspect_3",
                "name": "Harold Finchley",
                "occupation": "VP of Grid Operations",
                "relationship": "Executive Supervisor",
                "personality": "Authoritarian, corporate, prioritizes profit over security updates.",
                "alibi": "Attending an energy deregulation conference in Geneva.",
                "secret": "Slashed the cyber defense budget by 40% to inflate annual executive bonuses.",
                "motive": "Wanted to blame external nation-state hackers to claim federal emergency subsidies.",
                "stress_level": "Calm",
                "suspicion_score": 40
            },
            {
                "id": "suspect_4",
                "name": "Maya Lin",
                "occupation": "Database Systems Administrator",
                "relationship": "Direct subordinate to David Zheng",
                "personality": "Anxious, meticulous, easily rattled under pressure.",
                "alibi": "Was running batch database maintenance in the SOC until 1:30 AM.",
                "secret": "Accidentally clicked a spear-phishing link two days prior.",
                "motive": "Feared being fired by Zheng if her security lapse was discovered.",
                "stress_level": "Nervous",
                "suspicion_score": 45
            },
            {
                "id": "suspect_5",
                "name": "Alexei Ramos",
                "occupation": "Former Substation Maintenance Tech",
                "relationship": "Disgruntled Terminated Employee",
                "personality": "Resentful, outspoken critic of the automated SCADA transition.",
                "alibi": "Claims he was at an all-night diner three miles away.",
                "secret": "Still possessed an unrevoked physical master key to Substation 4.",
                "motive": "Revenge against management for terminating union technicians.",
                "stress_level": "Defensive",
                "suspicion_score": 50
            }
        ],
        "hints": [
            "Hint 1: Inspect the binary header and SSH fingerprints recovered from the Master SCADA Dispatch Center.",
            "Hint 2: Review the regulatory dossier to identify who had an ideological grievance against grid management.",
            "Hint 3: Search the personal lockers in the SOC for physical hardware capable of bypassing an air gap."
        ]
    }
}

def get_mock_case(difficulty: str = "Easy", crime_type: str = "Theft") -> Dict[str, Any]:
    """Retrieve pre-packaged offline mystery case when Gemini API is unavailable.
    
    Provides 3 rich offline cases:
    - Easy: The Vanishing Ruby at Blackwood Manor (Theft)
    - Medium: The Midnight Cyanide Protocol (Murder)
    - Hard: The Apex Grid Ransomware Blackout (Cybercrime)
    """
    selected_key = "Easy"
    if crime_type == "Murder" or difficulty == "Medium":
        selected_key = "Medium"
    elif crime_type in ["Cybercrime", "Fraud"] or difficulty == "Hard":
        selected_key = "Hard"
    elif crime_type in ["Theft", "Kidnapping"] or difficulty == "Easy":
        selected_key = "Easy"

    if difficulty in MOCK_CASES and (not crime_type or crime_type in ["Any", "All"]):
        selected_key = difficulty

    base = MOCK_CASES.get(selected_key, MOCK_CASES["Easy"])
    case_copy = json_deepcopy(base)
    case_copy["id"] = f"case_{uuid.uuid4().hex[:8]}"
    case_copy["is_fallback"] = True
    return case_copy

def json_deepcopy(d):
    import json
    return json.loads(json.dumps(d))

