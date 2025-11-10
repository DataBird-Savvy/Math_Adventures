
import pickle
import pandas as pd
from typing import Tuple
from logger import logger


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
        """Loads the ML model from pickle file."""
        try:
            with open(self.model_path, "rb") as f:
                model = pickle.load(f)
            self.logger.info(f"Model loaded successfully from {self.model_path}")
            return model
        except Exception as e:
            self.logger.error(f"Failed to load model from {self.model_path}: {e}")
            raise e

   
    def recommend_next_level(
        self,
        current_level: str,
        correct: bool,
        response_time: float,
        streak: int,
        confidence: float
    ) -> Tuple[str, int]:
        """
        Predicts the next difficulty level based on performance metrics.

        Args:
            current_level (str): Current difficulty ('Easy', 'Medium', 'Hard')
            correct (bool): Whether the answer was correct
            response_time (float): Time taken to answer
            streak (int): Current streak of correct answers
            confidence (float): Calculated confidence score

        Returns:
            tuple: (next_level: str, updated_streak: int)
        """
    
        self.logger.info(
            f"🧠 Input -> Level: {current_level}, Correct: {correct}, "
            f"Time: {response_time:.2f}s, Streak: {streak}, Confidence: {confidence:.2f}"
        )


        input_data = pd.DataFrame([{
            "difficulty": self.difficulty_mapping.get(current_level, 2),
            "response_time": response_time,
            "correct": int(correct),
            "streak": streak,
            "confidence": confidence
        }])

        try:
            predicted_level_num = self.model.predict(input_data)[0]
            next_level = self.reverse_difficulty_mapping.get(predicted_level_num, "Medium")
        except Exception as e:
            self.logger.error(f"Model prediction failed: {e}")
            next_level = current_level 

      
        new_streak = streak + 1 if correct else 0

        self.logger.info(f"Predicted Next Level: {next_level} | New Streak: {new_streak}")
        return next_level, new_streak
