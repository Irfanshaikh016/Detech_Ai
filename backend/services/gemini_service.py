import os
import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from backend.services.mock_cases import get_mock_case

logger = logging.getLogger(__name__)

# gemini-1.5-flash was fully retired by Google (requests now 404). Default to a
# currently-serving model, but keep it overridable via env var so a future
# deprecation doesn't require another code change.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def get_api_key(override_key: Optional[str] = None) -> str:
    if override_key and len(override_key.strip()) > 5:
        return override_key.strip()
    env_key = os.getenv("GEMINI_API_KEY", "")
    return env_key.strip()

def _strip_json_fences(raw: str) -> str:
    """Strip markdown code fences Gemini sometimes wraps JSON in, robustly."""
    text = raw.strip()
    if text.startswith("```"):
        # Drop the opening fence line (``` or ```json)
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text[3:]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()

def call_gemini_api(prompt: str, system_instruction: str = "", api_key: str = "", response_json: bool = False, max_output_tokens: int = 2048) -> str:
    """Call Gemini REST API directly for maximum reliability and zero dependency issues."""
    key = get_api_key(api_key)
    if not key:
        raise ValueError("No Gemini API key provided!")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={key}"
    
    contents = []
    if system_instruction:
        contents.append({
            "role": "user",
            "parts": [{"text": f"[SYSTEM INSTRUCTION]: {system_instruction}\n\n[USER REQUEST]: {prompt}"}]
        })
    else:
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

    payload: Dict[str, Any] = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_output_tokens,
        }
    }
    
    if response_json:
        payload["generationConfig"]["responseMimeType"] = "application/json"

    headers = {"Content-Type": "application/json"}

    with httpx.Client(timeout=45.0) as client:
        res = client.post(url, json=payload, headers=headers)
        if res.status_code == 404:
            logger.error(f"Gemini API 404 for model '{GEMINI_MODEL}' — it may have been retired. Check https://ai.google.dev/gemini-api/docs/deprecations")
            raise Exception(f"Gemini model '{GEMINI_MODEL}' returned 404 (likely retired/unavailable).")
        if res.status_code != 200:
            logger.error(f"Gemini API Error ({res.status_code}): {res.text}")
            raise Exception(f"Gemini API returned status {res.status_code}: {res.text[:200]}")
        
        data = res.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected response structure: {data}")
            raise Exception("Failed to parse response from Gemini API.")

