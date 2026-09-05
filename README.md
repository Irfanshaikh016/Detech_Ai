# DetectAI – AI Crime Investigation Game 🕵️‍♂️

**DetectAI** is an AI-assisted crime investigation game and cyber-forensic simulation. Each investigation presents a unique mystery with suspects, motives, evidence, interrogation, clues, and an AI Judge. Players investigate the case, collect evidence, question suspects, and submit an accusation.

The project uses a vintage **Noir Web App** powered by FastAPI, Gemini AI integration, SQLite case archives, and an offline fallback mode. The current production deployment runs as a **single Render Web Service**.

## 🌐 Live Demo

- **Application:** https://detech-ai.onrender.com
- **Health Check:** https://detech-ai.onrender.com/api/health
- **API Documentation:** https://detech-ai.onrender.com/docs
- **Repository:** https://github.com/Irfanshaikh016/Detech_Ai

> The frontend automatically uses the current application origin as its backend URL. Users do not need to configure a backend URL or enter an API key in the browser.

---

## 🏗️ System Architecture

```text
                         ┌──────────────────────────────┐
                         │       DetectAI Web App        │
                         │   HTML + CSS + Vanilla JS     │
                         └──────────────┬───────────────┘
                                        │ Same-origin REST API
                                        ▼
                         ┌──────────────────────────────┐
                         │       FastAPI Backend         │
                         │       backend/main.py        │
                         └───────┬───────────┬──────────┘
                                 │           │
                 ┌───────────────┘           └────────────────┐
                 ▼                                            ▼
       ┌────────────────────┐                       ┌────────────────────┐
       │ Google Gemini API  │                       │ SQLite Database    │
       │ Case generation    │                       │ Cases, logs, scores │
       │ Interrogation      │                       │ Leaderboard         │
       │ AI Judge           │                       └────────────────────┘
       └────────────────────┘
                 │
                 ▼
       ┌────────────────────┐
       │ Offline Mock Engine│
       │ Used when AI keys  │
       │ are unavailable    │
       └────────────────────┘
```

### Deployment model

- **Hosting:** Render Web Service
- **Frontend:** Served directly by FastAPI
- **Backend:** FastAPI + Uvicorn
- **Database:** SQLite
- **AI:** Gemini/Grok through server-side environment variables
- **Source control:** GitHub
- **Deployment:** GitHub push → Render deployment

---

## 🌟 Key Features

1. **Procedural mystery generation** across Murder, Theft, Cybercrime, Kidnapping, and Fraud.
2. **Offline Demo Mode** with pre-packaged cases when AI keys are unavailable.
3. **Interactive onboarding flow**: Home → How to Play → Rules & Guidelines → Case Setup → Case Generation Loader → Case Briefing.
4. **Dynamic suspect interrogation** with conversation memory, personalities, secrets, alibis, and stress states.
5. **Interactive crime-scene investigation** with clues, CCTV records, fingerprints, transcripts, and physical evidence.
6. **Evidence Locker** for collecting and organizing important clues.
7. **Three-level hint system** with progressive guidance and scoring penalties.
8. **AI Judge and deterministic scoring** based on culprit accuracy, evidence strength, motive logic, and investigation thoroughness.
9. **Case archives and leaderboard** backed by SQLite.
10. **Responsive Noir interface** built with HTML5, CSS3, and vanilla JavaScript.
11. **Secure API-key handling** with AI keys kept on the server.
12. **Automatic same-origin backend configuration** without a settings popup.

---

## 🎮 Main User Flow

```text
Home
  ↓
How to Play
  ↓
Rules & Guidelines
  ↓
Case Setup
  ↓
Open a New Case File
  ↓
Case Generation Loader
  ↓
Case Briefing
  ↓
Investigate Evidence + Question Suspects
  ↓
Request Hints When Needed
  ↓
Submit Accusation
  ↓
AI Judge Verdict + Score
```

### Navigation and security updates

- The **Backend Settings** modal and gear button have been removed.
- The frontend resolves the backend automatically:

```javascript
const BACKEND_URL = window.location.origin;
```

- API keys are never entered, stored, or exposed in the frontend.
- Browser navigation supports screen navigation and history handling.
- A favicon is served through `/favicon.ico`.

---

## 💻 Tech Stack

- **Language:** Python 3.9+
- **Backend:** FastAPI, Uvicorn, Pydantic, HTTPX
- **Frontend:** HTML5, CSS3, Vanilla JavaScript, ES6
- **AI Integration:** Google Gemini REST API and optional Grok integration
- **Database:** SQLite
- **Testing:** Pytest, FastAPI TestClient
- **Deployment:** Render
- **Version Control:** Git and GitHub

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
│   ├── mock_cases.py       # Offline fallback cases
│   └── tests/
│       └── test_api.py     # Automated tests
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
git clone https://github.com/Irfanshaikh016/Detech_Ai.git
cd Detech_Ai
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
GROK_API_KEY=your_grok_api_key_here
GEMINI_MODEL=gemini-2.5-flash
PORT=8000
```

> API keys are optional. Without a valid key, DetectAI uses its offline mock engine.

### Run locally

```bash
python run.py --web
```

Open `http://127.0.0.1:8000` in your browser.

