import sqlite3
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# تحديد المسارات
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "database.db")
MODEL_DIR = os.path.join(BASE_DIR, "core")


def train_model():
    """
    يجلب البيانات من الـ SQL، يحولها لأرقام، ويدرب مودل Random Forest محلياً
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code_snippet, category, label FROM dataset")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("Data set is empty! Please run initial_dataset.py first.")
        return

    X = [row[0] for row in rows]
    y = [
        f"{row[1]}_{row[2]}" for row in rows
    ]  # مثل: 'security_bad' أو 'clean_code_good'

    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    X_vectorized = vectorizer.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_vectorized, y)

    with open(os.path.join(MODEL_DIR, "classifier.pkl"), "wb") as f:
        pickle.dump(model, f)
    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    print(" Model and Vectorizer trained and saved successfully inside 'core/'.")


def predict_code_snippet(snippet):
    """
    توقع حالة كود معين مع استخراج درجة الثقة الذاتية للمودل
    """
    # تحميل المودل والـ Vectorizer
    with open(os.path.join(MODEL_DIR, "classifier.pkl"), "rb") as f:
        model = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    snippet_vec = vectorizer.transform([snippet])
    prediction = model.predict(snippet_vec)[0]

    probabilities = model.predict_proba(snippet_vec)[0]
    max_prob = max(probabilities)

    category, label = prediction.split("_")
    return category, label, max_prob


if __name__ == "__main__":
    train_model()

    test_snippet = "eval(user_input)"
    cat, lbl, confidence = predict_code_snippet(test_snippet)
    print(f"\n--- Model Inference Test ---")
    print(f"Code: {test_snippet}")
    print(f"Predicted Category: {cat} | Label: {lbl} | Confidence: {confidence:.2%}")
