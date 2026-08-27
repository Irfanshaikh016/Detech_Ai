# DetectAI – AI Crime Investigation Game 🕵️‍♂️

**DetectAI** is an AI-powered detective game built as an SY B.Sc. AI & ML project/hackathon application. Traditional detective games have fixed stories that become predictable after one playthrough; **DetectAI** uses Generative AI to craft a completely unique crime scenario, dynamic suspects with memory, smart evidence logs, interactive location exploration, progressive AI hints, and an **AI Judge** that evaluates your final accusation and awards a Detective Score (0–100).

---

## 🏗️ System Architecture

```text
Player
   │
Streamlit UI Frontend (Port 8501)
   │
FastAPI Python Backend (Port 8000)
 ├───────────────────┐
 │                   │
Gemini 1.5/2.0 API  SQLite Database (`detectai.db`)
 │                   │
Crime Generation     Save Case State & Chat Logs
 │
Prompt Engineering & AI Suspect Interrogation Engine
 │
AI Judge Courtroom (Detective Score 0-100 & Verdict Breakdown)
```

---

## 🔥 Key Features

1. **Dynamic Crime Generation**: Generates infinite unique mystery cases across **Murder**, **Theft**, **Kidnapping**, **Cybercrime**, and **Fraud**.
2. **AI Suspects with Memory**: Each suspect features distinct personality, occupation, relation, alibi, secret, motive, and real-time stress levels (`Calm`, `Defensive`, `Nervous`, `Cornered`).
3. **Crime Scene Exploration**: Scan locations (Victim's House, Office, Crime Scene, Parking Area, Cafe, Hotel) to discover CCTV footage, fingerprints, phone logs, emails, and financial records.
4. **Smart Evidence Locker**: Collect and present specific evidence to suspects during interrogation to break their alibis.
5. **3-Level Progressive AI Hint Desk**: Offers directional nudges, timeline conflict highlights, and smoking gun clues.
6. **AI Judge & Score System**: Evaluates player accusations, motive logic, and supporting evidence, awarding a final **Detective Score (0–100)** with judge feedback.
7. **Difficulty Levels**:
   - **Easy**: 3 suspects, 5 clues
   - **Medium**: 5 suspects, 10 clues
   - **Hard**: 8 suspects, 15 clues with red herrings

---

## 🚀 Quick Start Guide

### 1. Install Backend Dependencies & Start Server

```bash
cd backend
pip install -r requirements.txt
python main.py
```
*The FastAPI backend will start at `http://127.0.0.1:8000` (Docs: `http://127.0.0.1:8000/docs`).*

### 2. Install Frontend Dependencies & Start App

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
*The Streamlit detective interface will open automatically in your browser at `http://localhost:8501`.*

---

## 🔑 API Key Configuration

The backend reads your Gemini API Key from `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
```
Get a free key at https://aistudio.google.com/apikey. Never commit a real key to source control — `.env` is listed in `.gitignore` for this reason.

Alternatively, you can enter or override your Gemini API key directly in the Streamlit UI sidebar!

> ⚠️ The model used is set via `GEMINI_MODEL` (defaults to `gemini-2.5-flash`) in `backend/services/gemini_service.py`. Google retires Gemini model IDs on a rolling basis — if case generation starts silently falling back to the offline mock case, check https://ai.google.dev/gemini-api/docs/deprecations for the current model name.

---

## 🎓 Learning Outcomes & Concepts

- **Generative AI & LLM Integration**: Dynamic JSON structured prompting with Google Gemini API.
- **Prompt Engineering**: Roleplay system instructions with stress state machines and character consistency memory.
- **Full-Stack REST Architecture**: FastAPI backend + SQLite database + Streamlit UI frontend.
