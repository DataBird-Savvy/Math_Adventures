
import pickle
import pandas as pd
def recommend_next_level(current_level, correct, response_time, streak):
    loaded_model = pickle.load(open("artifacts/level_recommender_model.pkl", "rb"))
    difficulty_mapping = {"Easy": 1, "Medium": 2, "Hard": 3}
    reverse_difficulty_mapping = {1: "Easy", 2: "Medium", 3: "Hard"}    
    input_data = pd.DataFrame([{
        "difficulty": difficulty_mapping[current_level],
        "response_time": response_time,
        "correct": int(correct),
        "streak": streak
    }])
   
    predicted_level_num = loaded_model.predict(input_data)[0]   
    next_level=reverse_difficulty_mapping[predicted_level_num]
    if correct:
        streak += 1
    else:
        streak = 0
    return next_level, streak
