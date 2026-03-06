# Email Shield: Machine Learning Architecture & Concepts

This document provides an in-depth explanation of how machine learning (ML) is implemented within the **Email Shield** project to detect and block phishing and malicious emails.

## 1. Executive Summary of the ML Approach
Traditional email gateways rely heavily on signatures and static blacklists which fail against Zero-Day phishing attacks. Email Shield employs a **Machine Learning** approach, specifically using a **Random Forest Classifier** from the `scikit-learn` library, to analyze URL structures dynamically. 

By extracting heuristic features from the URLs found in incoming emails, the model can accurately classify them as `Safe` or `Phishing` based on common patterns adopted by threat actors.

---

## 2. Model Selection: Random Forest Classifier
The system uses the `RandomForestClassifier` with 100 decision trees (`n_estimators=100`). 
**Why Random Forest?**
- **Robustness**: It builds multiple decision trees and merges them together for a more accurate and stable prediction.
- **Overfitting Prevention**: By averaging multiple trees, it reduces the risk of overfitting on the training data.
- **Interpretable Features**: It works remarkably well with numerical heuristic features extracted from URLs.

---

## 3. The Dataset (`data/create_dataset.py`)
Machine Learning requires labelled data to train the model. The project generates a synthetic dataset containing both benign and malicious tracking patterns.
- **Safe URLs (Label 0)**: Standard domains like `google.com`, `wikipedia.org`, `microsoft.com`, often appended with variations like `/contact` or `/about`.
- **Phishing URLs (Label 1)**: Simulated malicious URLs characterized by distinct patterns:
  - Typosquatting and subdomains (e.g., `secure-login-bank.com.update-info.xyz`)
  - Verification lures (e.g., `verify-netflix-payment.net`)
  - Direct IP addresses instead of hostnames (e.g., `192.168.1.1/login.php`)

All data is compiled into a CSV file (`data/dataset.csv`) which functions as the ground truth during the training phase.

---

## 4. Feature Extraction (`model/features.py`)
The raw URL strings cannot be fed directly into the Random Forest model; they must be transformed into a numerical representation (a feature vector). Email Shield parses every URL to extract the following 10 features:

1. **`url_length`**: Total character count of the URL. Phishing URLs are often excessively long to obscure the actual domain.
2. **`hostname_length`**: Character count of just the domain name (netloc). 
3. **`dot_count`**: Number of `.` characters. Multiple subdomains (e.g., `login.amazon.secure.com`) indicate high risk.
4. **`hyphen_count`**: Number of `-` characters. Threat actors frequently use hyphenated domains (e.g., `update-account-now.com`).
5. **`at_count`**: Number of `@` characters. An `@` symbol in a URL can trick the browser into ignoring everything preceding it, a classic phishing tactic.
6. **`qmark_count`**: Number of `?` characters, indicating query parameters.
7. **`slash_count`**: Number of `/` characters, representing deep directory paths.
8. **`digits_count`**: Total numeric digits. High numbers of digits can indicate randomly generated URLs.
9. **`has_ip`**: A regular expression check (0 or 1) that flags if an IPv4 address is used instead of a standard domain.
10. **`is_https`**: Checks if the URL protocol is HTTPS (1) or HTTP (0). While attackers use HTTPS frequently today, raw HTTP is still a strong anomaly signal.

**Example Process:**
A URL like `http://192.168.1.1/login.php?token=123` is mapped to a vector:
`[39, 11, 3, 0, 0, 1, 3, 11, 1, 0]`

---

## 5. Model Training & Serialization (`model/train.py`)
The training pipeline automates the learning process:
1. **Data Loading**: Loads `data/dataset.csv`.
2. **Transformation**: Iterates over every URL and generates the feature vector using `features.py`.
3. **Splitting**: Splits the data into a **Training Set (80%)** and a **Testing Set (20%)** using `train_test_split`.
4. **Training**: The Random Forest model (`rf.fit(X_train, y_train)`) learns to correlate the 10 features with the `Safe` (0) or `Phishing` (1) labels.
5. **Evaluation**: Predicts against the 20% test set, generating an accuracy score and classification report to ensure it generalizes well.
6. **Serialization**: The trained model state is securely saved as a binary pickle file (`phishing_model.pkl`) using `joblib`. This allows the gateway to load the pre-trained brain without retraining on every email.

---

## 6. Real-Time Inference & Disposition (`email_shield/gateway.py`)
Once deployed, the `gateway.py` script actively polls the `incoming/` directory.

- **Parsing**: When an email file drops, it extracts all URLs via `email_parser.extract_urls_from_text`.
- **Prediction**: It feeds the URLs to the `PhishingPredictor` (which deserializes the `.pkl` model). The model converts the URLs to feature vectors in real-time and runs `.predict()`.
- **Routing**: 
  - If *any* URL is flagged as `1` (Phishing), the entire file drops into the `quarantine/` folder.
  - If the model returns `0` (Safe) for all URLs, and it passes the Malware/signature heuristic checks, the email routes to the `inbox/`.
- **Audit Logging**: The decision, along with the specific malicious URL isolated by the model, is logged to `audit_log.db` for the executive dashboard.
