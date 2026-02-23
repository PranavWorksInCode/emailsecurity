# AI-Powered Email Shield (Phishing & Malware Detector)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg" alt="Machine Learning">
  <img src="https://img.shields.io/badge/Analytics-Streamlit-red.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Database-SQLite-lightgrey.svg" alt="SQLite">
</p>

## 🚀 Executive Summary

The **Email Shield** is an automated, AI-driven security middleware designed to intercept and neutralize sophisticated phishing threats and malware before they reach end-users. Unlike traditional blacklist-based filters that fail against Zero-Day attacks, this system employs a **Random Forest Machine Learning model** to perform real-time heuristic analyzing URL structures and file payloads.

It acts as a simulated **Secure Email Gateway (SEG)**, equipped with real-time file monitoring, malware heuristics, an ML prediction engine, and an interactive executive analytics dashboard.

---

## 🏗️ System Architecture & Data Flow

Our system follows a scalable micro-service architecture consisting of three primary components:

1. **Gateway Service (The Monitor)**: Functions as a File System Watcher. It monitors incoming streams and gracefully handles errors to prevent system crashes on corrupt data.
2. **Security Layer (The Shield & Brain)**:
   - **Malware Heuristics**: Pre-computes dangerous payloads, blocking executable files (`.exe`, `.bat`, `.vbs`) and performing **Magic Byte Verification** to counter spoofing (e.g., an executable disguised as a `.pdf`).
   - **ML Analysis Engine**: The neural core. Extracts features from URLs (e.g., length, entropy, IP usage, suspicious TLDs) and classifies them using a high-accuracy Random Forest Classifier.
3. **Action Handler (The Router)**: Deterministically routes emails to their final disposition based on the AI's `P(Phish)` confidence score. Safe emails enter the Inbox, while threats are instantly Quarantined.

### Data Feed Lifecycle
1. **Ingestion**: Email file is received in the `incoming/` buffer.
2. **Parsing**: A high-efficiency parser extracts embedded URLs.
3. **Inference**: URLs map to feature vectors (e.g., `[12, 0.45, 1, ...]`) and route through the AI model.
4. **Disposition**: If probability > 0.5, the threat is isolated. All events are logged to the audit database for UBA (User Behavior Analytics).

---

## 🛠️ Core Components & Tech Stack

- **Machine Learning**: `scikit-learn`, `pandas`, `numpy` (Random Forest, Feature Extraction)
- **Data Engineering**: Regular Expressions (Regex), Real-time Feature Mapping
- **Analytics Dashboard**: `streamlit` for executive threat visualization
- **Storage**: `sqlite3` for immutable audit logging

**Directory Structure:**
- `model/`: ML logic, dataset training (`train.py`), feature extraction (`features.py`), and the serialized AI model (`phishing_model.pkl`).
- `email_shield/`: Core application logic encompassing the Gateway (`gateway.py`), Heuristics, and Disposition routing (`inbox/`, `quarantine/`).
- `tools/`: Operational scripts including `generate_traffic.py` (simulates benign, phishing, malware, and spoofing traffic) and `reset_system.py`.

---

## 📊 Analytics & Reporting

The built-in **Executive Dashboard (`dashboard.py`)** provides a centralized view for SOC analysts:
- **Threat Landscape Visualization**: Real-time pie charts visualizing Safe vs. Phishing vs. Malware traffic composition.
- **Deep User Forensics**: Searchable grids to filter threats by Sender, Recipient, or AI Verdict.
- **Malware Tracking**: Pinpoints exact zero-day artifacts and spoofed extensions tied to specific threat actors.

---

## ⚙️ Setup & Installation

**1. Clone & Install Dependencies**
```bash
git clone https://github.com/PranavWorksInCode/emailsecurity.git
cd emailsecurity
pip install -r requirements.txt
```

**2. Initialize Dataset & Train Model (First Run Only)**
This simulates feature generation and builds the predictive model.
```bash
python data/create_dataset.py
python model/train.py
```

**3. Launch the Gateway Daemon**
This starts the real-time monitoring service on the `incoming/` directory.
```bash
python email_shield/gateway.py
```

**4. Run Simulations & View Analytics**
Generate synthetic threats to observe the mitigation in real-time, and view the SOC dashboard.
```bash
# Start the simulated traffic generator
python tools/generate_traffic.py

# Launch the Streamlit User Behavior Analytics Dashboard
streamlit run dashboard.py
```

**5. Factory Reset**
To clear the audit database and flush all email buffers:
```bash
python tools/reset_system.py
```

---

## 📈 Production Blueprint & Scaling (Enterprise)

To deploy this in a Fortune 500 Enterprise setting, the system is designed to scale from local polling to Cloud-Native integration:

- **API-Based Protection (M365 / Google Workspace)**: Upgrading the ingestion node to poll the **Microsoft Graph API**. It asynchronously consumes unread messages, leverages the API to move threats directly to Junk/Quarantine folders without network configuration changes.
- **Containerization**: Wrapping `production_gateway.py` into a Docker image deployed on **AWS ECS**, **Azure Container Apps**, or **Kubernetes**.
- **Event Streaming**: Transitioning the single-file loop ingestion to **Kafka Event Streams** for horizontally scaled parsing via Celery workers.
- **Advanced Threat Intel**: Roadmap includes Link Unshortening, Homograph Attack Detection (Typosquatting), Computer Vision for stolen banking logos, and NLP for high-urgency contextual scanning.

---

## 📄 License & Copyright

&copy; 2024 PranavWorksInCode. All Rights Reserved.

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. (If no LICENSE file exists, this code is provided for educational and portfolio purposes.)
