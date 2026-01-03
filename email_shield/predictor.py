import joblib
import os
import sys

# Add parent directory to path so we can import 'model.features'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model import features

class PhishingPredictor:
    def __init__(self, model_path="model/phishing_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.load_model()

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            print("Model loaded successfully.")
        else:
            print(f"Warning: Model not found at {self.model_path}. Please run train.py first.")

    def predict_urls(self, urls):
        """
        Takes a list of URL strings.
        Returns a dict: { "url": is_phishing(bool) }
        """
        if not self.model:
            return {url: False for url in urls} # Fail open if no model (for safety)

        results = {}
        for url in urls:
            # Extract features
            feat_dict = features.extract_features(url)
            # Convert to list (matching training format)
            feat_vector = [list(feat_dict.values())]
            
            # Predict (1 = Phishing, 0 = Safe)
            prediction = self.model.predict(feat_vector)[0]
            results[url] = bool(prediction == 1)
            
        return results
