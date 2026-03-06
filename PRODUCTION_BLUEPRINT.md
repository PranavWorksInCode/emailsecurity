# My Production Deployment Blueprint: Microsoft 365 Integration

This document outlines how I plan to transform my **Email Shield** from a local file-based simulation into a cloud-native security application that protects a real organization (for example, using Microsoft 365).

## 1. The Architecture Change

| Feature | My Simulation (Current) | Production (Real World Target) |
| :--- | :--- | :--- |
| **Input** | Reads text files from `incoming/` | Polls **Microsoft Graph API** (`/messages`) |
| **Analysis** | Running locally on my laptop | Runs in **Docker / Azure Functions** |
| **Action** | Moves file to `quarantine/` | Sends API call to **Move to Junk / Delete** |
| **Storage** | Local SQLite DB | Managed SQL Database (PostgreSQL/AzureSQL) |

## 2. The Production Code (`production_gateway.py`)

I wrote this placeholder code to deploy server-side eventually. It replaces my file-watching loop with an API polling loop.

```python
import time
import requests
import json
from predictor import PhishingPredictor
# My db_manager would connect to a real SQL server here
from db_manager import DBManager 

# --- MY CONFIGURATION ---
TENANT_ID = "YOUR_TENANT_ID"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
TARGET_MAILBOX = "employees@company.com" # Or I could iterate through all users
GRAPH_API_URL = "https://graph.microsoft.com/v1.0"

class ProductionGateway:
    def __init__(self):
        self.predictor = PhishingPredictor(model_path="model/phishing_model.pkl")
        self.db = DBManager() # Connects to my Cloud SQL
        self.access_token = self._get_auth_token()

    def _get_auth_token(self):
        """Authenticates with Azure AD to get my access token."""
        url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
        data = {
            'client_id': CLIENT_ID,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': CLIENT_SECRET,
            'grant_type': 'client_credentials'
        }
        resp = requests.post(url, data=data)
        return resp.json().get('access_token')

    def fetch_new_emails(self):
        """Polls inbox for unread messages."""
        headers = {'Authorization': f'Bearer {self.access_token}'}
        # Get unread emails from Inbox
        endpoint = f"{GRAPH_API_URL}/users/{TARGET_MAILBOX}/mailFolders/inbox/messages"
        params = {'$filter': 'isRead eq false', '$top': 10}
        
        response = requests.get(endpoint, headers=headers, params=params)
        if response.status_code == 200:
            return response.json().get('value', [])
        return []

    def quarantine_email(self, message_id):
        """Moves a malicious email to the Junk folder via API."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        endpoint = f"{GRAPH_API_URL}/users/{TARGET_MAILBOX}/messages/{message_id}/move"
        data = {'destinationId': 'junkemail'}
        
        requests.post(endpoint, headers=headers, json=data)
        print(f" [!!!] Action Taken: Quarantined Message {message_id}")

    def run(self):
        print("Starting my Cloud Email Shield...")
        while True:
            emails = self.fetch_new_emails()
            
            for email in emails:
                subject = email.get('subject', 'No Subject')
                body_content = email.get('body', {}).get('content', '')
                sender = email.get('from', {}).get('emailAddress', {}).get('address')
                message_id = email.get('id')

                print(f"Analyzing: {subject} from {sender}")
                
                # Extract URLs (Reusing my parser logic)
                # Note: Real body is HTML, I might need BeautifulSoup to clean tags first
                urls = extract_urls_from_text(body_content) 
                
                # AI Prediction
                results = self.predictor.predict_urls(urls)
                
                if any(results.values()):
                    print(f" -> PHISHING DETECTED in {message_id}")
                    self.db.log_scan(message_id, sender, "PHISHING", str(results))
                    self.quarantine_email(message_id)
                else:
                    print(" -> Safe.")
                    self.db.log_scan(message_id, sender, "SAFE", "N/A")
            
            time.sleep(5) # Poll every 5 seconds

# Helper function placeholder I wrote
def extract_urls_from_text(text):
    import re
    return re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
```

## 3. My Deployment Instructions

To actually use this in a business environment:

1.  **Register App in Azure Portal**:
    *   Go to **Azure Active Directory** -> **App Registrations**.
    *   Create a new App (e.g., "AI-Email-Shield").
    *   **Permissions**: Add `Mail.ReadWrite` (Application Permission) so my app can scan *all* mailboxes without user login.
    *   Copy the `Tenant ID`, `Client ID`, and `Client Secret`.

2.  **Containerize (Docker)**:
    *   Create a `Dockerfile`:
        ```dockerfile
        FROM python:3.9-slim
        WORKDIR /app
        COPY . .
        RUN pip install -r requirements.txt
        CMD ["python", "production_gateway.py"]
        ```

3.  **Run in the Cloud**:
    *   Push this Docker container to **AWS ECS** or **Azure Container Apps**.
    *   Set the environment variables (IDs and Secrets) securely in the cloud console.

4.  **Integration**:
    *   My script will now run 24/7 in the cloud, silently watching the company's mailboxes and moving phishing links to Junk instantly.
