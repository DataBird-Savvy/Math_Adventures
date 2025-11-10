import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

data=pd.read_csv("../data/learning_progress_expanded.csv")

X = data[["difficulty", "response_time", "correct", "streak","confidence"]]
y = data["next_level"]



model = RandomForestClassifier()
model.fit(X, y)

pred = model.predict([[2, 6.1, 1, 2,87.5]])  
print("Predicted next level:", pred[0])


with open("../artifacts/level_recommender_model.pkl", "wb") as f:
    pickle.dump(model, f)
