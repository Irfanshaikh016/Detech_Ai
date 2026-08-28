"""SQLite database setup for DetectAI"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "detectai.db"

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cases table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE NOT NULL,
        case_title TEXT,
        crime_type TEXT,
        difficulty TEXT,
        victim_name TEXT,
        case_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Interrogation logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interrogation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        suspect_id TEXT NOT NULL,
        role TEXT,
        content TEXT,
        stress_level TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    )
    """)
    
    # Verdicts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verdicts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        player_name TEXT,
        accused_suspect_id TEXT,
        motive_provided TEXT,
        is_correct BOOLEAN,
        score INTEGER,
        explanation TEXT,
        supported_clues TEXT,
        ignored_clues TEXT,
        difficulty TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
    )
    """)
    
    # Leaderboard table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_name TEXT,
        score INTEGER,
        difficulty TEXT,
        case_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def save_case(case_id, case_title, crime_type, difficulty, victim_name, case_data):
    """Save a generated case to database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        case_data_json = json.dumps(case_data) if isinstance(case_data, dict) else case_data
        cursor.execute("""
        INSERT OR REPLACE INTO cases (case_id, case_title, crime_type, difficulty, victim_name, case_data, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (case_id, case_title, crime_type, difficulty, victim_name, case_data_json, datetime.now()))
        conn.commit()
    except Exception as e:
        print(f"Error saving case: {e}")
    finally:
        conn.close()

def get_case(case_id):
    """Retrieve a case from database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT case_data FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        try:
            return json.loads(row[0])
        except:
            return row[0]
    return None

def save_interrogation_log(case_id, suspect_id, role, content, stress_level=None):
    """Save interrogation interaction"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO interrogation_logs (case_id, suspect_id, role, content, stress_level)
        VALUES (?, ?, ?, ?, ?)
        """, (case_id, suspect_id, role, content, stress_level))
        conn.commit()
    except Exception as e:
        print(f"Error saving interrogation log: {e}")
    finally:
        conn.close()

def get_interrogation_logs(case_id, suspect_id):
    """Retrieve interrogation history"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT role, content, stress_level FROM interrogation_logs 
    WHERE case_id = ? AND suspect_id = ?
    ORDER BY timestamp ASC
    """, (case_id, suspect_id))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "role": row[0],
            "content": row[1],
            "stress_level": row[2]
        })
    return history

def save_verdict(case_id, player_name, accused_suspect_id, motive_provided, is_correct, score, explanation, supported, ignored, difficulty):
    """Save case verdict"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        supported_json = json.dumps(supported) if isinstance(supported, list) else supported
        ignored_json = json.dumps(ignored) if isinstance(ignored, list) else ignored
        cursor.execute("""
        INSERT INTO verdicts (case_id, player_name, accused_suspect_id, motive_provided, is_correct, score, explanation, supported_clues, ignored_clues, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, player_name, accused_suspect_id, motive_provided, is_correct, score, explanation, supported_json, ignored_json, difficulty))
        
        # Add to leaderboard if score is recorded
        if score > 0:
            cursor.execute("""
            INSERT INTO leaderboard (player_name, score, difficulty, case_id)
            VALUES (?, ?, ?, ?)
            """, (player_name, score, difficulty, case_id))
        
        conn.commit()
    except Exception as e:
        print(f"Error saving verdict: {e}")
    finally:
        conn.close()

def get_leaderboard(limit=10):
    """Get top scores from leaderboard"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT player_name, score, difficulty FROM leaderboard 
    ORDER BY score DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for row in rows:
        leaderboard.append({
            "player_name": row[0],
            "score": row[1],
            "difficulty": row[2]
        })
    return leaderboard
