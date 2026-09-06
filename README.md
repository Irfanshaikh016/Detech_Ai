# DetectAI – AI Crime Investigation Game 🕵️‍♂️

**DetectAI** is an AI-assisted crime investigation game and cyber-forensic simulation. Unlike traditional mystery games that follow static, predictable scripts, DetectAI dynamically orchestrates unique crime mysteries using Google Gemini Generative AI with Grok API secondary fallback, or runs seamlessly in full offline mode with rich, pre-packaged scenario missions.

DetectAI features dual frontends (a feature-packed **Cyber-Noir Streamlit UI** and a lightweight, vintage-styled **Noir HTML5/CSS3/JS Single Page Web App**), backed by an asynchronous **FastAPI** engine with persistent **SQLite** case archives, interrogation transcripts, scenario catalogs, and judicial scoring.

## 🌐 Live Demo

- **Application:** https://detech-ai.onrender.com
- **Health Check:** https://detech-ai.onrender.com/api/health
- **API Documentation:** https://detech-ai.onrender.com/docs
- **Repository:** https://github.com/Irfanshaikh016/Detech_Ai

> The frontend automatically uses the current application origin as its backend URL. Users do not need to configure a backend URL or enter an API key in the browser.

---

## 🏗️ System Architecture

```text
                               ┌────────────────────────────────────────┐
                               │               DetectAI                 │
                               └──────────────────┬─────────────────────┘
                                                  │
                ┌─────────────────────────────────┴─────────────────────────────────┐
                ▼                                                                   ▼
    ┌─────────────────────────────┐                                   ┌─────────────────────────────┐
    │     Streamlit Interface     │                                   │      Noir Web App (SPA)     │
    │     (frontend/app.py)       │                                   │      (index.html + app.js)  │
    │     Port 8501               │                                   │      Served at / on Port 8000│
    └──────────────┬──────────────┘                                   └──────────────┬──────────────┘
                   │                                                                 │
                   └──────────────────────────────┬──────────────────────────────────┘
                                                  │ HTTP REST / JSON
                                                  ▼
                               ┌─────────────────────────────────────┐
                               │           FastAPI Backend           │
                               │           (backend/main.py)         │
                               │           Port 8000                 │
                               └──────────┬──────────────┬───────────┘
                                          │              │
                     ┌────────────────────┴───┐      ┌───┴───────────────────────┐
                     ▼                        ▼      ▼                           ▼
            ┌──────────────────┐    ┌────────────────────┐   ┌──────────────────────────────┐
            │ AI Providers     │    │  SQLite Database   │   │     Offline Mock Engine      │
            │                  │    │  (detectai.db)     │   │     (mock_cases.py)          │
            │  1. Gemini REST  │    │  - cases           │   │  - Theft (Easy)              │
            │  2. Grok Fallback│    │  - interrogation   │   │  - Murder (Medium)           │
            │  3. Offline Auto │    │  - verdicts        │   │  - Cybercrime (Hard)         │
            └──────────────────┘    │  - leaderboard     │   │  Zero API Key Needed         │
                                    └────────────────────┘   └──────────────────────────────┘
```

---

## 🌟 5 Core Working Features

### 1. Scenario-Based Missions
- **Mission Selector**: Choose between dynamically generated AI mysteries (Procedural Mystery) or curated forensic scenarios:
  - *The Blackwood Manor Heist* (Theft / Easy) — Recover the stolen Bloodfire Ruby.
  - *The Cyanide Protocol* (Murder / Medium) — Investigate poisoned pharmaceutical research.
  - *Project Blackout* (Cybercrime / Hard) — Unmask the insider behind a SCADA grid ransomware attack.
- Endpoints: `GET /api/scenarios` and `POST /api/cases/generate` with `scenario_id`.

### 2. Investigation Gameplay Loop
- **Multi-Location Crime Scenes**: Investigate individual rooms, research facilities, and server hubs to discover hidden forensic clues.
- **Dynamic Case Notebook & Status**: Track visited locations, gathered clues, ongoing interrogation notes, and case status in real time.

### 3. Evidence Collection & Suspect Interrogation
- **Interactive Clue Inspection**: Inspect collected evidence in a dedicated forensic examination modal featuring item category, forensic observation details, and investigative relevance.
- **Suspect Interrogation with Memory**: Question suspects individually with natural language questions and present physical evidence to expose contradictions. Suspects update their emotional stress level (`Calm`, `Defensive`, `Nervous`, `Cornered`) in response.

### 4. Progressive Hints & Deterministic Detective Scoring
- **3-Tier Progressive Hint Desk**: Sequential, locked hint unlocks (Level 1: Directional Nudge, Level 2: Timeline Conflict, Level 3: Smoking Gun Correlation).
- **Impartial Judicial Evaluation**: The Judge evaluates accusation accuracy, motive explanation, and supporting evidence citations. Scores (0–100) incorporate smoking gun bonuses (+15) and hint penalties (-5 per hint used).

### 5. Replayability & Case Archives
- **Case Replay**: Replay any solved or unsolved case from the beginning with `POST /api/cases/{case_id}/replay` or the "🔄 Replay This Case" button.
- **Central Case Archives**: Persistent SQLite records store every case, interrogation log, and verdict. Resume in-progress investigations or review historical verdicts at any time.
- **Global Leaderboard**: Track high scores, solved cases, and detective rankings.

---

## 🎮 Main User Flow

