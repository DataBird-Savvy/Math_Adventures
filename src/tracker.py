import sqlite3
from datetime import datetime
import pandas as pd

def init_db():
    conn = sqlite3.connect("progress.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT,
            difficulty TEXT,
            correct INTEGER,
            response_time REAL,
            streak INTEGER
        )
    """)
    conn.commit()
    conn.close()


def log_progress(session_id, difficulty, correct, response_time, streak):
    conn = sqlite3.connect("progress.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO progress (session_id, timestamp, difficulty, correct, response_time, streak)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), difficulty, int(correct), response_time, streak))
    conn.commit()
    conn.close()


def get_progress(session_id):
    conn = sqlite3.connect("progress.db")
    df = pd.read_sql_query(f"SELECT * FROM progress WHERE session_id='{session_id}'", conn)
    conn.close()
    return df
