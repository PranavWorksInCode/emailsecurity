# My Email Shield: Machine Learning Architecture & Concepts

This document provides an in-depth explanation of how I implemented machine learning (ML) within my **Email Shield** project to detect and block phishing and malicious emails.

## 1. Executive Summary of My ML Approach
Traditional email gateways rely heavily on signatures and static blacklists which fail against Zero-Day phishing attacks. I wanted to build something smarter. So, my Email Shield employs a **Machine Learning** approach, specifically using a **Random Forest Classifier** from the `scikit-learn` library, to analyze URL structures dynamically. 

By extracting heuristic features from the URLs found in incoming emails, my model can accurately classify them as `Safe` or `Phishing` based on common patterns I've observed threat actors adopting.

---

## 2. Model Selection: Why I Chose Random Forest
I decided to use the `RandomForestClassifier` with 100 decision trees (`n_estimators=100`). 
**Here's why I went with Random Forest:**
- **Robustness**: It builds multiple decision trees and merges them together, which gives me a much more accurate and stable prediction.
- **Overfitting Prevention**: By averaging multiple trees, I reduced the risk of overfitting on my training data.
- **Interpretable Features**: It works remarkably well with the numerical heuristic features I extract from URLs.

---

## 3. The Dataset I Created (`data/create_dataset.py`)
Machine Learning requires labeled data to train the model, so I generated a synthetic dataset containing both benign and malicious tracking patterns.
- **Safe URLs (Label 0)**: Standard domains like `google.com`, `wikipedia.org`, `microsoft.com`, often appended with variations like `/contact` or `/about`.
- **Phishing URLs (Label 1)**: Simulated malicious URLs characterized by distinct patterns I've modeled:
  - Typosquatting and subdomains (e.g., `secure-login-bank.com.update-info.xyz`)
  - Verification lures (e.g., `verify-netflix-payment.net`)
  - Direct IP addresses instead of hostnames (e.g., `192.168.1.1/login.php`)

I compiled all of this data into a CSV file (`data/dataset.csv`), which acts as the ground truth during my training phase.

---

## 4. Feature Extraction (`model/features.py`)
I couldn't just feed raw URL strings directly into the Random Forest model; I had to transform them into a numerical representation (a feature vector). So, I built a parser in my Email Shield to extract the following 10 features from every URL:

1. **`url_length`**: Total character count of the URL. I look for phishing URLs that are excessively long to obscure the actual domain.
2. **`hostname_length`**: Character count of just the domain name (netloc). 
3. **`dot_count`**: Number of `.` characters. Multiple subdomains (e.g., `login.amazon.secure.com`) indicate high risk to my model.
4. **`hyphen_count`**: Number of `-` characters. I noticed threat actors frequently use hyphenated domains (e.g., `update-account-now.com`).
5. **`at_count`**: Number of `@` characters. An `@` symbol in a URL can trick the browser into ignoring everything preceding it, a classic phishing tactic I wanted to catch.
6. **`qmark_count`**: Number of `?` characters, indicating query parameters.
7. **`slash_count`**: Number of `/` characters, representing deep directory paths.
8. **`digits_count`**: Total numeric digits. High numbers of digits often indicate randomly generated URLs in my tests.
9. **`has_ip`**: A regular expression check (0 or 1) that flags if an IPv4 address is used instead of a standard domain.
10. **`is_https`**: Checks if the URL protocol is HTTPS (1) or HTTP (0). While attackers use HTTPS frequently today, raw HTTP is still a strong anomaly signal for my model.

**Example Process from my code:**
A URL like `http://192.168.1.1/login.php?token=123` is mapped to a vector:
`[39, 11, 3, 0, 0, 1, 3, 11, 1, 0]`

---

## 5. Model Training & Serialization (`model/train.py`)
I automated the learning process in my training pipeline:
1. **Data Loading**: Loads my `data/dataset.csv`.
2. **Transformation**: Iterates over every URL and generates the feature vector using my `features.py` script.
3. **Splitting**: Splits the data into a **Training Set (80%)** and a **Testing Set (20%)** using `train_test_split`.
4. **Training**: My Random Forest model (`rf.fit(X_train, y_train)`) learns to correlate the 10 features with the `Safe` (0) or `Phishing` (1) labels.
5. **Evaluation**: Predicts against the 20% test set, generating an accuracy score and classification report so I can ensure it generalizes well.
6. **Serialization**: The trained model state is securely saved as a binary pickle file (`phishing_model.pkl`) using `joblib`. This allows my gateway to load the pre-trained brain without retraining on every email.

---

## 6. Real-Time Inference & Disposition (`email_shield/gateway.py`)
Once I deploy it, my `gateway.py` script actively polls the `incoming/` directory.

- **Parsing**: When an email file drops, it extracts all URLs via my `email_parser.extract_urls_from_text`.
- **Prediction**: It feeds the URLs to the `PhishingPredictor` (which deserializes the `.pkl` model). The model converts the URLs to feature vectors in real-time and runs `.predict()`.
- **Routing**: 
  - If *any* URL is flagged as `1` (Phishing), my gateway drops the entire file into the `quarantine/` folder.
  - If my model returns `0` (Safe) for all URLs, and it passes the Malware/signature heuristic checks I implemented, the email routes safely to the `inbox/`.
- **Audit Logging**: The decision, along with the specific malicious URL isolated by my model, is logged to `audit_log.db` so I can view it on the executive dashboard I built.
