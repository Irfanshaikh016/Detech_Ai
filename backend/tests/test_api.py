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
