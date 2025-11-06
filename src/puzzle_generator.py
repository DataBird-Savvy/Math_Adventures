import random

# Operation sequences for progressive difficulty
OPERATIONS = ["+", "-", "*", "/"]

def generate_puzzle(level):
    """
    Generate a math puzzle based on the difficulty level.
    Returns (question_text, correct_answer)
    """

    if level == "Easy":

        num1, num2 = random.randint(1, 9), random.randint(1, 9)
        op = random.choice(["+", "-"])
    elif level == "Medium":

        num1, num2 = random.randint(10, 50), random.randint(1, 20)
        op = random.choice(["+", "-", "*"])
        
    elif level == "Hard":

        num1, num2 = random.randint(10, 99), random.randint(1, 50)
        op = random.choice(OPERATIONS)
    else:

        num1, num2 = random.randint(100, 999), random.randint(10, 99)
        op = random.choice(OPERATIONS)

    if op == "/":
        num2 = random.randint(1, 9)
        num1 = num2 * random.randint(1, 9) 


    question = f"{num1} {op} {num2}"


    correct_answer = eval(question)

    if isinstance(correct_answer, float):
        correct_answer = round(correct_answer, 2)

    return question, correct_answer





if __name__ == "__main__":
   
    for lvl in ["Easy", "Medium", "Hard", "Very Hard"]:
        q, a = generate_puzzle(lvl)
        print(f"{lvl}: {q} = {a}")
