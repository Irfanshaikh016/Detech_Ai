import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import database.db as db
import services.gemini_service as gemini_service

router = APIRouter(prefix="/api/cases", tags=["cases"])

class GenerateCaseRequest(BaseModel):
    difficulty: str = "Medium" # Easy, Medium, Hard
    crime_type: str = "Murder" # Murder, Theft, Kidnapping, Cybercrime, Fraud
    api_key: Optional[str] = None

class InterrogateRequest(BaseModel):
    suspect_id: str
    question: str
    evidence_id: Optional[str] = None
    api_key: Optional[str] = None

class HintRequest(BaseModel):
    hint_level: int = 1
    api_key: Optional[str] = None

class JudgeRequest(BaseModel):
    accused_suspect_id: str
    motive_provided: str
    evidence_ids: List[str]
    player_name: Optional[str] = "Detective"
    api_key: Optional[str] = None

@router.get("/leaderboard")
def get_leaderboard_endpoint():
    leaderboard = db.get_leaderboard(limit=10)
    return {"status": "success", "leaderboard": leaderboard}


@router.post("/generate")
def generate_case_endpoint(req: GenerateCaseRequest):
    case_data = gemini_service.generate_crime_case(
        difficulty=req.difficulty,
        crime_type=req.crime_type,
        api_key=req.api_key or ""
    )
    
    if not case_data.get("id") or case_data["id"] == "generated_case_id":
        case_data["id"] = f"case_{uuid.uuid4().hex[:8]}"
        
    case_id = case_data["id"]
    title = case_data.get("title", "Mysterious Crime Case")
    crime_type = case_data.get("crime_type", req.crime_type)
    difficulty = case_data.get("difficulty", req.difficulty)
    victim_name = case_data.get("victim", {}).get("name", "Unknown Victim")
    
    # Save to SQLite database
    db.save_case(case_id, title, crime_type, difficulty, victim_name, case_data)
    
    # Strip ground truth before returning to frontend player (so they can't cheat)
    sanitized_case = dict(case_data)
    # Keep ground_truth in backend, but remove from response
    sanitized_case.pop("ground_truth", None)
    
    return {"status": "success", "case_id": case_id, "case": sanitized_case}

@router.get("/{case_id}")
def get_case_endpoint(case_id: str):
    case_data = db.get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found in database.")
    
    sanitized_case = dict(case_data)
    sanitized_case.pop("ground_truth", None)
    return {"status": "success", "case": sanitized_case}

@router.post("/{case_id}/interrogate")
def interrogate_endpoint(case_id: str, req: InterrogateRequest):
    case_data = db.get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    # Retrieve past interrogation logs for conversation memory
    history = db.get_interrogation_logs(case_id, req.suspect_id)
    
    # Find evidence presented if evidence_id given
    evidence_presented = None
    if req.evidence_id:
        evidence_presented = next((e for e in case_data.get("evidence", []) if e["id"] == req.evidence_id), None)
        
    # Save player's question to SQLite log
    question_text = req.question
    if evidence_presented:
        question_text += f" (Confronting with evidence: {evidence_presented.get('name')})"
    db.save_interrogation_log(case_id, req.suspect_id, "player", question_text)
    
    # Call AI dialogue engine
    ai_result = gemini_service.interrogate_suspect(
        case_data=case_data,
        suspect_id=req.suspect_id,
        history=history,
        question=req.question,
        evidence_presented=evidence_presented,
        api_key=req.api_key or ""
    )
    
    # Save suspect response to SQLite log
    db.save_interrogation_log(
        case_id,
        req.suspect_id,
        "suspect",
        ai_result.get("response", ""),
        stress_level=ai_result.get("stress_level", "Calm")
    )
    
    updated_history = db.get_interrogation_logs(case_id, req.suspect_id)
    return {
        "status": "success",
        "response": ai_result.get("response"),
        "stress_level": ai_result.get("stress_level"),
        "history": updated_history
    }

@router.get("/{case_id}/interrogate/{suspect_id}")
def get_interrogation_history(case_id: str, suspect_id: str):
    history = db.get_interrogation_logs(case_id, suspect_id)
    return {"status": "success", "history": history}

@router.post("/{case_id}/hint")
def get_hint_endpoint(case_id: str, req: HintRequest):
    case_data = db.get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    hint_text = gemini_service.generate_ai_hint(case_data, hint_level=req.hint_level, api_key=req.api_key or "")
    return {"status": "success", "hint_level": req.hint_level, "hint": hint_text}

@router.post("/{case_id}/judge")
def judge_accusation_endpoint(case_id: str, req: JudgeRequest):
    case_data = db.get_case(case_id)
    if not case_data:
        raise HTTPException(status_code=404, detail="Case not found.")
    
    verdict = gemini_service.evaluate_accusation(
        case_data=case_data,
        accused_suspect_id=req.accused_suspect_id,
        motive_provided=req.motive_provided,
        evidence_ids=req.evidence_ids,
        api_key=req.api_key or ""
    )
    
    # Save verdict to SQLite
    db.save_verdict(
        case_id=case_id,
        player_name=req.player_name or "Detective",
        accused_suspect_id=req.accused_suspect_id,
        motive_provided=req.motive_provided,
        is_correct=verdict.get("is_correct", False),
        score=verdict.get("score", 50),
        explanation=verdict.get("judge_explanation", ""),
        supported=verdict.get("supported_clues", []),
        ignored=verdict.get("ignored_clues", []),
        difficulty=case_data.get("difficulty", "Medium")
    )
    
    # Include ground truth in the final verdict response so player learns the full backstory!
    verdict["ground_truth"] = case_data.get("ground_truth")
    return {"status": "success", "verdict": verdict}
