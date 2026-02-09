import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load data
df = pd.read_csv("training_data.csv")

X = df["text"]
y = df["priority"]

# Vectorizer
vectorizer = TfidfVectorizer(stop_words="english")

X_vec = vectorizer.fit_transform(X)

# Model
model = LogisticRegression(max_iter=1000)
model.fit(X_vec, y)

# Save model + vectorizer
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("✅ ML model trained and saved")
