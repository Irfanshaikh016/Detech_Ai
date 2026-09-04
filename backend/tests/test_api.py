"""Integration tests for DetectAI FastAPI backend."""

def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_generate_case_offline(client):
    res = client.post("/api/cases/generate", json={
        "difficulty": "Easy",
        "crime_type": "Theft",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "case_id" in data
    assert "case" in data
    case = data["case"]
    assert case["title"]
    assert len(case["suspects"]) >= 3
    assert len(case["evidence"]) >= 5
    assert len(case["locations"]) >= 1
    assert "ground_truth" not in case
    assert case.get("is_fallback") is True


def test_get_case(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Murder"})
    case_id = gen.json()["case_id"]
    res = client.get(f"/api/cases/{case_id}")
    assert res.status_code == 200
    assert res.json()["case"]["id"] == case_id
    assert "ground_truth" not in res.json()["case"]


def test_get_case_not_found(client):
    res = client.get("/api/cases/nonexistent_case_xyz")
    assert res.status_code == 404


def test_interrogate_flow(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]
    suspect_id = gen.json()["case"]["suspects"][0]["id"]

    empty = client.get(f"/api/cases/{case_id}/interrogate/{suspect_id}")
    assert empty.status_code == 200
    assert empty.json()["history"] == []

    ask = client.post(f"/api/cases/{case_id}/interrogate", json={
        "suspect_id": suspect_id,
        "question": "Where were you at 9 PM?",
    })
    assert ask.status_code == 200
    body = ask.json()
    assert body["response"]
    assert body["stress_level"]
    assert len(body["history"]) == 2
    assert body["history"][0]["role"] == "player"
    assert body["history"][0]["message"]
    assert body["history"][1]["role"] == "suspect"


def test_hint_levels(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]

    for level in (1, 2, 3):
        res = client.post(f"/api/cases/{case_id}/hint", json={"hint_level": level})
        assert res.status_code == 200
        assert res.json()["hint"]


def test_judge_accusation(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]
    case = gen.json()["case"]
    guilty_id = "suspect_1"
    evidence_ids = [e["id"] for e in case["evidence"][:2]]

    res = client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": guilty_id,
        "motive_provided": "Gambling debts forced them to steal the ruby.",
        "evidence_ids": evidence_ids,
        "player_name": "Detective Test",
    })
    assert res.status_code == 200
    verdict = res.json()["verdict"]
    assert verdict["is_correct"] is True
    assert 0 <= verdict["score"] <= 100
    assert verdict["judge_explanation"]
    assert verdict["ground_truth"]["criminal_name"]


def test_leaderboard_after_verdict(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]
    client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_1",
        "motive_provided": "Debt motive caused them to steal the priceless ruby to repay loans.",
        "evidence_ids": ["ev_1", "ev_2"],
        "player_name": "Leaderboard Tester",
    })

    res = client.get("/api/cases/leaderboard")
    assert res.status_code == 200
    rows = res.json()["leaderboard"]
    assert len(rows) >= 1
    target = next((r for r in rows if r["player_name"] == "Leaderboard Tester"), None)
    assert target is not None
    assert "case_title" in target
    assert "case_id" in target


def test_frontend_served(client):
    res = client.get("/")
    if res.status_code == 200 and "text/html" in res.headers.get("content-type", ""):
        assert "DetectAI" in res.text
    else:
        # API-only fallback when index.html missing
        assert res.json()["status"] == "online"


def test_list_cases(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    assert gen.status_code == 200
    case_id = gen.json()["case_id"]

    res = client.get("/api/cases")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "cases" in data
    cases = data["cases"]
    assert len(cases) >= 1

    # Locate generated case in list
    target = next((c for c in cases if c["case_id"] == case_id), None)
    assert target is not None
    assert "title" in target
    assert target["crime_type"] == "Theft"
    assert target["difficulty"] == "Easy"
    assert target["is_completed"] is False
    assert target["status"] == "In Progress"


def test_case_resumption_and_logs(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]
    suspect_id = gen.json()["case"]["suspects"][0]["id"]

    # Ask question
    ask = client.post(f"/api/cases/{case_id}/interrogate", json={
        "suspect_id": suspect_id,
        "question": "What is your alibi?",
    })
    assert ask.status_code == 200

    # Retrieve all logs for case
    res = client.get(f"/api/cases/{case_id}/logs")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["case_id"] == case_id
    assert suspect_id in data["interrogations"]
    assert len(data["interrogations"][suspect_id]) == 2


def test_case_verdict_history(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]

    # Pre-verdict check
    pre = client.get(f"/api/cases/{case_id}/verdict")
    assert pre.status_code == 200
    assert pre.json()["verdict"] is None

    # Submit verdict
    client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_1",
        "motive_provided": "Gambling debts forced theft.",
        "evidence_ids": ["ev_1"],
        "player_name": "Resumption Tester",
    })

    # Post-verdict check
    post = client.get(f"/api/cases/{case_id}/verdict")
    assert post.status_code == 200
    verdict = post.json()["verdict"]
    assert verdict is not None
    assert verdict["is_correct"] is True
    assert verdict["player_name"] == "Resumption Tester"

    # Verify status in case list
    list_res = client.get("/api/cases")
    cases = list_res.json()["cases"]
    c = next((item for item in cases if item["case_id"] == case_id), None)
    assert c is not None
    assert c["is_completed"] is True
    assert c["status"] == "Solved"


