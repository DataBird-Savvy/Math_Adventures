import sqlite3
from datetime import datetime
import pandas as pd
from logger import logger
from exception import MathsException

class ProgressTracker:
    def __init__(self, db_name: str = "progress.db"):
        self.db_name = db_name
        try:
            self._init_db()
            logger.info(f"✅ Database initialized: {db_name}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise MathsException("Database initialization failed") from e

    def _connect(self):
        """Internal method to connect to SQLite database."""
        try:
            return sqlite3.connect(self.db_name)
        except Exception as e:
            logger.error(f"❌ DB connection failed: {e}")
            raise MathsException("Failed to connect to database") from e

    def _init_db(self):
        """Create the progress table if it doesn’t exist."""
        conn = None
        try:
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
        except Exception as e:
            logger.error(f"❌ Error creating database table: {e}")
            raise MathsException("Failed to initialize tables") from e
        finally:
            if conn:
                conn.close()

    def log_progress(self, session_id: str, difficulty: str, correct: bool,
                     response_time: float, streak: int, confidence: float):
        """Insert a new progress record with error handling."""
        conn = None
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO progress (
                    session_id, timestamp, difficulty, correct, response_time, streak, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
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
            logger.info(
                f"🧩 Logged progress → {session_id} | {difficulty} | Correct: {correct} | "
                f"Time: {response_time:.2f}s | Streak: {streak} | Confidence: {confidence}"
            )
        except Exception as e:
            logger.error(f"❌ Error logging progress: {e}")
            raise MathsException("Failed to log progress") from e
        finally:
            if conn:
                conn.close()

    def get_progress(self, session_id: str) -> pd.DataFrame:
        """Retrieve progress safely and prevent SQL injection."""
        conn = None
        try:
            conn = self._connect()
            df = pd.read_sql_query(
                "SELECT * FROM progress WHERE session_id = ?",
                conn,
                params=(session_id,)
            )
            logger.info(f"📊 Retrieved {len(df)} progress entries for session: {session_id}")
            return df
        except Exception as e:
            logger.error(f"❌ Failed retrieving progress: {e}")
            raise MathsException("Failed to retrieve progress data") from e
        finally:
            if conn:
                conn.close()

    @staticmethod
    def calculate_confidence(correct: bool, difficulty: str, response_time: float,
                             streak: int, expected_time: float) -> float:
        """Calculate learner confidence score with safe guards."""
        try:
            confidence = 50

            confidence += 20 * (2 * int(correct) - 1)  # +- 20 on correctness
            confidence += 2 * min(streak, 20)         # Max +40 from streak

            time_effect = 2 * (expected_time - response_time)
            time_effect = max(-15, min(15, time_effect))
            confidence += time_effect

            difficulty_score = {"Easy": 1, "Medium": 2, "Hard": 3}.get(difficulty, 1)
            confidence += 3 * difficulty_score * int(correct)

            confidence = max(0, min(100, confidence))
            final_score = round(confidence, 2)

            logger.info(
                f"💡 Confidence calculated: {final_score} ({difficulty}, streak={streak}, "
                f"response={response_time:.2f}s)"
            )
            return final_score

        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            raise MathsException("Failed to calculate confidence") from e
