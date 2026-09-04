import os
import json
import time
import logging
import httpx
from typing import Dict, Any, List, Optional
from backend.services.mock_cases import get_mock_case

logger = logging.getLogger(__name__)

# Primary & Secondary AI Provider Models
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-4.6")

PLACEHOLDER_KEYS = {"", "your_gemini_api_key_here", "your_grok_api_key_here", "none", "null", "undefined"}

def get_gemini_api_key(override_key: Optional[str] = None) -> str:
    if override_key and len(override_key.strip()) > 5:
        key = override_key.strip()
        if key.lower() not in PLACEHOLDER_KEYS:
            return key
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key.lower() in PLACEHOLDER_KEYS:
        return ""
    return env_key

def get_grok_api_key(override_key: Optional[str] = None) -> str:
    if override_key and len(override_key.strip()) > 5:
        key = override_key.strip()
        if key.lower() not in PLACEHOLDER_KEYS:
            return key
    env_key = os.getenv("GROK_API_KEY", "").strip()
    if env_key.lower() in PLACEHOLDER_KEYS:
        return ""
    return env_key

# Backward-compatible alias
get_api_key = get_gemini_api_key

def _strip_json_fences(raw: str) -> str:
    """Strip markdown code fences Gemini or Grok sometimes wrap JSON in, robustly."""
    text = raw.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text[3:]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def call_gemini_api(
    prompt: str,
    system_instruction: str = "",
    api_key: str = "",
    response_json: bool = False,
    max_output_tokens: int = 8192,
    timeout: float = 30.0,
    max_retries: int = 2,
    retry_delay: float = 1.0
) -> str:
    """Call Gemini REST API directly with bounded retries for transient failures (503, 429, 5xx)."""
    key = get_gemini_api_key(api_key)
    if not key:
        raise ValueError("No Gemini API key provided")

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

    attempt = 0
    current_delay = retry_delay
    total_attempts = max_retries + 1

    while attempt < total_attempts:
        attempt += 1
        logger.info(f"Gemini request started")
        try:
            with httpx.Client(timeout=timeout) as client:
                res = client.post(url, json=payload, headers=headers)
                
                if res.status_code == 200:
                    try:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise ValueError("No candidates in Gemini API response")
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if not parts:
                            raise ValueError("No content parts in Gemini API response")
                        text = parts[0].get("text", "")
                        if not text or not str(text).strip():
                            raise ValueError("Empty text in Gemini API response")
                        return str(text).strip()
                    except (ValueError, KeyError, IndexError) as parse_err:
                        logger.warning(f"Unexpected response structure or empty content from Gemini API: {parse_err}")
                        raise Exception("Failed to parse response from Gemini API.")

                if res.status_code in RETRYABLE_STATUS_CODES:
                    logger.warning(f"Gemini returned temporary status {res.status_code}")
                    if attempt < total_attempts:
                        logger.warning(f"Gemini retry {attempt}/{max_retries}")
                        time.sleep(current_delay)
                        current_delay *= 2.0
                        continue
                    else:
                        logger.warning("Gemini retries exhausted")
                        raise Exception(f"Gemini API returned status {res.status_code}")
                else:
                    logger.warning(f"Gemini API returned non-retryable status {res.status_code}")
                    raise Exception(f"Gemini API returned status {res.status_code}")

        except httpx.RequestError as req_err:
            logger.warning(f"Gemini request network error: {req_err.__class__.__name__}")
            if attempt < total_attempts:
                logger.warning(f"Gemini retry {attempt}/{max_retries}")
                time.sleep(current_delay)
                current_delay *= 2.0
                continue
            else:
                logger.warning("Gemini retries exhausted")
                raise Exception(f"Gemini request failed after {total_attempts} attempts: {req_err.__class__.__name__}")

    logger.warning("Gemini retries exhausted")
    raise Exception("Gemini request retries exhausted")