def test_case_invalid_and_missing_handling(client):
    assert client.get("/api/cases/nonexistent_case_12345").status_code == 404
    assert client.get("/api/cases/nonexistent_case_12345/logs").status_code == 404
    assert client.get("/api/cases/nonexistent_case_12345/verdict").status_code == 404


def test_generate_case_offline_categories(client):
    # Test Murder / Medium
    res_murder = client.post("/api/cases/generate", json={"difficulty": "Medium", "crime_type": "Murder"})
    assert res_murder.status_code == 200
    case_murder = res_murder.json()["case"]
    assert case_murder["crime_type"] == "Murder"
    assert case_murder["difficulty"] == "Medium"
    assert "Cyanide" in case_murder["title"]
    assert len(case_murder["suspects"]) >= 4
    assert len(case_murder["evidence"]) >= 6

    # Test Cybercrime / Hard
    res_cyber = client.post("/api/cases/generate", json={"difficulty": "Hard", "crime_type": "Cybercrime"})
    assert res_cyber.status_code == 200
    case_cyber = res_cyber.json()["case"]
    assert case_cyber["crime_type"] == "Cybercrime"
    assert case_cyber["difficulty"] == "Hard"
    assert "Ransomware" in case_cyber["title"]
    assert len(case_cyber["suspects"]) >= 5
    assert len(case_cyber["evidence"]) >= 6


def test_scoring_edge_cases(client):
    gen = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
    case_id = gen.json()["case_id"]

    # 1. Optimal Correct Accusation (Smoking gun + detailed motive + 0 hints)
    res_opt = client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_1",
        "motive_provided": "Owed catastrophic illegal gambling debts and needed the ruby to pay off loan sharks.",
        "evidence_ids": ["ev_1", "ev_2"],
        "player_name": "Optimal Detective",
        "hints_used": 0
    })
    assert res_opt.status_code == 200
    v_opt = res_opt.json()["verdict"]
    assert v_opt["is_correct"] is True
    assert v_opt["score"] >= 90

    # 2. Correct Accusation with Hints Penalty (2 hints used = -10 pts)
    res_hints = client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_1",
        "motive_provided": "Owed catastrophic illegal gambling debts and needed the ruby to pay off loan sharks.",
        "evidence_ids": ["ev_1", "ev_2"],
        "player_name": "Hint Detective",
        "hints_used": 2
    })
    v_hints = res_hints.json()["verdict"]
    assert v_hints["is_correct"] is True
    assert v_hints["score"] == v_opt["score"] - 10

    # 3. Correct Accusation with Zero Evidence Presented (heavy penalty)
    res_no_ev = client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_1",
        "motive_provided": "I just know he did it.",
        "evidence_ids": [],
        "player_name": "Lucky Guesser",
        "hints_used": 0
    })
    v_no_ev = res_no_ev.json()["verdict"]
    assert v_no_ev["is_correct"] is True
    assert v_no_ev["score"] < v_opt["score"]

    # 4. Incorrect Suspect Accusation (capped <= 35)
    res_wrong = client.post(f"/api/cases/{case_id}/judge", json={
        "accused_suspect_id": "suspect_2",
        "motive_provided": "Disliked Lord Blackwood's commissions.",
        "evidence_ids": ["ev_3"],
        "player_name": "Wrong Detective",
        "hints_used": 0
    })
    v_wrong = res_wrong.json()["verdict"]
    assert v_wrong["is_correct"] is False
    assert v_wrong["score"] <= 35
    assert "DISMISSED" in v_wrong["judge_explanation"] or "innocent" in v_wrong["judge_explanation"]


# ==============================================================================
# Dual AI Provider (Gemini + Grok + Offline Fallback) Scenario Tests
# ==============================================================================

import json
from unittest.mock import patch

