"""SQLite database setup for DetectAI"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.environ.get("DETECTAI_TEST_DB", "detectai.db")

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
        """, (case_id, case_title, crime_type, difficulty, victim_name, case_data_json, datetime.now().isoformat()))
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
    SELECT role, content, stress_level, timestamp FROM interrogation_logs 
    WHERE case_id = ? AND suspect_id = ?
    ORDER BY id ASC
    """, (case_id, suspect_id))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            "role": row[0],
            "content": row[1],
            "message": row[1],
            "stress_level": row[2],
            "timestamp": row[3] if len(row) > 3 else None
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
    try:
        cursor.execute("""
        SELECT l.player_name, l.score, l.difficulty, l.case_id, c.case_title, v.is_correct, l.created_at
        FROM leaderboard l
        LEFT JOIN cases c ON l.case_id = c.case_id
        LEFT JOIN verdicts v ON l.case_id = v.case_id AND l.player_name = v.player_name
        ORDER BY l.score DESC, l.id DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        leaderboard = []
        for row in rows:
            leaderboard.append({
                "player_name": row[0],
                "score": row[1],
                "difficulty": row[2],
                "case_id": row[3],
                "case_title": row[4] or row[3] or "Mystery Case",
                "is_correct": bool(row[5]) if row[5] is not None else True,
                "timestamp": str(row[6]) if row[6] is not None else datetime.now().isoformat()
            })
        if leaderboard:
            return leaderboard
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("""
        SELECT jv.player_name, jv.score, jv.is_correct, jv.difficulty, jv.timestamp, jv.case_id, c.title 
        FROM judge_verdicts jv
        LEFT JOIN cases c ON jv.case_id = c.id
        ORDER BY jv.score DESC, jv.timestamp DESC, jv.id DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            {
                "player_name": r[0],
                "score": r[1],
                "is_correct": bool(r[2]),
                "difficulty": r[3],
                "timestamp": r[4],
                "case_id": r[5],
                "case_title": r[6] or r[5] or "Mystery Case"
            }
            for r in rows
        ]
    except Exception:
        return []
    finally:
        conn.close()

def get_recent_cases(limit=15):
    """Get list of recently generated/active/completed cases with status"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT 
            c.case_id, 
            c.case_title, 
            c.crime_type, 
            c.difficulty, 
            c.victim_name, 
            c.created_at,
            c.updated_at,
            v.is_correct,
            v.score,
            COUNT(i.id) as log_count
        FROM cases c
        LEFT JOIN verdicts v ON c.case_id = v.case_id
        LEFT JOIN interrogation_logs i ON c.case_id = i.case_id
        GROUP BY c.case_id
        ORDER BY c.id DESC
        LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        cases_list = []
        for r in rows:
            has_verdict = r[7] is not None
            is_correct = bool(r[7]) if has_verdict else None
            score = r[8] if has_verdict else None
            
            if has_verdict:
                status = "Solved" if is_correct else "Failed"
            else:
                status = "In Progress"
                
            cases_list.append({
                "case_id": r[0],
                "title": r[1] or "Mystery Case",
                "crime_type": r[2] or "Unknown",
                "difficulty": r[3] or "Medium",
                "victim_name": r[4] or "Unknown",
                "created_at": str(r[5]) if r[5] else datetime.now().isoformat(),
                "updated_at": str(r[6]) if r[6] else None,
                "is_completed": has_verdict,
                "is_correct": is_correct,
                "score": score,
                "status": status,
                "log_count": r[9] or 0
            })
        return cases_list
    except sqlite3.OperationalError:
        # Fallback for alternative or minimal schemas
        try:
            cursor.execute("SELECT case_id, case_title, crime_type, difficulty, victim_name, created_at FROM cases ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "case_id": r[0],
                    "title": r[1] or "Mystery Case",
                    "crime_type": r[2] or "Unknown",
                    "difficulty": r[3] or "Medium",
                    "victim_name": r[4] or "Unknown",
                    "created_at": str(r[5]) if r[5] else datetime.now().isoformat(),
                    "is_completed": False,
                    "status": "In Progress",
                    "log_count": 0
                }
                for r in rows
            ]
        except Exception:
            return []
    except Exception as e:
        print(f"Error fetching recent cases: {e}")
        return []
    finally:
        conn.close()

def get_case_verdict(case_id):
    """Retrieve verdict for a specific case if one exists"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT 
            player_name, accused_suspect_id, motive_provided, is_correct, score, 
            explanation, supported_clues, ignored_clues, difficulty, created_at
        FROM verdicts
        WHERE case_id = ?
        ORDER BY id DESC
        LIMIT 1
        """, (case_id,))
        row = cursor.fetchone()
        if not row:
            return None
            
        supported = row[6]
        try:
            supported = json.loads(supported) if isinstance(supported, str) else supported
        except Exception:
            pass
            
        ignored = row[7]
        try:
            ignored = json.loads(ignored) if isinstance(ignored, str) else ignored
        except Exception:
            pass
            
        # Retrieve ground truth from case_data for completed verdict review
        gt = None
        cursor.execute("SELECT case_data FROM cases WHERE case_id = ?", (case_id,))
        c_row = cursor.fetchone()
        if c_row:
            try:
                c_data = json.loads(c_row[0]) if isinstance(c_row[0], str) else c_row[0]
                gt = c_data.get("ground_truth")
            except Exception:
                pass

        return {
            "case_id": case_id,
            "player_name": row[0],
            "accused_suspect_id": row[1],
            "motive_provided": row[2],
            "is_correct": bool(row[3]),
            "score": row[4],
            "explanation": row[5],
            "judge_explanation": row[5],
            "supported_clues": supported or [],
            "ignored_clues": ignored or [],
            "difficulty": row[8],
            "created_at": str(row[9]),
            "ground_truth": gt
        }
    except Exception as e:
        print(f"Error getting case verdict: {e}")
        return None
    finally:
        conn.close()

def get_all_interrogation_logs_for_case(case_id):
    """Retrieve all interrogation logs for a case grouped by suspect_id"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT suspect_id, role, content, stress_level, timestamp
        FROM interrogation_logs
        WHERE case_id = ?
        ORDER BY id ASC
        """, (case_id,))
        rows = cursor.fetchall()
        
        grouped_logs = {}
        for row in rows:
            suspect_id = row[0]
            if suspect_id not in grouped_logs:
                grouped_logs[suspect_id] = []
            grouped_logs[suspect_id].append({
                "role": row[1],
                "content": row[2],
                "message": row[2],
                "stress_level": row[3],
                "timestamp": str(row[4]) if row[4] else None
            })
        return grouped_logs
    except Exception as e:
        print(f"Error getting all interrogation logs: {e}")
        return {}
    finally:
        conn.close()