def call_grok_api(
    prompt: str,
    system_instruction: str = "",
    api_key: str = "",
    response_json: bool = False,
    max_tokens: int = 8192,
    timeout: float = 30.0
) -> str:
    """Call Grok API via OpenAI-compatible endpoint with configurable timeout and response validation."""
    key = get_grok_api_key(api_key)
    if not key:
        raise ValueError("No Grok API key provided")

    from openai import OpenAI
    client = OpenAI(
        api_key=key,
        base_url="https://api.x.ai/v1",
        timeout=timeout
    )

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    kwargs: Dict[str, Any] = {
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
    }
    if response_json:
        kwargs["response_format"] = {"type": "json_object"}

    logger.info(f"Calling Grok API (model={GROK_MODEL}, timeout={timeout}s)...")
    completion = client.chat.completions.create(**kwargs)
    if not completion or not getattr(completion, "choices", None) or len(completion.choices) == 0:
        logger.warning("Grok API returned empty completion choices")
        raise ValueError("Grok API returned empty completion choices")

    choice = completion.choices[0]
    content = getattr(choice.message, "content", None)
    if not content or not str(content).strip():
        logger.warning("Grok API returned empty message content")
        raise ValueError("Grok API returned empty message content")
    return str(content).strip()

def _validate_and_normalize_case(
    case_data: Any,
    difficulty: str,
    crime_type: str,
    provider: str
) -> Optional[Dict[str, Any]]:
    """Validate JSON case schema and ensure consistent fields and metadata."""
    if not isinstance(case_data, dict):
        return None

    required_keys = ["title", "suspects", "evidence", "locations", "ground_truth"]
    for k in required_keys:
        if k not in case_data:
            logger.warning(f"{provider} generated case missing required key '{k}'")
            return None

    if not isinstance(case_data.get("suspects"), list) or len(case_data["suspects"]) < 3:
        logger.warning(f"{provider} case has insufficient suspects")
        return None

    if not isinstance(case_data.get("evidence"), list) or len(case_data["evidence"]) < 3:
        logger.warning(f"{provider} case has insufficient evidence clues")
        return None

    if not isinstance(case_data.get("locations"), list) or len(case_data["locations"]) < 1:
        logger.warning(f"{provider} case has insufficient locations")
        return None

    gt = case_data.get("ground_truth")
    if not isinstance(gt, dict) or not (gt.get("criminal_id") or gt.get("criminal_name")):
        logger.warning(f"{provider} case has invalid ground_truth")
        return None

    # Preserve requested difficulty and crime type
    case_data["difficulty"] = difficulty
    case_data["crime_type"] = crime_type

    # Normalize evidence defaults
    for e in case_data["evidence"]:
        if isinstance(e, dict):
            if "importance" not in e:
                e["importance"] = "Medium"
            if "stars" not in e:
                e["stars"] = 3

    # Normalize suspects defaults
    for s in case_data["suspects"]:
        if isinstance(s, dict):
            if "suspicion_score" not in s:
                s["suspicion_score"] = 35
            if "stress_level" not in s:
                s["stress_level"] = "Calm"

    case_data["provider"] = provider
    case_data["is_fallback"] = (provider == "offline")
    return case_data