SAMPLE_AI_CASE = {
    "id": "generated_case_id",
    "title": "The Quantum Syndicate Incident",
    "crime_type": "Cybercrime",
    "difficulty": "Medium",
    "summary": "A high-frequency trading firm was hacked.",
    "victim": {"name": "Dr. Elena Vance", "occupation": "CTO", "background": "Quantum researcher"},
    "ground_truth": {
        "criminal_id": "suspect_1",
        "criminal_name": "Marcus Kane",
        "motive": "Stole decryption keys for black market sale",
        "how_it_was_done": "Bypassed firewall using infected USB drive",
        "smoking_gun_evidence": "ev_1"
    },
    "locations": [{"id": "loc_1", "name": "Server Room", "description": "Humming server racks", "image_type": "office", "evidence_ids": ["ev_1"]}],
    "evidence": [
        {"id": "ev_1", "name": "Infected USB", "category": "Emails", "location": "Server Room", "description": "USB found under desk", "relevance": "Contains malware", "importance": "Critical", "stars": 5},
        {"id": "ev_2", "name": "Terminal Logs", "category": "Phone Call Logs", "location": "Server Room", "description": "SSH session at 2am", "relevance": "Points to Kane", "importance": "Medium", "stars": 3},
        {"id": "ev_3", "name": "Keycard Badge", "category": "Witness Statements", "location": "Server Room", "description": "Entry log badge", "relevance": "Badge used by Kane", "importance": "High", "stars": 4}
    ],
    "suspects": [
        {"id": "suspect_1", "name": "Marcus Kane", "occupation": "Sysadmin", "relationship": "Colleague", "personality": "Quiet", "alibi": "Was at home sleeping", "secret": "In debt", "motive": "Money", "stress_level": "Calm", "suspicion_score": 60},
        {"id": "suspect_2", "name": "Sarah Connor", "occupation": "Security Guard", "relationship": "Contractor", "personality": "Vigilant", "alibi": "Patrolling perimeter", "secret": "Missed shift", "motive": "None", "stress_level": "Calm", "suspicion_score": 20},
        {"id": "suspect_3", "name": "Victor Stone", "occupation": "DevOps Lead", "relationship": "Peer", "personality": "Arrogant", "alibi": "Code review", "secret": "Side gig", "motive": "Ego", "stress_level": "Calm", "suspicion_score": 30}
    ],
    "hints": ["Check the physical server logs", "Look at USB timestamps", "Kane's badge was scanned"]
}

def test_dual_provider_both_keys_valid_gemini_chosen(client):
    """1. Both keys valid -> Gemini response chosen."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "valid-gemini-key-12345",
            "grok_api_key": "valid-grok-key-12345"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "gemini"
        assert data["case"]["provider"] == "gemini"
        assert data["case"]["is_fallback"] is False
        mock_gemini.assert_called_once()
        mock_grok.assert_not_called()

def test_dual_provider_gemini_invalid_grok_response(client):
    """2. Gemini key invalid / HTTP failure -> Grok response."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = Exception("Gemini API returned status 401")
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "invalid-gemini-key",
            "grok_api_key": "valid-grok-key-12345"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "grok"
        assert data["case"]["provider"] == "grok"
        assert data["case"]["is_fallback"] is False
        mock_gemini.assert_called_once()
        mock_grok.assert_called_once()

def test_dual_provider_both_unavailable_offline_response(client):
    """3. Gemini unavailable and Grok unavailable -> offline response."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = Exception("Gemini 500 server error")
        mock_grok.side_effect = Exception("Grok 503 service unavailable")
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Murder",
            "api_key": "mock-gemini-key",
            "grok_api_key": "mock-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "offline"
        assert data["case"]["provider"] == "offline"
        assert data["case"]["is_fallback"] is True

def test_dual_provider_only_gemini_configured(client):
    """4. Only Gemini key configured -> Gemini works."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}), \
         patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "only-gemini-key-12345"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "gemini"
        mock_gemini.assert_called_once()
        mock_grok.assert_not_called()

