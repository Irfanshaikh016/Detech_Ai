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
        "motive_provided": "Debt motive.",
        "evidence_ids": ["ev_2"],
        "player_name": "Leaderboard Tester",
    })

    res = client.get("/api/cases/leaderboard")
    assert res.status_code == 200
    rows = res.json()["leaderboard"]
    assert len(rows) >= 1
    assert rows[0]["player_name"] == "Leaderboard Tester"
    assert "case_title" in rows[0]
    assert "case_id" in rows[0]


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
