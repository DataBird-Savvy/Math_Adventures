import sqlite3
from datetime import datetime
import pandas as pd
from logger import logger



class ProgressTracker:
    def __init__(self, db_name: str = "progress.db"):
        self.db_name = db_name
        self._init_db()
        logger.info(f"✅ Database initialized: {db_name}")

    def _connect(self):
        """Internal method to connect to SQLite database."""
        return sqlite3.connect(self.db_name)

    def _init_db(self):
        """Create the progress table if it doesn’t exist."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                difficulty TEXT,
                correct INTEGER,
                response_time REAL,
                streak INTEGER,
                confidence REAL
            )
        """)
        conn.commit()
        conn.close()

    def log_progress(self, session_id: str, difficulty: str, correct: bool,
                     response_time: float, streak: int, confidence: float):
        """Insert a new progress record."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO progress (session_id, timestamp, difficulty, correct, response_time, streak, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            difficulty,
            int(correct),
            response_time,
            streak,
            confidence
        ))
        conn.commit()
        conn.close()
        logger.info(f"🧩 Logged progress → {session_id} | {difficulty} | Correct: {correct} | "
                    f"Time: {response_time:.2f}s | Streak: {streak} | Confidence: {confidence}")

    def get_progress(self, session_id: str) -> pd.DataFrame:
        """Retrieve all progress records for a given session."""
        conn = self._connect()
        df = pd.read_sql_query(
            f"SELECT * FROM progress WHERE session_id='{session_id}'", conn
        )
        conn.close()
        logger.info(f"📊 Retrieved {len(df)} progress entries for session: {session_id}")
        return df

    @staticmethod
    def calculate_confidence(correct: bool, difficulty: str, response_time: float,
                             streak: int, expected_time: float) -> float:
        """
        Calculate learner confidence score (0-100).
        """
        confidence = 50


        confidence += 20 * (2 * int(correct) - 1)

        confidence += 2 * min(streak, 20)


        time_effect = 2 * (expected_time - response_time)
        time_effect = max(-15, min(15, time_effect))
        confidence += time_effect

        difficulty_score = {"Easy": 1, "Medium": 2, "Hard": 3}.get(difficulty, 1)
        confidence += 3 * difficulty_score * int(correct)

      
        confidence = max(0, min(100, confidence))

        final_score = round(confidence, 2)
        logger.info(f"💡 Confidence calculated: {final_score} ({difficulty}, streak={streak}, "
                    f"response={response_time:.2f}s)")
        return final_score