def test_dual_provider_only_grok_configured(client):
    """5. Only Grok key configured -> Grok works."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}), \
         patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "grok_api_key": "only-grok-key-12345"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "grok"
        mock_gemini.assert_not_called()
        mock_grok.assert_called_once()

def test_dual_provider_no_keys_configured_offline(client):
    """6. No keys configured -> offline response."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}):
        res = client.post("/api/cases/generate", json={
            "difficulty": "Easy",
            "crime_type": "Theft"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "offline"
        assert data["case"]["provider"] == "offline"
        assert data["case"]["is_fallback"] is True
        assert data["case"]["difficulty"] == "Easy"

def test_difficulty_medium_preserved(client):
    """7. Medium difficulty -> Medium case."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}):
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Theft"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["case"]["difficulty"] == "Medium"

def test_difficulty_hard_preserved(client):
    """8. Hard difficulty -> Hard case."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}):
        res = client.post("/api/cases/generate", json={
            "difficulty": "Hard",
            "crime_type": "Murder"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["case"]["difficulty"] == "Hard"

def test_invalid_ai_json_triggers_fallback(client):
    """9. Invalid AI JSON -> next provider or offline fallback works."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = "This is definitely not valid JSON from Gemini!"
        mock_grok.return_value = "```json\n{malformed json from Grok: missing quotes\n```"
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Fraud",
            "api_key": "gemini-key",
            "grok_api_key": "grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "offline"
        assert data["case"]["is_fallback"] is True
        assert data["case"]["difficulty"] == "Medium"

def test_api_timeout_triggers_next_provider(client):
    """10. API timeout -> next provider is attempted."""
    import httpx
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = httpx.ReadTimeout("Gemini connection timed out")
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "timeout-gemini-key",
            "grok_api_key": "grok-backup-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "grok"
        assert data["case"]["is_fallback"] is False
        mock_gemini.assert_called_once()
        mock_grok.assert_called_once()


# =====================================================================
# Master Test Suite: 12 Scenarios for Gemini 503 & Grok Fallback
# =====================================================================

def test_scenario_1_gemini_success(client):
    """1. Gemini success."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Theft",
            "api_key": "valid-gemini-key",
            "grok_api_key": "valid-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "gemini"
        assert data["case"]["provider"] == "gemini"
        assert data["case"]["is_fallback"] is False
        mock_gemini.assert_called_once()
        mock_grok.assert_not_called()


def test_scenario_2_gemini_503_retry_then_success(client):
    """2. Gemini temporary 503, then retry succeeds."""
    import httpx
    req = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent")
    r503 = httpx.Response(503, request=req)
    r200 = httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": json.dumps(SAMPLE_AI_CASE)}]}}]}, request=req)

    with patch("httpx.Client.post", side_effect=[r503, r200]) as mock_post, \
         patch("time.sleep") as mock_sleep, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "temp-503-gemini-key",
            "grok_api_key": "backup-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "gemini"
        assert data["case"]["provider"] == "gemini"
        assert data["case"]["is_fallback"] is False
        assert mock_post.call_count == 2
        mock_sleep.assert_called_once()
        mock_grok.assert_not_called()


def test_scenario_3_gemini_repeated_503_exhausts_retries_grok_succeeds(client):
    """3. Gemini repeated 503 exhausts retries, then Grok succeeds."""
    import httpx
    req = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent")
    r503 = httpx.Response(503, request=req)

    with patch("httpx.Client.post", side_effect=[r503, r503, r503]) as mock_post, \
         patch("time.sleep") as mock_sleep, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "persistent-503-gemini-key",
            "grok_api_key": "working-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "grok"
        assert data["case"]["provider"] == "grok"
        assert data["case"]["is_fallback"] is False
        assert mock_post.call_count == 3
        assert mock_sleep.call_count == 2
        mock_grok.assert_called_once()


def test_scenario_4_gemini_and_grok_fail_offline_fallback(client):
    """4. Gemini failure and Grok failure, then offline fallback."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = Exception("Gemini service unavailable 503")
        mock_grok.side_effect = Exception("Grok rate limit 429")
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Murder",
            "api_key": "failing-gemini-key",
            "grok_api_key": "failing-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert data["provider"] == "offline"
        assert data["case"]["provider"] == "offline"
        assert data["case"]["is_fallback"] is True


def test_scenario_5_missing_gemini_key(client):
    """5. Missing Gemini key -> skips Gemini, tries Grok."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}), \
         patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "",
            "grok_api_key": "valid-grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "grok"
        mock_gemini.assert_not_called()
        mock_grok.assert_called_once()


def test_scenario_6_missing_grok_key(client):
    """6. Gemini fails and Grok key is missing -> skips Grok, uses offline."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}), \
         patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = Exception("Gemini 503 error")
        res = client.post("/api/cases/generate", json={
            "difficulty": "Easy",
            "crime_type": "Theft",
            "api_key": "failing-gemini",
            "grok_api_key": ""
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "offline"
        assert data["case"]["is_fallback"] is True
        mock_gemini.assert_called_once()
        mock_grok.assert_not_called()


def test_scenario_7_invalid_gemini_json(client):
    """7. Invalid Gemini JSON -> Grok fallback is attempted."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = "{malformed JSON from Gemini"
        mock_grok.return_value = json.dumps(SAMPLE_AI_CASE)
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Cybercrime",
            "api_key": "gemini-key",
            "grok_api_key": "grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "grok"
        assert data["case"]["is_fallback"] is False
        mock_gemini.assert_called_once()
        mock_grok.assert_called_once()


def test_scenario_8_invalid_grok_json(client):
    """8. Invalid Grok JSON -> falls back to offline generator."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.side_effect = Exception("Gemini 503")
        mock_grok.return_value = "<html>Not valid JSON from Grok</html>"
        res = client.post("/api/cases/generate", json={
            "difficulty": "Hard",
            "crime_type": "Murder",
            "api_key": "gemini-key",
            "grok_api_key": "grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "offline"
        assert data["case"]["is_fallback"] is True
        assert data["case"]["difficulty"] == "Hard"


def test_scenario_9_empty_provider_response(client):
    """9. Empty provider response -> rejected and triggers fallback."""
    with patch("backend.services.gemini_service.call_gemini_api") as mock_gemini, \
         patch("backend.services.gemini_service.call_grok_api") as mock_grok:
        mock_gemini.return_value = "   "
        mock_grok.return_value = ""
        res = client.post("/api/cases/generate", json={
            "difficulty": "Medium",
            "crime_type": "Theft",
            "api_key": "gemini-key",
            "grok_api_key": "grok-key"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["provider"] == "offline"
        assert data["case"]["is_fallback"] is True


def test_scenario_10_correct_provider_metadata(client):
    """10. Correct provider metadata ("gemini", "grok", "offline")."""
    # Gemini
    with patch("backend.services.gemini_service.call_gemini_api", return_value=json.dumps(SAMPLE_AI_CASE)):
        res1 = client.post("/api/cases/generate", json={"api_key": "valid-gemini-key-123", "difficulty": "Easy", "crime_type": "Theft"})
        d1 = res1.json()
        assert d1["provider"] == "gemini"
        assert d1["case"]["provider"] == "gemini"
        assert d1["case"]["is_fallback"] is False

    # Grok
    with patch("backend.services.gemini_service.call_gemini_api", side_effect=Exception("Gemini failed")), \
         patch("backend.services.gemini_service.call_grok_api", return_value=json.dumps(SAMPLE_AI_CASE)):
        res2 = client.post("/api/cases/generate", json={"api_key": "valid-gemini-key-123", "grok_api_key": "valid-grok-key-123", "difficulty": "Easy", "crime_type": "Theft"})
        d2 = res2.json()
        assert d2["provider"] == "grok"
        assert d2["case"]["provider"] == "grok"
        assert d2["case"]["is_fallback"] is False

    # Offline
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}):
        res3 = client.post("/api/cases/generate", json={"difficulty": "Easy", "crime_type": "Theft"})
        d3 = res3.json()
        assert d3["provider"] == "offline"
        assert d3["case"]["provider"] == "offline"
        assert d3["case"]["is_fallback"] is True


def test_scenario_11_response_schema_preserved(client):
    """11. Existing endpoint response schema preserved without ground_truth leak."""
    res = client.post("/api/cases/generate", json={"difficulty": "Medium", "crime_type": "Murder"})
    assert res.status_code == 200
    data = res.json()
    assert "status" in data and data["status"] == "success"
    assert "case_id" in data and data["case_id"].startswith("case_")
    assert "provider" in data
    assert "case" in data
    c = data["case"]
    required_case_keys = ["id", "title", "crime_type", "difficulty", "summary", "victim", "locations", "evidence", "suspects", "hints", "provider", "is_fallback"]
    for k in required_case_keys:
        assert k in c, f"Missing required case key: {k}"
    assert "ground_truth" not in c, "ground_truth must be stripped from response to prevent cheating"


def test_scenario_12_difficulty_selection_preserved(client):
    """12. Existing difficulty-selection behavior preserved across Easy, Medium, Hard."""
    with patch.dict("os.environ", {"GEMINI_API_KEY": "", "GROK_API_KEY": ""}):
        for diff in ["Easy", "Medium", "Hard"]:
            res = client.post("/api/cases/generate", json={"difficulty": diff, "crime_type": "Theft"})
            assert res.status_code == 200
            data = res.json()
            case = data["case"]
            assert case["difficulty"] == diff
            assert len(case["suspects"]) >= 3
            assert len(case["evidence"]) >= 5
            assert len(case["locations"]) >= 1



