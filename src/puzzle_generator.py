import random
import logging
from typing import Tuple

class PuzzleGenerator:
    """
    A class-based generator that creates math puzzles of varying difficulty
    for adaptive learning systems like Math Adventures.
    """

    OPERATIONS = ["+", "-", "*", "/"]
    DIFFICULTY_MAP = {"Easy": 1, "Medium": 2, "Hard": 3}

    def __init__(self):
        self.logger = logging.getLogger(__name__)


    def get_expected_time(self, difficulty: int, operation: str) -> float:
        """Estimate expected solving time based on operation and difficulty."""
        base_time = {
            "+": 5,
            "-": 6,
            "*": 8,
            "/": 10
        }.get(operation, 8)

        expected_time = base_time + (difficulty - 1) * 1.5
        self.logger.info(f"Expected time for {operation} at difficulty {difficulty}: {expected_time:.2f}s")
        return expected_time
    
    
    def generate_puzzle(self, level: str, streak: int = 1, confidence: float=50.0) -> Tuple[str, float, float, str]:
        """
        Generate a math puzzle based on the difficulty level, streak, and confidence.
        Returns: (question_text, correct_answer, expected_time, new_level)
        """
        level = level.capitalize()
        self.logger.info(f"Generating puzzle | Level: {level}, Streak: {streak}, Confidence: {confidence}")

        # Increase intensity if confidence is high
        confidence_high = confidence >= 80
        confidence_low = confidence <= 50

        if level == "Easy":
            if confidence_high:
                ops = ["+", "-", "*"]  
                num1, num2 = random.randint(10, 25), random.randint(5, 15)
            elif confidence_low:
                ops = ["+", "-"]
                num1, num2 = random.randint(1, 12), random.randint(1, 10)
            else:
                
                if streak <= 5:
                    ops = ["+", "-"]
                    num1, num2 = random.randint(1, 15), random.randint(1, 10)
                elif streak <= 8:
                    ops = ["+", "-"]
                    num1, num2 = random.randint(10, 30), random.randint(5, 15)
                else:
                    ops = ["*", "/"]
                    num1, num2 = random.randint(5, 20), random.randint(2, 10)

        elif level == "Medium":
            if confidence_high:
                ops = ["+", "-", "*", "/"]  
                num1, num2 = random.randint(30, 70), random.randint(10, 30)
            elif confidence_low:
                ops = ["+", "-", "*"]        
                num1, num2 = random.randint(10, 40), random.randint(5, 20)
            else:
                if streak <= 5:
                    ops = ["+", "-", "*"]
                    num1, num2 = random.randint(10, 40), random.randint(5, 20)
                elif streak <= 10:
                    ops = ["+", "-", "*", "/"]
                    num1, num2 = random.randint(20, 60), random.randint(5, 25)
                else:
                    ops = ["+", "-", "*", "/"]
                    num1, num2 = random.randint(30, 80), random.randint(10, 30)

        elif level == "Hard":
            if confidence_high:
                ops = ["+", "-", "*", "/"]
                num1, num2 = random.randint(80, 200), random.randint(10, 40)
            elif confidence_low:
                ops = ["+", "-", "*"]     
                num1, num2 = random.randint(20, 80), random.randint(5, 25)
            else:
                if streak <= 5:
                    ops = ["+", "-", "*", "/"]
                    num1, num2 = random.randint(20, 80), random.randint(5, 25)
                elif streak <= 10:
                    ops = ["+", "-", "*", "/"]
                    num1, num2 = random.randint(50, 120), random.randint(10, 30)
                else:
                    ops = ["+", "-", "*", "/"]
                    num1, num2 = random.randint(80, 200), random.randint(10, 40)

        else:
            raise ValueError("Invalid level! Choose Easy, Medium, or Hard.")

        
        op = random.choice(ops)
        if op == "/":
            num1 = num2 * random.randint(1, 9)
            correct_answer = round(num1 / num2, 2)
        else:
            correct_answer = eval(f"{num1} {op} {num2}")

        question = f"{num1} {op} {num2}"
        expected_time = self.get_expected_time(self.DIFFICULTY_MAP[level], op)

        self.logger.info(f"Generated puzzle: {question} = {correct_answer}, expected_time={expected_time:.2f}s")
        return question, correct_answer, expected_time
