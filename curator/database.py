import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

DB = "profiles.db"

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    
    # Profiles table (replaces accounts)
    cursor.execute('CREATE TABLE IF NOT EXISTS profiles (name TEXT PRIMARY KEY, profile TEXT)')
    
    # Logs table (shared)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            datetime DATETIME,
            type TEXT,
            message TEXT
        )
    ''')
    
    # Trends table (replaces market)
    cursor.execute('CREATE TABLE IF NOT EXISTS trends (date TEXT PRIMARY KEY, data TEXT)')
    
    conn.commit()


# ---- Profiles ----
def write_profile(name: str, profile_dict: dict) -> None:
    """Insert or update a profile record."""
    json_data = json.dumps(profile_dict)
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (name, profile)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET profile=excluded.profile
        ''', (name.lower(), json_data))
        conn.commit()

def read_profile(name: str) -> dict | None:
    """Read a profile record by name."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile FROM profiles WHERE name = ?', (name.lower(),))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None


# ---- Logs ----
def write_log(name: str, type: str, message: str) -> None:
    """Write a log entry."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO logs (name, datetime, type, message)
            VALUES (?, datetime('now'), ?, ?)
        ''', (name.lower(), type, message))
        conn.commit()

def read_log(name: str, last_n=10):
    """Read the most recent log entries for a given profile."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT datetime, type, message FROM logs 
            WHERE name = ? 
            ORDER BY datetime DESC
            LIMIT ?
        ''', (name.lower(), last_n))
        return reversed(cursor.fetchall())


# ---- Trends ----
def write_trends(date: str, data: dict) -> None:
    """Insert or update trend data for a specific date."""
    data_json = json.dumps({k: v.to_dict() if hasattr(v, "to_dict") else v for k, v in data.items()})
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO trends (date, data)
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET data=excluded.data
        ''', (date, data_json))
        conn.commit()

def read_trends(date: str) -> dict | None:
    """Read stored trend data for a specific date."""
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM trends WHERE date = ?', (date,))
        row = cursor.fetchone()
        return json.loads(row[0]) if row else None
