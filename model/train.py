import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import features
import os

# 1. Load Data
print("Loading dataset...")
try:
    df = pd.read_csv("data/dataset.csv")
except FileNotFoundError:
    print("Error: data/dataset.csv not found. Run data/create_dataset.py first.")
    exit()

# 2. Extract Features
print("Extracting features (this might take a moment)...")
X_data = [] # List of feature lists
for url in df['url']:
    feat_dict = features.extract_features(url)
    X_data.append(list(feat_dict.values())) # Convert dict to list of values

y = df['label'] # Target variable (0 = Safe, 1 = Phishing)

# 3. Split Data
X_train, X_test, y_train, y_test = train_test_split(X_data, y, test_size=0.2, random_state=42)

# 4. Train Model
print("Training Random Forest Classifier...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

# 5. Evaluate
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 6. Save Model
model_path = "model/phishing_model.pkl"
joblib.dump(rf, model_path)
print(f"Model saved to {model_path}")
