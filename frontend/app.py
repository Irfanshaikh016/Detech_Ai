import os
import sys
import json
import time
import requests
import random
import uuid
import streamlit as st

# Add project root and backend directory to sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.abspath(os.path.join(ROOT_DIR, "backend"))
for p in (ROOT_DIR, BACKEND_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Import backend modules directly
USE_DIRECT_SERVICES = False
try:
    try:
        import backend.database.db as db
        import backend.services.gemini_service as gemini_service
    except ImportError:
        import database.db as db
        import services.gemini_service as gemini_service
    db.init_db()
    USE_DIRECT_SERVICES = True
except Exception as e:
    print(f"[DetectAI] Direct backend import note: {e}")

# Configure Streamlit page layout and theme
st.set_page_config(
    page_title="DetectAI - AI Crime Investigation Game",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Audio Chimes (Base64 WAV Data URIs for subtle sound effects)
SOUND_CLUE = "data:audio/wav;base64,UklGRl9vAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU...AEAAAAAA=="

def play_sound(sound_type="clue"):
    if st.session_state.get("sound_enabled", True):
        if sound_type == "clue":
            freq = 587.33 # D5
        elif sound_type == "interrogate":
            freq = 440.00 # A4
        elif sound_type == "victory":
            freq = 880.00 # A5
        else:
            freq = 220.00 # A3
            
        js_audio = f"""
        <script>
        (function() {{
            try {{
                var AudioContext = window.AudioContext || window.webkitAudioContext;
                if (!AudioContext) return;
                var ctx = new AudioContext();
                var osc = ctx.createOscillator();
                var gain = ctx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime({freq}, ctx.currentTime);
                gain.gain.setValueAtTime(0.15, ctx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 0.35);
            }} catch(e) {{}}
        }})();
        </script>
        """
        st.components.v1.html(js_audio, height=0, width=0)

# Custom Dark Cyber-Noir Visual Design System CSS
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Dark Cyber Noir Theme Background */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #161b26 0%, #0d0f17 70%, #050609 100%);
        color: #e2e8f0;
    }

    /* Hero & Glassmorphism Header */
    .hero-header {
        background: rgba(22, 27, 38, 0.75);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(0, 242, 254, 0.25);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 242, 254, 0.05);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 242, 254, 0.08) 0%, transparent 60%);
        pointer-events: none;
    }

    .game-title {
        font-size: 3.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00c6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
        letter-spacing: -1px;
    }

    .game-subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 400;
    }

    /* KPI Dashboard Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 14px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: #00f2fe;
    }
    .kpi-title {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00f2fe;
    }

    /* Stress & Demeanor Badges */
    .badge-calm {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-defensive {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-nervous {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-cornered {
        background-color: rgba(168, 85, 247, 0.15);
        color: #a855f7;
        border: 1px solid rgba(168, 85, 247, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        animation: pulse 1.5s infinite;
    }

    /* Evidence Cards with Importance Colors */
    .evidence-card {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: transform 0.2s ease;
    }
    .evidence-card:hover {
        transform: translateY(-2px);
    }
    .evidence-critical {
        border-left: 5px solid #ef4444;
        border-top: 1px solid rgba(239, 68, 68, 0.2);
    }
    .evidence-medium {
        border-left: 5px solid #f59e0b;
        border-top: 1px solid rgba(245, 158, 11, 0.2);
    }
    .evidence-low {
        border-left: 5px solid #10b981;
        border-top: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* Location Image Card */
    .location-img-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    .location-img-card:hover {
        border-color: #00f2fe;
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0, 242, 254, 0.2);
    }

    /* Courtroom Score Dial */
    .score-circle {
        background: radial-gradient(circle, rgba(0,242,254,0.2) 0%, rgba(0,0,0,0) 70%);
        border: 4px solid #00f2fe;
        border-radius: 50%;
        width: 150px;
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        margin: 0 auto 20px auto;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.4);
    }
    .score-number {
        font-size: 3.2rem;
        font-weight: 800;
        color: #00f2fe;
        line-height: 1;
    }

    /* Achievement Badge */
    .achievement-badge {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 215, 0, 0.4);
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Custom Streamlit Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(0, 242, 254, 0.15) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Curated Unsplash Stock Images for Crime Scene Locations
LOCATION_IMAGES = {
    "warehouse": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=600&q=80",
    "apartment": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=600&q=80",
    "house": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80",
    "office": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=600&q=80",
    "parking": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80",
    "hotel": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80",
    "cafe": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=600&q=80",
    "lab": "https://images.unsplash.com/photo-1581093450021-4a7360e9a6b5?auto=format&fit=crop&w=600&q=80",
    "default": "https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80"
}

def get_location_image(image_type="default"):
    key = str(image_type).lower().strip()
    return LOCATION_IMAGES.get(key, LOCATION_IMAGES["default"])

# Session State Initialization
if "case_id" not in st.session_state:
    st.session_state.case_id = None
if "case_data" not in st.session_state:
    st.session_state.case_data = None
if "collected_evidence" not in st.session_state:
    st.session_state.collected_evidence = []
if "visited_locations" not in st.session_state:
    st.session_state.visited_locations = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {} # suspect_id -> list of msgs
if "verdict" not in st.session_state:
    st.session_state.verdict = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")
if "grok_api_key" not in st.session_state:
    st.session_state.grok_api_key = os.getenv("GROK_API_KEY", "")
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "player_name" not in st.session_state:
    st.session_state.player_name = "Detective Irfan"
if "detective_notes" not in st.session_state:
    st.session_state.detective_notes = ""
if "achievements" not in st.session_state:
    st.session_state.achievements = set()
if "sound_enabled" not in st.session_state:
    st.session_state.sound_enabled = True
if "used_hints" not in st.session_state:
    st.session_state.used_hints = 0
if "suspect_suspicion" not in st.session_state:
    st.session_state.suspect_suspicion = {} # suspect_id -> score (0-100)

def unlock_achievement(title, icon="🏆"):
    if title not in st.session_state.achievements:
        st.session_state.achievements.add(title)
        st.toast(f"ACHIEVEMENT UNLOCKED: {icon} {title}!", icon="🎉")
        play_sound("victory")

def resume_case_session(case_id):
    """Resume a previously created or in-progress case from database"""
    if not case_id or not str(case_id).strip():
        st.error("Invalid case ID provided.")
        return
    
    case_id = str(case_id).strip()
    case_raw = None
    if USE_DIRECT_SERVICES:
        try:
            case_raw = db.get_case(case_id)
        except Exception as e:
            print(f"[DetectAI] Error direct fetching case {case_id}: {e}")
    if not case_raw:
        try:
            res = requests.get(f"{BACKEND_URL}/api/cases/{case_id}", timeout=10)
            if res.status_code == 200:
                case_raw = res.json().get("case")
        except Exception as e:
            st.error(f"Error communicating with backend: {e}")
            return
            
    if not case_raw:
        st.error(f"Case '{case_id}' was not found in the database.")
        return

    sanitized_case = dict(case_raw)
    sanitized_case.pop("ground_truth", None)

    # Fetch logs
    all_logs = {}
    if USE_DIRECT_SERVICES:
        try:
            all_logs = db.get_all_interrogation_logs_for_case(case_id)
        except Exception:
            pass
    if not all_logs:
        try:
            lres = requests.get(f"{BACKEND_URL}/api/cases/{case_id}/logs", timeout=5)
            if lres.status_code == 200:
                all_logs = lres.json().get("interrogations", {})
        except Exception:
            pass

    # Fetch verdict if case was already completed
    verdict = None
    if USE_DIRECT_SERVICES:
        try:
            verdict = db.get_case_verdict(case_id)
        except Exception:
            pass
    if not verdict:
        try:
            vres = requests.get(f"{BACKEND_URL}/api/cases/{case_id}/verdict", timeout=5)
            if vres.status_code == 200:
                verdict = vres.json().get("verdict")
        except Exception:
            pass

    # Reconstruct evidence and locations
    all_evidence = sanitized_case.get("evidence", [])
    all_evidence_map = {e["id"]: e for e in all_evidence}
    all_locations = sanitized_case.get("locations", [])
    
    collected_ev = []
    visited_locs = []
    if verdict:
        collected_ev = list(all_evidence)
        visited_locs = [loc.get("id") for loc in all_locations]
    else:
        for s_id, s_logs in (all_logs or {}).items():
            for entry in s_logs:
                msg = entry.get("message") or entry.get("content") or ""
                for eid, ev in all_evidence_map.items():
                    if ev.get("name", "") in msg and ev not in collected_ev:
                        collected_ev.append(ev)
        for loc in all_locations:
            loc_ev_ids = loc.get("evidence_ids", [])
            if any(eid in [ce["id"] for ce in collected_ev] for eid in loc_ev_ids):
                if loc.get("id") not in visited_locs:
                    visited_locs.append(loc.get("id"))

    st.session_state.case_id = case_id
    st.session_state.case_data = sanitized_case
    st.session_state.collected_evidence = collected_ev
    st.session_state.visited_locations = visited_locs
    st.session_state.chat_history = all_logs or {}
    st.session_state.verdict = verdict
    st.session_state.start_time = time.time()
    st.session_state.used_hints = 0
    st.session_state.suspect_suspicion = {s["id"]: s.get("suspicion_score", 35) for s in sanitized_case.get("suspects", [])}

    st.success(f"Resumed case: {sanitized_case.get('title', case_id)}")
    play_sound("clue")
    st.rerun()

# Sidebar: Controls, Audio Toggle, Notes & Leaderboard Preview
with st.sidebar:
    st.image("https://img.icons8.com/isometric-line/100/00f2fe/detective.png", width=64)
    st.markdown("### 🕵️‍♂️ DetectAI Hub")
    
    st.session_state.player_name = st.text_input("Detective Name", value=st.session_state.player_name)
    st.session_state.sound_enabled = st.checkbox("🔊 Sound Effects", value=st.session_state.sound_enabled)
    
    st.markdown("---")
    st.markdown("#### ⚙️ Dual AI Provider Setup")
    api_key_input = st.text_input(
        "Gemini API Key (Primary)",
        value=st.session_state.api_key,
        type="password",
        help="Primary provider key. Leave blank to use server environment."
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    grok_key_input = st.text_input(
        "Grok API Key (Secondary Failover)",
        value=st.session_state.grok_api_key,
        type="password",
        help="Secondary provider key (xAI Grok). Used automatically if Gemini fails."
    )
    if grok_key_input:
        st.session_state.grok_api_key = grok_key_input

    st.markdown("---")
    st.markdown("#### 🎮 New Investigation")
    difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    crime_type = st.selectbox("Crime Category", ["Murder", "Theft", "Kidnapping", "Cybercrime", "Fraud"], index=0)

    # Dynamic Detective Loading Messages
    loading_messages = [
        "🔍 Searching crime scene database...",
        "🧬 Analyzing fingerprint patterns & DNA traces...",
        "📞 Tracing encrypted phone call logs...",
        "🤖 Profiling AI suspects & alibi records...",
        "⚖️ Preparing judicial indictment file..."
    ]

    if st.button("🚀 Generate AI Crime Case", type="primary", use_container_width=True):
        selected_msg = random.choice(loading_messages)
        with st.spinner(selected_msg):
            case_id = None
            case_dict = None

            if USE_DIRECT_SERVICES:
                try:
                    case_dict = gemini_service.generate_crime_case(
                        difficulty=difficulty,
                        crime_type=crime_type,
                        api_key=st.session_state.api_key,
                        grok_api_key=st.session_state.grok_api_key
                    )
                    if not case_dict.get("id") or case_dict["id"] == "generated_case_id":
                        case_dict["id"] = f"case_{uuid.uuid4().hex[:8]}"
                    case_id = case_dict["id"]
                    
                    db.save_case(
                        case_id,
                        case_dict.get("title", "Mystery Case"),
                        case_dict.get("crime_type", crime_type),
                        case_dict.get("difficulty", difficulty),
                        case_dict.get("victim", {}).get("name", "Unknown"),
                        case_dict
                    )
                    sanitized_case = dict(case_dict)
                    sanitized_case.pop("ground_truth", None)
                    case_dict = sanitized_case
                except Exception as ex:
                    st.error(f"Direct generation error: {ex}")

            if not case_dict:
                # HTTP Fallback
                try:
                    res = requests.post(
                        f"{BACKEND_URL}/api/cases/generate",
                        json={
                            "difficulty": difficulty,
                            "crime_type": crime_type,
                            "api_key": st.session_state.api_key,
                            "grok_api_key": st.session_state.grok_api_key
                        },
                        timeout=40
                    )
                    if res.status_code == 200:
                        data = res.json()
                        case_id = data["case_id"]
                        case_dict = data["case"]
                except Exception as ex:
                    st.error(f"Backend Connection Error: {ex}")

            if case_dict and case_id:
                st.session_state.case_id = case_id
                st.session_state.case_data = case_dict
                st.session_state.collected_evidence = []
                st.session_state.visited_locations = []
                st.session_state.chat_history = {}
                st.session_state.verdict = None
                st.session_state.start_time = time.time()
                st.session_state.detective_notes = ""
                st.session_state.used_hints = 0
                st.session_state.suspect_suspicion = {s["id"]: s.get("suspicion_score", 35) for s in case_dict.get("suspects", [])}
                
                st.success(f"Case Generated: {case_dict['title']}")
                play_sound("clue")
                st.rerun()

    # Case Archives & Resumption in Sidebar
    st.markdown("---")
    st.markdown("#### 📂 Case Archives")
    with st.expander("Resume Existing Investigation", expanded=False):
        recent_cases = []
        if USE_DIRECT_SERVICES:
            try:
                recent_cases = db.get_recent_cases(limit=12)
            except Exception:
                pass
        if not recent_cases:
            try:
                cases_res = requests.get(f"{BACKEND_URL}/api/cases", timeout=4)
                if cases_res.status_code == 200:
                    recent_cases = cases_res.json().get("cases", [])
            except Exception:
                pass

        if recent_cases:
            case_options = {
                f"{c['case_id']} | {c.get('title', 'Mystery Case')} [{c.get('status', 'In Progress')}]": c['case_id']
                for c in recent_cases
            }
            selected_case_label = st.selectbox(
                "Select Case File",
                options=list(case_options.keys()),
                key="resume_case_selector"
            )
            selected_case_id = case_options[selected_case_label]
            if st.button("📂 Resume Selected Case", use_container_width=True):
                resume_case_session(selected_case_id)
        else:
            st.caption("No previous cases saved yet.")

        st.markdown("##### Quick ID Lookup")
        manual_case_id = st.text_input("Enter Case ID", placeholder="case_xxxx", key="manual_case_id_input")
        if st.button("🔍 Load by ID", use_container_width=True):
            if manual_case_id and manual_case_id.strip():
                resume_case_session(manual_case_id.strip())
            else:
                st.warning("Please enter a valid Case ID.")

    # Notebook Drawer in Sidebar
    if st.session_state.case_data:
        st.markdown("---")
        st.markdown("#### 📝 Detective Notepad")
        st.session_state.detective_notes = st.text_area(
            "Quick Case Notes",
            value=st.session_state.detective_notes,
            height=120,
            placeholder="Record your suspicions, alibi flaws, or clues here..."
        )

    # Leaderboard Preview
    st.markdown("---")
    st.markdown("### 🏆 Hall of Fame")
    lb_data = []
    if USE_DIRECT_SERVICES:
        try:
            lb_data = db.get_leaderboard(limit=3)
        except Exception:
            pass
    if not lb_data:
        try:
            lb_res = requests.get(f"{BACKEND_URL}/api/cases/leaderboard", timeout=3)
            if lb_res.status_code == 200:
                lb_data = lb_res.json().get("leaderboard", [])[:3]
        except Exception:
            pass

    if lb_data:
        for idx, entry in enumerate(lb_data):
            medal = "🥇" if idx == 0 else ("🥈" if idx == 1 else "🥉")
            st.caption(f"{medal} **{entry['player_name']}** — {entry['score']} pts ({entry['difficulty']})")
    else:
        st.caption("No high scores recorded yet.")

# MAIN CONTENT DISPLAY
if not st.session_state.case_data:
    # Cyber-Noir Hero Welcome Screen
    st.markdown(
        """
        <div class="hero-header">
            <div class="game-title">DetectAI – AI Crime Investigation Game</div>
            <div class="game-subtitle">SY B.Sc. AI & ML Hackathon Project | Combined Unified Architecture (Streamlit + FastAPI + SQLite)</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("### 🔍 Welcome, Detective!")
        st.markdown(
            """
            Step into the shoes of a lead investigator in **DetectAI**, an immersive detective simulation where every mystery is procedurally crafted by Generative AI.

            #### 🎮 Key Features:
            - **🤖 Infinite Procedural Mysteries**: No two crime cases are ever identical.
            - **📍 Interactive Scene Scanner**: Uncover physical clues, CCTV logs & phone records.
            - **🗣️ Dynamic AI Interrogation**: Suspects remember past questions and react with real-time stress & suspicion meters.
            - **⚖️ AI Judge Courtroom**: Submit your indictment to be judged on logical deduction, evidence strength, and thoroughness.
            - **🏆 Achievements & Leaderboard**: Earn detective ranks and top the global leaderboard.
            """
        )
    with col2:
        st.info("💡 **Ready to solve your first murder or heist?** Choose your difficulty level in the left sidebar and click **Generate AI Crime Case** to start!")
        st.markdown(
            """
            <div class="kpi-card" style="margin-top: 15px;">
                <div class="kpi-title">CURRENT ARCHITECTURE</div>
                <div class="kpi-value" style="font-size: 1.3rem;">UNIFIED SINGLE-PROCESS ENGINE</div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    case = st.session_state.case_data
    case_id = st.session_state.case_id
    total_locations = len(case.get("locations", []))
    total_evidence = len(case.get("evidence", []))
    total_suspects = len(case.get("suspects", []))
    
    scanned_loc_count = len(st.session_state.visited_locations)
    collected_ev_count = len(st.session_state.collected_evidence)
    interrogated_sus_count = len(st.session_state.chat_history)

    # 1. INVESTIGATION PROGRESS TRACKER & PROGRESS BAR
    progress_val = (
        (0.2 if case_id else 0) +
        (0.25 * (scanned_loc_count / max(1, total_locations))) +
        (0.25 * (collected_ev_count / max(1, total_evidence))) +
        (0.20 * (interrogated_sus_count / max(1, total_suspects))) +
        (0.10 if st.session_state.verdict else 0)
    )
    progress_val = min(1.0, progress_val)

    st.markdown(
        f"""
        <div class="hero-header" style="padding: 20px 28px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="game-title" style="font-size: 2.2rem; margin:0;">{case.get('title')}</div>
                    <div class="game-subtitle">Category: <b>{case.get('crime_type')}</b> | Difficulty: <b>{case.get('difficulty')}</b> | Case ID: <code>{case_id}</code></div>
                </div>
                <div>
                    <span class="badge-calm" style="font-size: 1rem; padding: 6px 16px;">
                        INVESTIGATION {int(progress_val * 100)}% COMPLETE
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top Stage Badges & Progress Bar
    b1 = "🟢 Case Briefed"
    b2 = "🟢 Locations Scanned" if scanned_loc_count == total_locations else f"🟡 Locations ({scanned_loc_count}/{total_locations})"
    b3 = "🟢 Evidence Gathered" if collected_ev_count == total_evidence else f"🟡 Evidence ({collected_ev_count}/{total_evidence})"
    b4 = "🟢 Suspects Pressed" if interrogated_sus_count == total_suspects else f"🟡 Interrogations ({interrogated_sus_count}/{total_suspects})"
    b5 = "🟢 Verdict Reached" if st.session_state.verdict else "⚪ Court Indictment"

    st.caption(f"{b1}  ➔  {b2}  ➔  {b3}  ➔  {b4}  ➔  {b5}")
    st.progress(progress_val)

    provider = case.get("provider", "offline")
    if provider == "gemini":
        st.success("🟢 **AI Provider: Google Gemini Active** — Dynamically generated case.")
    elif provider == "grok":
        st.info("🟣 **AI Provider: xAI Grok Active** — Secondary failover case.")
    elif case.get("is_fallback") or provider == "offline":
        st.warning("⚡ **Offline Demo Mode**: Running pre-engineered forensic mystery scenario without external AI keys. Add an API Key in the sidebar for procedurally-generated AI cases.")

    # 2. DETECTIVE DASHBOARD (4 KPI CARDS)
    if progress_val < 0.4:
        rank_name = "Novice Sleuth"
    elif progress_val < 0.8:
        rank_name = "Senior Investigator"
    else:
        rank_name = "Master Detective 🕵️‍♂️"

    elapsed_secs = int(time.time() - st.session_state.start_time) if st.session_state.start_time else 0
    mins, secs = divmod(elapsed_secs, 60)
    time_str = f"{mins:02d}:{secs:02d}"

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">🕵️ DETECTIVE RANK</div><div class="kpi-value">{rank_name}</div></div>', unsafe_allow_html=True)
    with col_kpi2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">📁 EVIDENCE DISCOVERED</div><div class="kpi-value">{collected_ev_count} / {total_evidence}</div></div>', unsafe_allow_html=True)
    with col_kpi3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">👥 SUSPECTS QUESTIONED</div><div class="kpi-value">{interrogated_sus_count} / {total_suspects}</div></div>', unsafe_allow_html=True)
    with col_kpi4:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">⏱️ TIME ELAPSED</div><div class="kpi-value">{time_str}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Main Navigation Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Case Briefing",
        "🔍 Crime Scene Map",
        "🗣️ Interrogate Suspects",
        "📁 Evidence Locker",
        "📝 Detective Notebook",
        "💡 AI Hint Desk",
        "⚖️ AI Judge & Courtroom"
    ])

    # TAB 1: CASE BRIEFING
    with tab1:
        st.markdown("### 🚔 Police Dispatch Briefing")
        st.write(case.get("summary"))

        st.markdown("---")
        col_v, col_s = st.columns(2)
        with col_v:
            st.markdown("#### 👤 Victim Profile")
            victim = case.get("victim", {})
            st.markdown(f"**Name:** {victim.get('name')}")
            st.markdown(f"**Occupation:** {victim.get('occupation')}")
            st.markdown(f"**Background:** {victim.get('background')}")

        with col_s:
            st.markdown("#### 👥 Key Persons of Interest")
            for s in case.get("suspects", []):
                st.markdown(f"- **{s.get('name')}** ({s.get('occupation')}) – *{s.get('relationship')}*")

    # TAB 2: CRIME SCENE EXPLORATION (INTERACTIVE MAP & IMAGES)
    with tab2:
        st.markdown("### 📍 Location Inspection & Interactive Map")
        st.caption("Click a location card to scan for physical clues, digital logs, and forensic evidence.")

        locations = case.get("locations", [])
        all_evidence = {e["id"]: e for e in case.get("evidence", [])}

        loc_cols = st.columns(len(locations)) if locations else []
        for idx, loc in enumerate(locations):
            with loc_cols[idx]:
                img_url = get_location_image(loc.get("image_type", "default"))
                is_visited = loc.get("id") in st.session_state.visited_locations
                
                st.markdown(
                    f"""
                    <div class="location-img-card">
                        <img src="{img_url}" style="width:100%; height:130px; object-fit:cover;"/>
                        <div style="padding: 12px;">
                            <div style="font-weight:700; color:#00f2fe; font-size:1.1rem;">{loc.get('name')}</div>
                            <div style="font-size:0.85rem; color:#94a3b8; margin: 4px 0 10px 0;">{(loc.get('description') or '')[:75]}...</div>
                            {'<span class="badge-calm">✅ AREA SCANNED</span>' if is_visited else '<span class="badge-defensive">🟡 UNEXPLORED</span>'}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"Scan {loc.get('name')}", key=f"btn_loc_{loc.get('id')}", use_container_width=True):
                    if loc.get("id") not in st.session_state.visited_locations:
                        st.session_state.visited_locations.append(loc.get("id"))
                    
                    new_clues = 0
                    for eid in loc.get("evidence_ids", []):
                        if eid in all_evidence and eid not in [e["id"] for e in st.session_state.collected_evidence]:
                            st.session_state.collected_evidence.append(all_evidence[eid])
                            new_clues += 1
                    
                    play_sound("clue")
                    st.toast(f"Scanned {loc.get('name')}! Found {new_clues} new clues.", icon="🔎")
                    
                    if len(st.session_state.collected_evidence) >= 1:
                        unlock_achievement("First Clue Found", "🔎")
                    if len(st.session_state.visited_locations) == len(locations):
                        unlock_achievement("Master Scene Inspector", "📍")
                        
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 🔍 Evidence Uncovered at Locations")
        if st.session_state.collected_evidence:
            for ev in st.session_state.collected_evidence:
                importance = ev.get("importance", "Medium")
                card_class = "evidence-critical" if importance == "Critical" else ("evidence-medium" if importance == "Medium" else "evidence-low")
                stars_str = "⭐" * ev.get("stars", 3)
                
                st.markdown(
                    f"""
                    <div class="evidence-card {card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <b style="color:#00f2fe; font-size:1.1rem;">{ev.get('name')}</b>
                            <span>{stars_str} <span class="badge-calm">{importance.upper()}</span></span>
                        </div>
                        <small style="color:#94a3b8;">Location: <i>{ev.get('location')}</i> | Category: <i>{ev.get('category')}</i></small><br/>
                        <p style="margin-top:8px; color:#cbd5e1;">{ev.get('description')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No evidence collected yet. Click 'Scan Location' buttons above to search for clues.")

    # TAB 3: SUSPECT INTERROGATION (PROFILE CARDS & LIVE SUSPICION METERS)
    with tab3:
        st.markdown("### 🗣️ AI Suspect Interrogation Room")
        st.caption("Question suspects under pressure. Present evidence to expose contradictions in their alibis!")

        suspects = case.get("suspects", [])
        suspect_options = {f"{s['name']} ({s['occupation']})": s["id"] for s in suspects}
        selected_label = st.selectbox("Select Suspect to Interrogate", list(suspect_options.keys()))
        selected_suspect_id = suspect_options[selected_label]
        selected_suspect = next(s for s in suspects if s["id"] == selected_suspect_id)

        col_bio, col_chat = st.columns([1, 2])

        with col_bio:
            st.markdown(
                f"""
                <div class="kpi-card" style="text-align:left; padding:18px;">
                    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                        <span style="font-size:2.5rem;">👤</span>
                        <div>
                            <h3 style="margin:0; color:#00f2fe;">{selected_suspect['name']}</h3>
                            <small style="color:#94a3b8;">{selected_suspect['occupation']}</small>
                        </div>
                    </div>
                    <p><b>Relationship:</b> {selected_suspect['relationship']}</p>
                    <p><b>Personality:</b> {selected_suspect['personality']}</p>
                    <p><b>Claimed Alibi:</b> {selected_suspect['alibi']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Fetch interrogation history directly or via HTTP
            if selected_suspect_id not in st.session_state.chat_history:
                h_list = []
                if USE_DIRECT_SERVICES:
                    try:
                        h_list = db.get_interrogation_logs(case_id, selected_suspect_id)
                    except Exception:
                        pass
                if not h_list:
                    try:
                        h_res = requests.get(f"{BACKEND_URL}/api/cases/{case_id}/interrogate/{selected_suspect_id}", timeout=3)
                        if h_res.status_code == 200:
                            h_list = h_res.json().get("history", [])
                    except Exception:
                        pass
                st.session_state.chat_history[selected_suspect_id] = h_list

            chat_logs = st.session_state.chat_history.get(selected_suspect_id, [])
            latest_stress = chat_logs[-1].get("stress_level", "Calm") if chat_logs else selected_suspect.get("stress_level", "Calm")
            stress_class = f"badge-{latest_stress.lower()}"
            
            st.markdown("#### Demeanor & Suspicion Meter")
            st.markdown(f"Current Stress: <span class='{stress_class}'>{latest_stress.upper()}</span>", unsafe_allow_html=True)
            
            current_suspicion = st.session_state.suspect_suspicion.get(selected_suspect_id, 35)
            st.write(f"**Suspicion Score:** {current_suspicion}%")
            st.progress(current_suspicion / 100.0)

            st.markdown("---")
            st.markdown("#### 📊 Suspect Suspicion Overview")
            for s in suspects:
                s_score = st.session_state.suspect_suspicion.get(s["id"], 35)
                st.caption(f"{s['name']}: {s_score}%")
                st.progress(s_score / 100.0)

        with col_chat:
            st.markdown("#### 💬 Interrogation Transcript")
            
            chat_container = st.container(height=340)
            with chat_container:
                if not chat_logs:
                    st.caption("No questions asked yet. Type a question below or present evidence.")
                for msg in chat_logs:
                    if msg.get("role") == "player":
                        st.chat_message("user").write(msg.get("content"))
                    else:
                        st.chat_message("assistant").write(msg.get("content"))

            # Evidence dropdown to present
            ev_options = {"None (General Question)": None}
            for e in st.session_state.collected_evidence:
                ev_options[f"Present: {e['name']} ({e['category']})"] = e["id"]
            
            selected_ev_label = st.selectbox("Confront with Evidence (Optional)", list(ev_options.keys()))
            selected_ev_id = ev_options[selected_ev_label]

            question_input = st.text_input("Ask a question...", placeholder="Where were you between 9 PM and 10 PM?")
            
            if st.button("Send Question", type="primary", use_container_width=True):
                if question_input.strip():
                    with st.spinner(f"Interrogating {selected_suspect['name']}..."):
                        res_data = None
                        if USE_DIRECT_SERVICES:
                            try:
                                evidence_presented = None
                                if selected_ev_id:
                                    evidence_presented = next((e for e in st.session_state.collected_evidence if e["id"] == selected_ev_id), None)
                                
                                q_text = question_input.strip()
                                if evidence_presented:
                                    q_text += f" (Confronting with evidence: {evidence_presented.get('name')})"
                                
                                db.save_interrogation_log(case_id, selected_suspect_id, "player", q_text)
                                history = db.get_interrogation_logs(case_id, selected_suspect_id)
                                
                                ai_res = gemini_service.interrogate_suspect(
                                    case_data=st.session_state.case_data,
                                    suspect_id=selected_suspect_id,
                                    history=history,
                                    question=question_input.strip(),
                                    evidence_presented=evidence_presented,
                                    api_key=st.session_state.api_key,
                                    grok_api_key=st.session_state.grok_api_key
                                )
                                
                                db.save_interrogation_log(
                                    case_id,
                                    selected_suspect_id,
                                    "suspect",
                                    ai_res.get("response", ""),
                                    stress_level=ai_res.get("stress_level", "Calm")
                                )
                                
                                res_data = {
                                    "response": ai_res.get("response"),
                                    "stress_level": ai_res.get("stress_level"),
                                    "suspicion_change": ai_res.get("suspicion_change", 5),
                                    "history": db.get_interrogation_logs(case_id, selected_suspect_id)
                                }
                            except Exception as ex:
                                st.error(f"Direct Interrogation Error: {ex}")

                        if not res_data:
                            # HTTP Fallback
                            try:
                                payload = {
                                    "suspect_id": selected_suspect_id,
                                    "question": question_input.strip(),
                                    "evidence_id": selected_ev_id,
                                    "api_key": st.session_state.api_key,
                                    "grok_api_key": st.session_state.grok_api_key
                                }
                                res = requests.post(f"{BACKEND_URL}/api/cases/{case_id}/interrogate", json=payload, timeout=25)
                                if res.status_code == 200:
                                    res_data = res.json()
                            except Exception as ex:
                                st.error(f"Interrogation connection error: {ex}")

                        if res_data:
                            st.session_state.chat_history[selected_suspect_id] = res_data.get("history", [])
                            change = res_data.get("suspicion_change", 5)
                            st.session_state.suspect_suspicion[selected_suspect_id] = min(100, max(0, current_suspicion + change))
                            
                            play_sound("interrogate")
                            if selected_ev_id:
                                unlock_achievement("Master Interrogator", "🗣️")
                            st.rerun()

    # TAB 4: EVIDENCE LOCKER
    with tab4:
        st.markdown("### 📁 Evidence Notebook & Case Board")
        st.caption("All physical and digital evidence gathered across crime scenes.")

        if st.session_state.collected_evidence:
            for ev in st.session_state.collected_evidence:
                importance = ev.get("importance", "Medium")
                card_class = "evidence-critical" if importance == "Critical" else ("evidence-medium" if importance == "Medium" else "evidence-low")
                stars_str = "⭐" * ev.get("stars", 3)

                st.markdown(
                    f"""
                    <div class="evidence-card {card_class}">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0; color:#00f2fe;">{ev.get('name')}</h4>
                            <div>{stars_str} <span class="badge-calm">{importance.upper()}</span></div>
                        </div>
                        <p style="margin-top:6px; color:#cbd5e1;"><b>Location:</b> {ev.get('location')} | <b>Category:</b> {ev.get('category')}</p>
                        <p style="color:#94a3b8;">{ev.get('description')}</p>
                        <small style="color:#00f2fe;">Relevance: {ev.get('relevance')}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.warning("No evidence has been collected yet! Go to the 'Crime Scene' tab to explore locations.")

    # TAB 5: DETECTIVE NOTEBOOK
    with tab5:
        st.markdown("### 📝 Detective Notebook & Case Theories")
        st.caption("Organize your thoughts, record motive hypotheses, and track suspect alibis.")

        notes_input = st.text_area(
            "Investigation Notes",
            value=st.session_state.detective_notes,
            height=250,
            placeholder="Type your investigation notes here..."
        )
        st.session_state.detective_notes = notes_input

        st.download_button(
            label="📥 Export Notes to Text File",
            data=st.session_state.detective_notes,
            file_name=f"Detective_Notes_{case_id}.txt",
            mime="text/plain"
        )

    # TAB 6: AI HINT SYSTEM
    with tab6:
        st.markdown("### 💡 AI Detective Hint Desk")
        st.caption("Need guidance? Request progressive hints generated by AI.")

        col_h1, col_h2, col_h3 = st.columns(3)

        def get_hint(hint_lvl):
            st.session_state.used_hints += 1
            hint_txt = None
            if USE_DIRECT_SERVICES:
                try:
                    hint_txt = gemini_service.generate_ai_hint(
                        st.session_state.case_data,
                        hint_level=hint_lvl,
                        api_key=st.session_state.api_key,
                        grok_api_key=st.session_state.grok_api_key
                    )
                except Exception:
                    pass
            if not hint_txt:
                try:
                    h_res = requests.post(
                        f"{BACKEND_URL}/api/cases/{case_id}/hint",
                        json={
                            "hint_level": hint_lvl,
                            "api_key": st.session_state.api_key,
                            "grok_api_key": st.session_state.grok_api_key
                        },
                        timeout=15
                    )
                    if h_res.status_code == 200:
                        hint_txt = h_res.json().get("hint")
                except Exception:
                    pass
            return hint_txt or "Check suspect alibis against physical evidence collected at crime scene locations."

        with col_h1:
            st.markdown("#### 🟢 First Hint")
            st.caption("Subtle direction nudge")
            if st.button("Unlock Hint 1", use_container_width=True):
                with st.spinner("Analyzing case data..."):
                    st.info(get_hint(1))

        with col_h2:
            st.markdown("#### 🟡 Second Hint")
            st.caption("Alibi & timeline conflict")
            if st.button("Unlock Hint 2", use_container_width=True):
                with st.spinner("Cross-referencing suspect statements..."):
                    st.warning(get_hint(2))

        with col_h3:
            st.markdown("#### 🔴 Smoking Gun Hint")
            st.caption("Direct evidence correlation")
            if st.button("Unlock Hint 3", use_container_width=True):
                with st.spinner("Evaluating smoking gun clue..."):
                    st.error(get_hint(3))

    # TAB 7: AI JUDGE & COURTROOM
    with tab7:
        st.markdown("### ⚖️ AI Judge & Courtroom Indictment")
        st.caption("Submit your official indictment. The AI Judge will score your detective work (0–100) and break down your reasoning.")

        if st.session_state.verdict:
            v = st.session_state.verdict
            is_correct = v.get("is_correct", False)
            score = v.get("score", 0)

            play_sound("victory" if is_correct else "error")

            st.markdown("---")
            col_score, col_verdict = st.columns([1, 2])

            with col_score:
                st.markdown(
                    f"""
                    <div class="score-circle">
                        <div class="score-number">{score}</div>
                        <div style="color:#94a3b8; font-size:0.85rem;">DETECTIVE SCORE</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if is_correct:
                    st.success("🏆 ACCUSED GUILTY! MASTER DETECTIVE")
                    if score >= 90:
                        unlock_achievement("Master Sleuth", "⚖️")
                else:
                    st.error("❌ CASE DISMISSED / WRONG ACCUSATION")

                if st.session_state.used_hints == 0:
                    unlock_achievement("No Hint Challenge", "🌟")

            with col_verdict:
                st.markdown("#### ⚖️ AI Judge's Score Breakdown")
                
                ev_str_score = v.get("evidence_strength", 80)
                logic_score = v.get("logic_score", 85)
                thorough_score = v.get("thoroughness_score", 90)

                st.write(f"**Evidence Strength:** {ev_str_score}%")
                st.progress(ev_str_score / 100.0)

                st.write(f"**Logical Deduction:** {logic_score}%")
                st.progress(logic_score / 100.0)

                st.write(f"**Investigation Thoroughness:** {thorough_score}%")
                st.progress(thorough_score / 100.0)

                st.markdown("#### ⚖️ Judge Explanation")
                st.write(v.get("judge_explanation"))

            st.markdown("---")
            col_sup, col_ign = st.columns(2)
            with col_sup:
                st.markdown("#### 🟢 Supporting Evidence Cited")
                for sup in v.get("supported_clues", []):
                    st.markdown(f"- ✅ {sup}")
            with col_ign:
                st.markdown("#### 🔴 Missed / Ignored Clues")
                for ig in v.get("ignored_clues", []):
                    st.markdown(f"- ⚠️ {ig}")

            st.markdown("---")
            st.markdown("### 🕵️ Ground Truth Revelation (Post-Trial Summary)")
            gt = v.get("ground_truth", {})
            if gt:
                st.info(
                    f"**Actual Criminal:** {gt.get('criminal_name')}\n\n"
                    f"**True Motive:** {gt.get('motive')}\n\n"
                    f"**How Crime Was Executed:** {gt.get('how_it_was_done')}"
                )

            report_text = f"""==================================================
DETECTAI OFFICIAL CASE INVESTIGATION REPORT
==================================================
Case ID: {case_id}
Title: {case.get('title')}
Category: {case.get('crime_type')}
Difficulty: {case.get('difficulty')}
Lead Detective: {st.session_state.player_name}
Final Score: {score} / 100
Verdict Status: {"GUILTY / CONVICTED" if is_correct else "CASE DISMISSED"}

COURT VERDICT EXPLANATION:
{v.get('judge_explanation')}

GROUND TRUTH REVELATION:
- Criminal: {gt.get('criminal_name')}
- Motive: {gt.get('motive')}
- Execution: {gt.get('how_it_was_done')}

DETECTIVE NOTES:
{st.session_state.detective_notes}
==================================================
"""
            st.download_button(
                label="📄 Download Official Case Report (TXT)",
                data=report_text,
                file_name=f"Case_Report_{case_id}.txt",
                mime="text/plain",
                use_container_width=True
            )

            if st.button("🎮 Start New Investigation Case", type="primary", use_container_width=True):
                st.session_state.case_data = None
                st.session_state.case_id = None
                st.session_state.verdict = None
                st.rerun()

        else:
            suspects = case.get("suspects", [])
            s_dict = {f"{s['name']} ({s['occupation']})": s["id"] for s in suspects}
            accused_label = st.selectbox("Accuse Primary Suspect", list(s_dict.keys()))
            accused_id = s_dict[accused_label]

            motive_input = st.text_area(
                "Explain the Motive & How the Crime Was Committed",
                placeholder="Arthur stole the ruby using his master keycard because he was deep in debt to gambling syndicates..."
            )

            st.markdown("#### Select Evidence to Support Your Indictment")
            selected_evidence_ids = []
            if st.session_state.collected_evidence:
                for ev in st.session_state.collected_evidence:
                    if st.checkbox(f"{ev['name']} ({ev['category']} - {ev['location']})", key=f"judge_ev_{ev['id']}"):
                        selected_evidence_ids.append(ev['id'])
            else:
                st.warning("You haven't collected any evidence yet. Explore crime scenes first!")

            if st.button("⚖️ Submit Official Indictment to AI Judge", type="primary", use_container_width=True):
                if not motive_input.strip():
                    st.error("Please explain your motive theory before submitting.")
                else:
                    with st.spinner("AI Judge is reviewing your case evidence and evaluating score..."):
                        verdict = None
                        if USE_DIRECT_SERVICES:
                            try:
                                verdict = gemini_service.evaluate_accusation(
                                    case_data=st.session_state.case_data,
                                    accused_suspect_id=accused_id,
                                    motive_provided=motive_input.strip(),
                                    evidence_ids=selected_evidence_ids,
                                    api_key=st.session_state.api_key,
                                    hints_used=st.session_state.used_hints
                                )
                                db.save_verdict(
                                    case_id=case_id,
                                    player_name=st.session_state.player_name,
                                    accused_suspect_id=accused_id,
                                    motive_provided=motive_input.strip(),
                                    is_correct=verdict.get("is_correct", False),
                                    score=verdict.get("score", 50),
                                    explanation=verdict.get("judge_explanation", ""),
                                    supported=verdict.get("supported_clues", []),
                                    ignored=verdict.get("ignored_clues", []),
                                    difficulty=st.session_state.case_data.get("difficulty", "Medium")
                                )
                                verdict["ground_truth"] = st.session_state.case_data.get("ground_truth")
                            except Exception as ex:
                                st.error(f"Direct verdict evaluation error: {ex}")

                        if not verdict:
                            try:
                                payload = {
                                    "accused_suspect_id": accused_id,
                                    "motive_provided": motive_input.strip(),
                                    "evidence_ids": selected_evidence_ids,
                                    "player_name": st.session_state.player_name,
                                    "api_key": st.session_state.api_key,
                                    "grok_api_key": st.session_state.grok_api_key,
                                    "hints_used": st.session_state.used_hints
                                }
                                j_res = requests.post(f"{BACKEND_URL}/api/cases/{case_id}/judge", json=payload, timeout=25)
                                if j_res.status_code == 200:
                                    verdict = j_res.json().get("verdict")
                            except Exception as ex:
                                st.error(f"Courtroom connection error: {ex}")

                        if verdict:
                            st.session_state.verdict = verdict
                            st.rerun()

    # Display Trophy Cabinet in Footer / Drawer if achievements exist
    if st.session_state.achievements:
        st.markdown("---")
        st.markdown("#### 🏆 Unlocked Trophies Cabinet")
        ach_cols = st.columns(len(st.session_state.achievements))
        for idx, ach in enumerate(st.session_state.achievements):
            with ach_cols[idx]:
                st.markdown(
                    f"""
                    <div class="achievement-badge">
                        <span>🏆</span>
                        <b style="color:#ffd700; font-size:0.85rem;">{ach}</b>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
