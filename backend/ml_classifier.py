import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "../ml/model.pkl"), "rb") as f:
    model = pickle.load(f)

with open(os.path.join(BASE_DIR, "../ml/vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

def predict_priority(text: str):
    if not text.strip():
        return None, 0.0

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = max(model.predict_proba(vec)[0])

    return pred, float(prob)
