# AI-Powered Phishing Detector (Email Shield)

A machine learning-based security tool that simulates an **Secure Email Gateway**. It monitors an `incoming` folder for new emails, extracts URLs, and uses a Random Forest classifier to determine if they are safe or malicious.

## Project Structure

- **`model/`**: Contains the Machine Learning logic.
    - `train.py`: Trains the model using `data/dataset.csv`.
    - `features.py`: Extracts numerical features from URLs (dots, length, IP address, etc.).
    - `phishing_model.pkl`: The saved AI model.
- **`email_shield/`**: The application logic.
    - `gateway.py`: The main service. Watches for files and moves them.
    - `incoming/`: Drop text files here to be scanned.
    - `inbox/`: Safe emails end up here.
    - `quarantine/`: Phishing emails are moved here.
- **`tools/`**: Utility scripts.
    - `generate_traffic.py`: Simulates traffic (Safe, Phishing, Malware, Spoofing).
    - `reset_system.py`: Clears the database and all email folders.
- `dashboard.py`: The Analytics Dashboard (Streamlit).

## Setup & Usage

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Generate Data & Train Model** (First time only):
    ```bash
    python data/create_dataset.py
    python model/train.py
    ```

3.  **Run the Email Shield**:
    ```bash
    python email_shield/gateway.py
    ```
    The script will start monitoring `email_shield/incoming/`.

4.  **Simulate Traffic & Dashboard**:
    ```bash
    python tools/generate_traffic.py
    streamlit run dashboard.py
    ```

5.  **Reset System**:
    To clear all data and start fresh:
    ```bash
    python tools/reset_system.py
    ```

4.  **Test it**:
    - Create a text file in `email_shield/incoming/` with a URL inside.
    - Watch it disappear and reappear in either `inbox/` or `quarantine/`.