def generate_crime_case(
    difficulty: str = "Medium",
    crime_type: str = "Murder",
    api_key: str = "",
    grok_api_key: str = ""
) -> Dict[str, Any]:
    """Generates a complete crime scenario with 3-tier fallback: Gemini -> Grok -> Offline mock."""
    diff = (difficulty or "Medium").capitalize()
    if diff not in ["Easy", "Medium", "Hard"]:
        diff = "Medium"
    ctype = (crime_type or "Murder").capitalize()

    suspect_count = 3 if diff == "Easy" else (5 if diff == "Medium" else 8)
    clue_count = 5 if diff == "Easy" else (10 if diff == "Medium" else 15)

    system_instruction = (
        "You are an expert game master and criminal mystery novelist. "
        "You generate highly detailed, realistic, logical detective game cases with consistent clues, motives, importance ratings, and suspect suspicion scores. "
        "Return ONLY raw JSON conforming strictly to the requested schema."
    )

    prompt = f"""
Generate a complex, immersive crime investigation case for a game.
Difficulty Level: {diff}
Crime Type: {ctype}
Number of Suspects: {suspect_count}
Number of Evidence Clues: {clue_count}

Output a single valid JSON object with the following exact keys:
{{
  "id": "generated_case_id",
  "title": "A Catchy Mystery Title",
  "crime_type": "{ctype}",
  "difficulty": "{diff}",
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

    # --- Level 1: Primary Provider (Gemini) ---
    gemini_key = get_gemini_api_key(api_key)
    if gemini_key:
        try:
            logger.info(f"Attempting case generation with Gemini ({GEMINI_MODEL}, difficulty={diff})...")
            raw_json = call_gemini_api(prompt, system_instruction=system_instruction, api_key=gemini_key, response_json=True, max_output_tokens=8192, timeout=30.0)
            if not raw_json or not raw_json.strip():
                raise ValueError("Empty response text from Gemini API")
            parsed = json.loads(_strip_json_fences(raw_json))
            validated = _validate_and_normalize_case(parsed, difficulty=diff, crime_type=ctype, provider="gemini")
            if validated:
                logger.info("Gemini generation succeeded")
                return validated
            logger.warning("Gemini response was invalid or malformed JSON schema. Attempting Grok fallback...")
        except Exception as e:
            logger.warning(f"Gemini generation failed ({e.__class__.__name__}: {e}). Attempting Grok fallback...")
    else:
        logger.info("Gemini API key not configured or missing. Skipping Gemini provider.")

    # --- Level 2: Secondary Provider (Grok) ---
    grok_key = get_grok_api_key(grok_api_key)
    if grok_key:
        try:
            logger.info("Attempting Grok fallback")
            raw_json = call_grok_api(prompt, system_instruction=system_instruction, api_key=grok_key, response_json=True, max_tokens=8192, timeout=30.0)
            if not raw_json or not raw_json.strip():
                raise ValueError("Empty response text from Grok API")
            parsed = json.loads(_strip_json_fences(raw_json))
            validated = _validate_and_normalize_case(parsed, difficulty=diff, crime_type=ctype, provider="grok")
            if validated:
                logger.info("Grok generation succeeded")
                return validated
            logger.warning("Grok response was invalid or malformed JSON schema. Attempting offline fallback...")
        except Exception as e:
            logger.warning(f"Grok generation failed ({e.__class__.__name__}: {e}). Attempting offline fallback...")
    else:
        logger.info("Grok API key not configured or missing. Skipping Grok provider.")

    # --- Level 3: Deterministic Offline Mock Fallback ---
    logger.info("Using offline fallback")
    offline_case = get_mock_case(difficulty=diff, crime_type=ctype)
    offline_case["provider"] = "offline"
    offline_case["is_fallback"] = True
    return offline_case

def interrogate_suspect(
    case_data: Dict[str, Any],
    suspect_id: str,
    history: List[Dict[str, Any]],
    question: str,
    evidence_presented: Optional[Dict[str, Any]] = None,
    api_key: str = "",
    grok_api_key: str = ""
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

    raw_response = None
    # 1. Try Gemini
    gemini_key = get_gemini_api_key(api_key)
    if gemini_key:
        try:
            raw_response = call_gemini_api(prompt, system_instruction=system_prompt, api_key=gemini_key, timeout=20.0)
        except Exception as e:
            logger.warning(f"Gemini interrogation failed: {e}")

    # 2. Try Grok
    if not raw_response:
        grok_key = get_grok_api_key(grok_api_key)
        if grok_key:
            try:
                raw_response = call_grok_api(prompt, system_instruction=system_prompt, api_key=grok_key, timeout=20.0)
            except Exception as e:
                logger.warning(f"Grok interrogation failed: {e}")

    if raw_response:
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

    # 3. Deterministic offline fallback
    if is_guilty and evidence_presented:
        return {"response": f"Wait! That... that's impossible. Where did you get that {evidence_presented.get('name')}?!", "stress_level": "Nervous", "suspicion_change": 15}
    return {"response": f"I've already told you what I know. My alibi stands: {suspect['alibi']}.", "stress_level": "Defensive", "suspicion_change": 5}

def generate_ai_hint(case_data: Dict[str, Any], hint_level: int = 1, api_key: str = "", grok_api_key: str = "") -> str:
    hints = case_data.get("hints", [])
    if len(hints) >= hint_level:
        return hints[hint_level - 1]
    
    prompt = f"""
Generate Hint Level {hint_level} (out of 3) for this mystery:
Crime: {case_data.get('title')}
Summary: {case_data.get('summary')}
Guilty Suspect: {case_data.get('ground_truth', {}).get('criminal_name')}
Smoking Gun: {case_data.get('ground_truth', {}).get('smoking_gun_evidence')}

Output ONLY the hint text.
"""
    gemini_key = get_gemini_api_key(api_key)
    if gemini_key:
        try:
            return call_gemini_api(prompt, api_key=gemini_key, timeout=15.0).strip()
        except Exception:
            pass

    grok_key = get_grok_api_key(grok_api_key)
    if grok_key:
        try:
            return call_grok_api(prompt, api_key=grok_key, timeout=15.0).strip()
        except Exception:
            pass

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