API documentation is available at `http://127.0.0.1:8000/docs`.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status |
| `GET` | `/api/cases` | List recent case history |
| `POST` | `/api/cases/generate` | Generate a new case |
| `GET` | `/api/cases/{case_id}` | Retrieve sanitized case data |
| `GET` | `/api/cases/{case_id}/logs` | Retrieve interrogation transcripts |
| `GET` | `/api/cases/{case_id}/verdict` | Retrieve a saved verdict |
| `POST` | `/api/cases/{case_id}/interrogate` | Ask a suspect a question |
| `GET` | `/api/cases/{case_id}/interrogate/{suspect_id}` | Retrieve suspect history |
| `POST` | `/api/cases/{case_id}/hint` | Request a progressive hint |
| `POST` | `/api/cases/{case_id}/judge` | Submit an accusation |
| `GET` | `/api/cases/leaderboard` | View detective rankings |

---

## 🧪 Testing

Run the complete test suite:

```bash
pytest backend/tests -v
```

The latest implementation report recorded:

```text
40 passed
```

Coverage includes health checks, offline case generation, case retrieval, invalid-case handling, interrogation memory, hint progression, accusation scoring, leaderboard integration, frontend asset mounting, onboarding navigation, settings-modal removal, and case-generation integration.

---

## ☁️ Render Deployment

The application is deployed as a **single Render Web Service**.

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
GEMINI_MODEL=gemini-2.5-flash
```

The API keys must remain server-side. Do not place them in `frontend/app.js` or expose them through browser settings.

### Deployment workflow

```text
GitHub push
   ↓
Render detects new commit
   ↓
Render installs dependencies
   ↓
Render starts FastAPI
   ↓
Health check passes
   ↓
Application becomes live
```

After deployment, verify:

```text
https://detech-ai.onrender.com
https://detech-ai.onrender.com/api/health
https://detech-ai.onrender.com/docs
```

---

## ⚡ Performance and Optimization

### Token consumption

- Send compact case summaries instead of complete database records.
- Avoid repeating system instructions and evidence.
- Limit conversation history to relevant messages.
- Use structured JSON responses.
- Set output-token limits.
- Cache repeated AI results when appropriate.
- Use offline fallback for demo scenarios.

### Response latency

- Use asynchronous FastAPI endpoints for AI operations.
- Avoid duplicate frontend API requests.
- Select only required database fields.
- Add indexes to frequently queried columns.
- Cache static assets and repeated responses.
- Use loading states for case generation.
- Keep AI processing separate from normal page navigation.

### Frontend optimization

- Use `defer` for JavaScript loading.
- Keep the frontend dependency-free.
- Load only the required screen content.
- Compress images and static assets.
- Debounce search and filter inputs.

---

## 🔄 CI/CD with GitHub Actions

The recommended pipeline is:

```text
Pull request or push to main
          ↓
Install dependencies
          ↓
Run automated tests
          ↓
Validate frontend assets
          ↓
Build/check application
          ↓
Deploy to Render
```

The workflow can be placed at `.github/workflows/ci-cd.yml`. Deployment should occur only after the test job succeeds. Render can handle the final production deployment through its GitHub integration or deploy hook.

---

## 🛠️ Troubleshooting

### Homepage loads but a button does nothing

1. Open browser DevTools with `F12`.
2. Check the **Console** tab for JavaScript errors.
3. Check the **Network** tab for failed `app.js` or frontend asset requests.
4. Confirm the deployed Render commit is the latest commit.
5. Hard-refresh the browser with `Ctrl + Shift + R`.

### Favicon returns 404

Confirm that `frontend/favicon.ico` exists and that the backend serves `/favicon.ico`. A favicon error normally does not prevent the application from working.

### AI generation fails

- Verify `GEMINI_API_KEY` or `GROK_API_KEY` in Render environment variables.
- Confirm the keys are not exposed in frontend code.
- Check Render logs.
- Test offline mode without an API key.

### API returns 404

- Confirm the request uses the correct `/api/...` endpoint.
- Confirm the frontend uses `window.location.origin`.
- Check that the Render service is running and the health endpoint returns successfully.

---

## 📜 License and Acknowledgments

Built as an SY B.Sc. AI & ML project. Powered by FastAPI, SQLite, Google Gemini AI, and a vintage Noir web interface.
