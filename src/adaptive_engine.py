import pickle
import pandas as pd
from typing import Tuple
from logger import logger
from exception import MathsException


class AdaptiveEngine:
    """
    Adaptive difficulty recommendation engine for Math Adventures.
    Uses a trained ML model to predict the next difficulty level
    based on user performance and confidence.
    """

    def __init__(self, model_path: str = "artifacts/level_recommender_model.pkl"):

        self.logger = logger
        self.model_path = model_path

        self.difficulty_mapping = {"Easy": 1, "Medium": 2, "Hard": 3}
        self.reverse_difficulty_mapping = {v: k for k, v in self.difficulty_mapping.items()}

        self.model = self._load_model()

    def _load_model(self):
        """Loads the ML model safely."""
        try:
            with open(self.model_path, "rb") as f:
                model = pickle.load(f)
            self.logger.info(f" Model loaded successfully from: {self.model_path}")
            return model
        except FileNotFoundError:
            self.logger.error(f" Model file not found: {self.model_path}")
            raise MathsException("Model file missing! Ensure trained model exists.")
        except Exception as e:
            self.logger.error(f" Failed to load model: {e}")
            raise MathsException("Model loading failed!") from e

    def recommend_next_level(
        self,
        current_level: str,
        correct: bool,
        response_time: float,
        streak: int,
        confidence: float
    ) -> Tuple[str, int]:
        """Predicts next difficulty with safe fallback behavior."""

        try:
            level_encoded = self.difficulty_mapping.get(current_level, 2)

            input_data = pd.DataFrame([{
                "difficulty": level_encoded,
                "response_time": response_time,
                "correct": int(correct),
                "streak": streak,
                "confidence": confidence
            }])

            self.logger.info(
                f"🧠 Predicting -> "
                f"Level: {current_level}, Correct: {correct}, Time: {response_time:.2f}s, "
                f"Streak: {streak}, Conf: {confidence:.2f}"
            )

            predicted_level_num = self.model.predict(input_data)[0]
            next_level = self.reverse_difficulty_mapping.get(predicted_level_num, current_level)

        except MathsException:
            raise  # already logged
        except Exception as e:
            self.logger.error(f" Prediction failed: {e}")
            next_level = current_level  # fallback
            self.logger.warning("⚠ Falling back to current difficulty due to error.")

        # Update streak logic
        new_streak = streak + 1 if correct else 0

        self.logger.info(f"Output → Next Level: {next_level} | New Streak: {new_streak}")
        return next_level, new_streak