```text
Home
  ↓
How to Play
  ↓
Rules & Guidelines
  ↓
Case Setup (Choose Scenario / Crime / Difficulty)
  ↓
Open a New Case File
  ↓
Case Generation Loader
  ↓
Case Briefing
  ↓
Investigate Locations → Inspect Evidence → Question Suspects
  ↓
Request Hints When Needed
  ↓
Submit Accusation
  ↓
AI Judge Verdict + Score
  ↓
Replay Case 🔄 / View Leaderboard / Case Archives
```

---

## 💻 Tech Stack

- **Backend**: Python 3.9+, FastAPI, Uvicorn, SQLite, Pydantic v2, HTTPX, Mangum (serverless adapter).
- **Frontend 1**: Streamlit, Web Audio API, custom cyber-noir CSS.
- **Frontend 2**: Vanilla HTML5, modern CSS3, ES6 JavaScript (zero npm build step needed).
- **AI Providers**: Google Gemini API (`gemini-3.5-flash-lite`), Grok API (`grok-beta` / OpenAI compatible), Offline Mock Fallback.
- **Testing**: Pytest, FastAPI TestClient (44 integration tests).
- **Deployment**: Render, Vercel Serverless, Streamlit Community Cloud.

---

## 📁 Project Structure

```text
DetectAI/
├── frontend/
│   ├── index.html          # Noir web interface
│   ├── app.js              # Navigation, API calls, and game logic
│   └── favicon.ico         # Browser favicon
├── backend/
│   ├── main.py             # FastAPI application
│   ├── routes/             # Case & API routers
│   ├── services/           # Gemini/Grok API & mock cases
│   ├── database/           # SQLite DB layer
│   └── tests/
│       └── test_api.py     # Automated integration tests
├── requirements.txt
├── render.yaml
├── run.py
├── .env.example
└── README.md
```

---

## 🚀 Local Setup

### Prerequisites

- Python 3.9 or higher
- Git
- Optional Gemini or Grok API key for AI-generated cases

### Clone the repository

```bash
git clone https://github.com/Irfanshaikh016/Detech_Ai.git detectai
cd detectai
```

### Create a virtual environment

```bash
python -m venv venv
```

**Windows:**
```bash
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file from `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
GROK_API_KEY=your_grok_api_key_here
PORT=8000
BACKEND_URL=http://127.0.0.1:8000
```

> **Note**: API keys are **not required** to play DetectAI. If keys are missing or unavailable, the game runs automatically in **Offline Mode** with complete scenario missions.

### Run locally

DetectAI includes a unified launcher script (`run.py`):

**Mode A: FastAPI Backend + Noir Web App (Recommended)**
```bash
python run.py --backend
# or:
python run.py --web
```
*Starts FastAPI on `http://127.0.0.1:8000`. Visiting `http://127.0.0.1:8000` in your browser loads the Noir case-file single-page web app directly! Interactive Swagger API docs are available at `http://127.0.0.1:8000/docs`.*

**Mode B: Streamlit UI**
```bash
python run.py --mode streamlit
```
*Launches the Streamlit Cyber-Noir detective dashboard at `http://localhost:8501`.*

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status (`{"status": "ok"}`). |
| `GET` | `/api/scenarios` | List curated scenario missions catalog. |
| `GET` | `/api/cases` | List recent case history with status and score. |
| `POST` | `/api/cases/generate` | Generate a new case (Gemini → Grok → Offline fallback) or scenario mission. |
| `GET` | `/api/cases/{case_id}` | Retrieve sanitized case data (ground truth hidden). |
| `POST` | `/api/cases/{case_id}/replay` | Reset case logs and verdict to replay case from beginning. |
| `GET` | `/api/cases/{case_id}/logs` | Retrieve all suspect interrogation transcripts for a case. |
| `GET` | `/api/cases/{case_id}/verdict`| Retrieve saved verdict if completed. |
| `POST` | `/api/cases/{case_id}/interrogate` | Interrogate a suspect with question & evidence. |
| `GET` | `/api/cases/{case_id}/interrogate/{suspect_id}` | Retrieve interrogation history for a suspect. |
| `POST` | `/api/cases/{case_id}/hint` | Request progressive hint (Level 1–3). |
| `POST` | `/api/cases/{case_id}/judge` | Submit accusation for AI Judge verdict & score. |
| `GET` | `/api/cases/leaderboard` | View top detective scores and rankings. |

---

## 🧪 Running the Test Suite

Run the complete automated test suite with pytest:
```bash
pytest backend/tests -v
```

All 44 integration tests cover:
- Health checks
- Scenario missions catalog & scenario ID case generation
- Offline multi-category generation (Theft, Murder, Cybercrime)
- Case retrieval & sanitized ground truth protection
- Missing/invalid case ID handling (404/400)
- Suspect interrogation transcripts and conversation memory
- Hint progression (Levels 1, 2, 3)
- Accusation scoring & edge cases (smoking gun bonuses, zero evidence penalties, hint deductions, wrong suspects)
- Leaderboard integration and case title joins
- Dual AI Provider pipelines (Gemini 503 retry, Grok fallback, offline fallback)
- Evidence inspection modal and Case Replay UI/endpoints
- Frontend static asset mounting & complete onboarding navigation flow

---

## ☁️ Render Deployment

The application is deployed as a single Render Web Service.

### Render settings

```text
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn backend.main:app --host 0.0.0.0 --port $PORT

Health Check Path:
/api/health
```

### Environment variables

Add these in **Render → Environment → Environment Variables**:

```text
GEMINI_API_KEY=your_gemini_api_key
GROK_API_KEY=your_grok_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

The API keys remain server-side and are never exposed to the frontend.

---

## 📜 License and Acknowledgments

Built as an SY B.Sc. AI & ML Project. Powered by Google Gemini AI, Grok API, FastAPI, SQLite, and Streamlit.

