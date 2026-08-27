import os
import sqlite3
import json
from typing import Dict, Any, Optional, List

DB_PATH = os.path.join(os.path.dirname(__file__), "detectai.db")

def init_db():
    """Initialize SQLite database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table for storing generated crime cases
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            crime_type TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            victim_name TEXT NOT NULL,
            case_data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table for storing suspect interrogation message logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interrogation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            suspect_id TEXT NOT NULL,
            role TEXT NOT NULL, -- 'player' or 'suspect'
            content TEXT NOT NULL,
            stress_level TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    # Table for storing final accusation results & Leaderboard
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS judge_verdicts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            player_name TEXT DEFAULT 'Detective',
            accused_suspect_id TEXT NOT NULL,
            motive_provided TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            score INTEGER NOT NULL,
            judge_explanation TEXT NOT NULL,
            supported_clues JSON,
            ignored_clues JSON,
            difficulty TEXT DEFAULT 'Medium',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (case_id) REFERENCES cases(id)
        )
    """)
    
    # --- Migration guard ---
    # The database file shipped/created by earlier versions of this app may
    # predate columns the current code relies on (e.g. an old detectai.db
    # with a judge_verdicts table that has no player_name/difficulty
    # columns). CREATE TABLE IF NOT EXISTS above is a no-op on an existing
    # table, so without this check every /judge and /leaderboard call fails
    # with "sqlite3.OperationalError: table judge_verdicts has no column
    # named player_name". Patch any missing columns onto existing tables.
    cursor.execute("PRAGMA table_info(judge_verdicts)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    if "player_name" not in existing_cols:
        cursor.execute("ALTER TABLE judge_verdicts ADD COLUMN player_name TEXT DEFAULT 'Detective'")
    if "difficulty" not in existing_cols:
        cursor.execute("ALTER TABLE judge_verdicts ADD COLUMN difficulty TEXT DEFAULT 'Medium'")

    conn.commit()
    conn.close()

def save_case(case_id: str, title: str, crime_type: str, difficulty: str, victim_name: str, case_data: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO cases (id, title, crime_type, difficulty, victim_name, case_data) VALUES (?, ?, ?, ?, ?, ?)",
        (case_id, title, crime_type, difficulty, victim_name, json.dumps(case_data))
    )
    conn.commit()
    conn.close()

def get_case(case_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT case_data FROM cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def save_interrogation_log(case_id: str, suspect_id: str, role: str, content: str, stress_level: Optional[str] = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interrogation_logs (case_id, suspect_id, role, content, stress_level) VALUES (?, ?, ?, ?, ?)",
        (case_id, suspect_id, role, content, stress_level)
    )
    conn.commit()
    conn.close()

def get_interrogation_logs(case_id: str, suspect_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, stress_level, timestamp FROM interrogation_logs WHERE case_id = ? AND suspect_id = ? ORDER BY id ASC",
        (case_id, suspect_id)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1], "stress_level": r[2], "timestamp": r[3]} for r in rows]

def save_verdict(case_id: str, player_name: str = 'Detective', accused_suspect_id: str = '', motive_provided: str = '', is_correct: bool = False, score: int = 50, explanation: str = '', supported: list = None, ignored: list = None, difficulty: str = 'Medium'):
    if supported is None: supported = []
    if ignored is None: ignored = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO judge_verdicts 
           (case_id, player_name, accused_suspect_id, motive_provided, is_correct, score, judge_explanation, supported_clues, ignored_clues, difficulty)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (case_id, player_name, accused_suspect_id, motive_provided, is_correct, score, explanation, json.dumps(supported), json.dumps(ignored), difficulty)
    )
    conn.commit()
    conn.close()

def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT player_name, score, is_correct, difficulty, timestamp 
           FROM judge_verdicts ORDER BY score DESC, timestamp DESC LIMIT ?""",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {"player_name": r[0], "score": r[1], "is_correct": bool(r[2]), "difficulty": r[3], "timestamp": r[4]}
        for r in rows
    ]
