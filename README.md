# DetectAI – AI Crime Investigation Game 🕵️‍♂️

**DetectAI** is a procedurally-generated detective game and cyber-forensic investigation simulation. Unlike traditional mystery games that follow static, predictable scripts, DetectAI dynamically orchestrates unique crime mysteries using Google Gemini Generative AI, or runs seamlessly in full offline mode with rich pre-packaged mystery scenarios.

DetectAI features dual frontends (a feature-packed **Cyber-Noir Streamlit UI** and a lightweight, vintage-styled **Noir HTML5/CSS3/JS Web App**), backed by an asynchronous **FastAPI** engine with persistent **SQLite** case archives, interrogation transcripts, and judicial scoring.

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
                               └──────────┬────────────────┬─────────┘
                                          │                │
                     ┌────────────────────┴───┐        ┌───┴───────────────────────┐
                     ▼                        ▼        ▼                           ▼
            ┌──────────────────┐    ┌────────────────────┐   ┌──────────────────────────────┐
            │  Gemini REST API │    │  SQLite Database   │   │     Offline Mock Engine      │
            │  (2.5-Flash)     │    │  (detectai.db)     │   │     (mock_cases.py)          │
            │                  │    │  - cases           │   │  - Theft (Easy)              │
            │  - Case Gen      │    │  - interrogation   │   │  - Murder (Medium)           │
            │  - Interrogation │    │  - verdicts        │   │  - Cybercrime (Hard)         │
            │  - Judge Scoring │    │  - leaderboard     │   │  Zero API Key Needed         │
            └──────────────────┘    └────────────────────┘   └──────────────────────────────┘
```

---

## 🌟 Key Features

1. **Procedural & Offline Mystery Generation**:
   - Generates infinite unique mystery cases across **Murder**, **Theft**, **Cybercrime**, **Kidnapping**, and **Fraud** when configured with Gemini AI.
   - **Offline Demo Mode**: 3 rich, forensic-ready fallback scenarios (**Theft** at Blackwood Manor, **Murder** via Cyanide Protocol, and **Cybercrime** grid ransomware blackout). Zero external API calls required.
2. **Dynamic AI Interrogation with Memory**:
   - Suspects have defined personas, relationships, secrets, alibis, and real-time stress states (`Calm`, `Defensive`, `Nervous`, `Cornered`).
   - Full conversation memory preserves past dialogue and reacts when confronted with contradictory physical evidence.
3. **Interactive Crime Scene Exploration**:
   - Investigate diverse environments (Research Labs, SCADA Centers, Vaults, Ballrooms, Terraces) to uncover CCTV logs, fingerprints, phone transcripts, and physical artifacts.
4. **Smart Evidence Locker**:
   - Collect and categorize evidence by forensic importance (`Critical`, `Medium`, `Low`). Present specific items directly to suspects to break alibis.
5. **3-Level Progressive Hint Desk**:
   - Level 1: Directional Nudge.
   - Level 2: Timeline & Statement Conflict.
   - Level 3: Smoking Gun Correlation.
6. **AI Judge & Deterministic Scoring**:
   - Impartial judicial evaluation measuring Culprit Accuracy, Evidence Strength, Motive Logic, and Investigation Thoroughness.
   - Includes hint penalties (-5 points per hint) and rewards smoking gun evidence.
7. **Persistent Case Archives & Resumption**:
   - Every case, interrogation transcript, and verdict is saved in SQLite.
   - Resume in-progress investigations or review past verdicts anytime from either frontend.
8. **Dual-Frontend Experience**:
   - **Streamlit UI**: Full-featured detective dashboard with audio synthesis, KPI meters, and notepad.
   - **Noir Web UI**: Vintage case-file single-page web app with folder tabs, stamps, and zero frontend dependencies.

---

## 💻 Tech Stack

- **Backend**: Python 3.9+, FastAPI, Uvicorn, SQLite, Pydantic v2, HTTPX, Mangum (serverless adapter).
- **Frontend 1**: Streamlit, Web Audio API, custom cyber-noir CSS.
- **Frontend 2**: Vanilla HTML5, modern CSS3, ES6 JavaScript (zero npm build step needed).
- **AI Integration**: Google Gemini REST API (`gemini-2.5-flash`).
- **Testing**: Pytest, FastAPI TestClient.
- **Deployment**: Render, Vercel Serverless, Streamlit Community Cloud.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9 or higher (Python 3.10 / 3.11 / 3.12 / 3.14 tested and supported).
- Git.

### 2. Clone and Setup
```bash
git clone https://github.com/Irfanshaikh016/project.git detectai
cd detectai

# Optional: create a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` (optional):
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
BACKEND_URL=http://127.0.0.1:8000
GEMINI_MODEL=gemini-2.5-flash
```
> **Note**: An API key is **not required** to run DetectAI. If left blank or invalid, the game runs in **Offline Demo Mode** with complete pre-packaged cases.

---

## 🎮 Launching the Game

DetectAI includes a unified launcher script (`run.py`):

### Mode A: Streamlit UI (Default)
```bash
python run.py
# or explicitly:
python run.py --mode streamlit
```
*Launches the Streamlit Cyber-Noir detective dashboard at `http://localhost:8501`.*

### Mode B: FastAPI Backend + Noir Web App
```bash
python run.py --backend
# or:
python run.py --web
```
*Starts FastAPI on `http://127.0.0.1:8000`. Visiting `http://127.0.0.1:8000` in any browser loads the Noir case-file single-page web app directly! Interactive Swagger API docs are available at `http://127.0.0.1:8000/docs`.*

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status (`{"status": "ok"}`). |
| `GET` | `/api/cases` | List recent case history with status and score. |
| `POST` | `/api/cases/generate` | Generate a new case (Gemini or offline fallback). |
| `GET` | `/api/cases/{case_id}` | Retrieve sanitized case data (ground truth hidden). |
| `GET` | `/api/cases/{case_id}/logs` | Retrieve all suspect interrogation transcripts. |
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
All 15 integration tests cover:
- Health checks
- Offline multi-category generation (Theft, Murder, Cybercrime)
- Case retrieval & sanitized ground truth protection
- Missing/invalid case ID handling (404/400)
- Suspect interrogation transcripts and conversation memory
- Hint progression (Levels 1, 2, 3)
- Accusation scoring & edge cases (smoking gun bonuses, zero evidence penalties, hint deductions, wrong suspects)
- Leaderboard integration and case title joins
- Frontend static asset mounting

---

## ☁️ Deployment Guide

### 1. Render Deployment (Backend Web Service)
A pre-configured `render.yaml` is included:
1. Connect your repository to [Render](https://render.com).
2. Create a new **Web Service** or use **Blueprint** (pointing to `render.yaml`).
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/api/health`
4. Set `GEMINI_API_KEY` in Render Environment Variables (optional).

### 2. Vercel Serverless Deployment
A pre-configured `vercel.json` and Mangum handler (`api/index.py`) are included:
1. Import repository into [Vercel](https://vercel.com).
2. Framework Preset: **Other**.
3. Environment Variables:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
4. Deploy. The backend API will be live at `https://your-project.vercel.app/api`.

### 3. Streamlit Community Cloud
1. Deploy repository to [Streamlit Community Cloud](https://share.streamlit.io).
2. Main file path: `frontend/app.py`.
3. Secrets:
   ```toml
   BACKEND_URL = "https://your-backend-url.onrender.com"
   GEMINI_API_KEY = "your-api-key"
   ```

---

## 📜 License & Acknowledgments
Built as an SY B.Sc. AI & ML Project. Powered by Google Gemini AI, FastAPI, SQLite, and Streamlit.