def generate_crime_case(difficulty: str = "Medium", crime_type: str = "Murder", api_key: str = "") -> Dict[str, Any]:
    """Generates a complete dynamic crime scenario using Gemini API with structured JSON output."""
    try:
        suspect_count = 3 if difficulty == "Easy" else (5 if difficulty == "Medium" else 8)
        clue_count = 5 if difficulty == "Easy" else (10 if difficulty == "Medium" else 15)

        system_instruction = (
            "You are an expert game master and criminal mystery novelist. "
            "You generate highly detailed, realistic, logical detective game cases with consistent clues, motives, importance ratings, and suspect suspicion scores. "
            "Return ONLY raw JSON conforming strictly to the requested schema."
        )

        prompt = f"""
Generate a complex, immersive crime investigation case for a game.
Difficulty Level: {difficulty}
Crime Type: {crime_type}
Number of Suspects: {suspect_count}
Number of Evidence Clues: {clue_count}

Output a single valid JSON object with the following exact keys:
{{
  "id": "generated_case_id",
  "title": "A Catchy Mystery Title",
  "crime_type": "{crime_type}",
  "difficulty": "{difficulty}",
  "summary": "Full overview of the crime committed, scene description, and time of occurrence.",
  "victim": {{
    "name": "Full Name",
    "occupation": "Job / Title",
    "background": "Brief history"
  }},
  "ground_truth": {{
    "criminal_id": "suspect_1",
    "criminal_name": "Full Name of actual guilty suspect",
    "motive": "Detailed real motive for the crime",
    "how_it_was_done": "Step-by-step description of how crime was executed",
    "smoking_gun_evidence": "ev_1"
  }},
  "locations": [
    {{
      "id": "loc_1",
      "name": "Location Name (e.g. Victim's House, Office, Crime Scene, Parking Area, Cafe, Hotel)",
      "description": "Visual atmosphere description",
      "image_type": "One of: warehouse, apartment, office, parking, cafe, hotel, house",
      "evidence_ids": ["ev_1", "ev_2"]
    }}
  ],
  "evidence": [
    {{
      "id": "ev_1",
      "name": "Clue Name",
      "category": "One of: CCTV Descriptions, Fingerprints, Phone Call Logs, Emails, Financial Records, Witness Statements",
      "location": "Location Name where found",
      "description": "Detailed text snippet or observation of this clue",
      "relevance": "How this connects to suspects or alibis",
      "importance": "One of: Critical, Medium, Low",
      "stars": 4
    }}
  ],
  "suspects": [
    {{
      "id": "suspect_1",
      "name": "Full Name",
      "occupation": "Job / Title",
      "relationship": "Connection to victim",
      "personality": "Behavioral traits e.g. Nervous, Hostile, Arrogant, Calm",
      "alibi": "Claimed whereabouts at time of crime",
      "secret": "A secret they are hiding (could be red herring or crime related)",
      "motive": "Potential motive to commit crime",
      "stress_level": "Calm",
      "suspicion_score": 45
    }}
  ],
  "hints": [
    "First subtle hint pointing towards a location or evidence type",
    "Second clearer hint highlighting a statement conflict or timeline mismatch",
    "Final strong hint correlating smoking gun evidence with guilty suspect"
  ]
}}
"""
        # Hard difficulty asks for up to 8 suspects + 15 clues, which needs more
        # room than the old 2048-token default (was silently truncating JSON).
        raw_json = call_gemini_api(prompt, system_instruction=system_instruction, api_key=api_key, response_json=True, max_output_tokens=8192)
        case_data = json.loads(_strip_json_fences(raw_json))
        
        # Ensure default values for importance & suspicion
        for e in case_data.get("evidence", []):
            if "importance" not in e:
                e["importance"] = "Medium"
            if "stars" not in e:
                e["stars"] = 3
        for s in case_data.get("suspects", []):
            if "suspicion_score" not in s:
                s["suspicion_score"] = 35

        return case_data
    except Exception as e:
        logger.warning(f"Gemini API generation failed ({e}), falling back to mock case generator (fixed 'Easy' story, not '{difficulty}').")
        return get_mock_case(difficulty, crime_type)

def interrogate_suspect(
    case_data: Dict[str, Any],
    suspect_id: str,
    history: List[Dict[str, Any]],
    question: str,
    evidence_presented: Optional[Dict[str, Any]] = None,
    api_key: str = ""
) -> Dict[str, Any]:
    """Roleplay as suspect during interrogation using prompt engineering and memory."""
    suspect = next((s for s in case_data.get("suspects", []) if s["id"] == suspect_id), None)
    if not suspect:
        return {"response": "I don't know who you're talking about.", "stress_level": "Calm", "suspicion_change": 0}

    ground_truth = case_data.get("ground_truth", {})
    is_guilty = (suspect["id"] == ground_truth.get("criminal_id"))

    system_prompt = f"""
You are playing the role of "{suspect['name']}", a suspect in a crime investigation game.
Occupation: {suspect['occupation']}
Relationship to Victim: {suspect['relationship']}
Personality: {suspect['personality']}
Your Claimed Alibi: {suspect['alibi']}
Your Secret: {suspect['secret']}
Your Potential Motive: {suspect['motive']}
Are you the actual criminal?: {"YES" if is_guilty else "NO"}
Ground Truth Crime Details: {ground_truth.get('how_it_was_done')}

RULES OF ENGAGEMENT:
1. NEVER directly confess to the crime unless overwhelmingly cornered with smoking gun evidence.
2. Answer strictly using facts consistent with your personality, secret, and alibi.
3. Stay strictly in character! If asked about something outside your knowledge, say you don't know.
4. Maintain memory consistency with previous answers in this interrogation transcript.
5. If the detective presents evidence that directly contradicts your alibi or secret, react noticeably (become Nervous, Defensive, or Panicked).
6. Keep your responses concise (2-4 sentences max), dynamic, and engaging.

At the very end of your response, output a single line in this format:
[STRESS: Calm | SUSPICION: +5]  (or [STRESS: Cornered | SUSPICION: +20], [STRESS: Defensive | SUSPICION: -5])
"""

    formatted_history = ""
    for msg in history[-6:]:
        role_label = "Detective" if msg.get("role") == "player" else suspect['name']
        formatted_history += f"{role_label}: {msg.get('content')}\n"

    evidence_str = ""
    if evidence_presented:
        evidence_str = f"\n[DETECTIVE CONFRONTS YOU WITH EVIDENCE]: '{evidence_presented.get('name')}' - Description: {evidence_presented.get('description')}\n"

    prompt = f"""
Interrogation Transcript So Far:
{formatted_history}

{evidence_str}
Detective's Question: "{question}"

Respond in character as {suspect['name']}:
"""

    try:
        raw_response = call_gemini_api(prompt, system_instruction=system_prompt, api_key=api_key)
        stress = suspect.get("stress_level", "Calm")
        suspicion_change = 0
        clean_text = raw_response.strip()
        
        if "[STRESS:" in clean_text:
            parts = clean_text.split("[STRESS:")
            clean_text = parts[0].strip()
            stress_info = parts[1].split("]")[0].strip()
            if "|" in stress_info:
                s_parts = stress_info.split("|")
                stress = s_parts[0].strip()
                if "SUSPICION:" in s_parts[1]:
                    try:
                        suspicion_change = int(s_parts[1].replace("SUSPICION:", "").strip())
                    except ValueError:
                        suspicion_change = 10 if stress in ["Nervous", "Cornered"] else 0
            else:
                stress = stress_info.strip()

        return {"response": clean_text, "stress_level": stress, "suspicion_change": suspicion_change}
    except Exception as e:
        logger.warning(f"Gemini interrogation failed: {e}")
        if is_guilty and evidence_presented:
            return {"response": f"Wait! That... that's impossible. Where did you get that {evidence_presented.get('name')}?!", "stress_level": "Nervous", "suspicion_change": 15}
        return {"response": f"I've already told you what I know. My alibi stands: {suspect['alibi']}.", "stress_level": "Defensive", "suspicion_change": 5}

def generate_ai_hint(case_data: Dict[str, Any], hint_level: int = 1, api_key: str = "") -> str:
    hints = case_data.get("hints", [])
    if len(hints) >= hint_level:
        return hints[hint_level - 1]
    
    try:
        prompt = f"""
Generate Hint Level {hint_level} (out of 3) for this mystery:
Crime: {case_data.get('title')}
Summary: {case_data.get('summary')}
Guilty Suspect: {case_data.get('ground_truth', {}).get('criminal_name')}
Smoking Gun: {case_data.get('ground_truth', {}).get('smoking_gun_evidence')}

Output ONLY the hint text.
"""
        return call_gemini_api(prompt, api_key=api_key).strip()
    except Exception:
        return f"Hint Level {hint_level}: Examine the evidence collected from the locations carefully and compare timeline statements."

def evaluate_accusation(
    case_data: Dict[str, Any],
    accused_suspect_id: str,
    motive_provided: str,
    evidence_ids: List[str],
    api_key: str = "",
    hints_used: int = 0
) -> Dict[str, Any]:
    ground_truth = case_data.get("ground_truth", {})
    actual_criminal_id = ground_truth.get("criminal_id")
    is_correct = (accused_suspect_id == actual_criminal_id)

    suspects = {s["id"]: s for s in case_data.get("suspects", [])}
    evidence_map = {e["id"]: e for e in case_data.get("evidence", [])}

    accused_suspect = suspects.get(accused_suspect_id, {})
    actual_criminal = suspects.get(actual_criminal_id, {})

    presented_ev = [evidence_map[eid] for eid in evidence_ids if eid in evidence_map]
    presented_ev_names = [e["name"] for e in presented_ev]
    smoking_gun_id = ground_truth.get("smoking_gun_evidence")
    has_smoking_gun = bool(smoking_gun_id and smoking_gun_id in evidence_ids)

    clean_motive = (motive_provided or "").strip()
    has_motive = len(clean_motive) >= 8
    detailed_motive = len(clean_motive) >= 20

    system_instruction = (
        "You are an impartial Supreme AI Judge presiding over a crime trial. "
        "Evaluate the detective player's final indictment with analytical clarity. "
        "Return strictly raw JSON format."
    )

    prompt = f"""
CASE GROUND TRUTH:
- Guilty Culprit: {actual_criminal.get('name')} (ID: {actual_criminal_id})
- True Motive: {ground_truth.get('motive')}
- How Crime Was Executed: {ground_truth.get('how_it_was_done')}
- Smoking Gun Evidence: {ground_truth.get('smoking_gun_evidence')}

PLAYER'S ACCUSATION:
- Accused Suspect: {accused_suspect.get('name')} (ID: {accused_suspect_id})
- Player's Claimed Motive: "{motive_provided}"
- Evidence Presented: {presented_ev_names}
- Hints Used: {hints_used}

SCORING GUIDELINES:
1. If accused is NOT the culprit, is_correct must be false and final score must be <= 35.
2. If accused IS the culprit:
   - Base score: 75.
   - +15 bonus if smoking gun evidence was presented.
   - -25 penalty if NO evidence was presented.
   - -15 penalty if motive is blank or superficial.
   - Deduct 5 points per hint used ({hints_used * 5} pts deduction).
   - Clamp final score between 50 and 100.
3. Calculate sub-scores: evidence_strength (0-100), logic_score (0-100), thoroughness_score (0-100).
4. Detail which clues support the verdict and which crucial evidence clues were ignored.

Return ONLY a JSON object:
{{
  "is_correct": {json.dumps(is_correct)},
  "score": 90,
  "evidence_strength": 90,
  "logic_score": 85,
  "thoroughness_score": 90,
  "judge_explanation": "Detailed verdict statement...",
  "supported_clues": ["Clue A", "Clue B"],
  "ignored_clues": ["Clue X", "Clue Y"]
}}
"""

    try:
        raw_json = call_gemini_api(prompt, system_instruction=system_instruction, api_key=api_key, response_json=True, max_output_tokens=3072)
        verdict = json.loads(_strip_json_fences(raw_json))
        # Ensure score adheres to bounds
        if not is_correct:
            verdict["is_correct"] = False
            verdict["score"] = min(35, verdict.get("score", 30))
        else:
            verdict["is_correct"] = True
            verdict["score"] = max(50, min(100, verdict.get("score", 85)))
        return verdict
    except Exception as e:
        logger.warning(f"Gemini Judge API failed ({e}), using stabilized fallback judge logic.")
        total_ev_count = max(1, len(case_data.get("evidence", [])))
        ev_count = len(presented_ev)
        
        if is_correct:
            # Deterministic scoring for correct accusation
            score = 75
            if has_smoking_gun:
                score += 15
            else:
                score += min(10, ev_count * 5)
                
            if not has_motive:
                score -= 15
            elif detailed_motive:
                score += 5
                
            if ev_count == 0:
                score -= 25
                
            score -= (hints_used * 5)
            final_score = max(50, min(100, score))
            
            ev_strength = min(100, max(25, 45 + (30 if has_smoking_gun else 0) + (10 * min(3, ev_count)) - (25 if ev_count == 0 else 0)))
            logic = min(100, max(30, 60 + (25 if detailed_motive else 0) - (20 if not has_motive else 0) - (hints_used * 5)))
            thoroughness = min(100, max(20, int((ev_count / total_ev_count) * 100)))
            
            explanation = (
                f"The Court finds the accused {accused_suspect.get('name')} GUILTY beyond reasonable doubt. "
                f"The indictment is corroborated by forensic evidence presented by the detective."
            )
        else:
            # Deterministic scoring for incorrect accusation
            score = 20 + min(10, ev_count * 3)
            if ev_count == 0:
                score -= 10
            final_score = max(5, min(35, score))
            
            ev_strength = min(40, max(10, 15 + (5 * min(4, ev_count))))
            logic = 20
            thoroughness = min(40, max(10, int((ev_count / total_ev_count) * 40)))
            
            explanation = (
                f"Case DISMISSED! Accused {accused_suspect.get('name')} is innocent. "
                f"The evidence cited fails to link the suspect to the primary crime, and the true perpetrator was {actual_criminal.get('name')}."
            )

        return {
            "is_correct": is_correct,
            "score": final_score,
            "evidence_strength": ev_strength,
            "logic_score": logic,
            "thoroughness_score": thoroughness,
            "judge_explanation": explanation,
            "supported_clues": presented_ev_names,
            "ignored_clues": [e["name"] for e in case_data.get("evidence", []) if e["id"] not in evidence_ids]
        }

