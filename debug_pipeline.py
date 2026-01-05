import os 
import sys
# Add 'email_shield' to path so gateway can import its siblings
sys.path.append(os.path.join(os.path.dirname(__file__), "email_shield"))

import time
from email_shield import gateway
from email_shield.db_manager import DBManager
from email_shield.predictor import PhishingPredictor

# Setup paths
base_dir = os.path.dirname(os.path.abspath(__file__))
# gateway.INCOMING_DIR is relative, usually "email_shield/incoming"
# We need to ensure we run this from the root

def test_pipeline():
    print("--- Starting Pipeline Test ---")
    
    # 1. Setup DB
    db = DBManager()
    
    # 2. Setup Predictor
    pred = PhishingPredictor("model/phishing_model.pkl")
    
    # 3. Create a Test File
    test_file = "email_shield/incoming/DEBUG_TEST_EMAIL.txt"
    with open(test_file, "w") as f:
        f.write("To: debug@test.com\nSubject: Debug\n\nCheck this safe link: https://google.com")
    
    print(f"Created test file: {test_file}")
    
    # 4. Run Scan (Manually trigger the function)
    print("Triggering scan_file()...")
    gateway.scan_file(test_file, pred, db)
    
    # 5. Verify DB
    print("Verifying Database...")
    import pandas as pd
    logs = db.get_all_logs()
    print(f"DB Row Count: {len(logs)}")
    
    if not logs.empty:
        last_entry = logs.iloc[-1]
        print(f"Last Entry: {last_entry['filename']} -> {last_entry['verdict']}")
        if last_entry['filename'] == "DEBUG_TEST_EMAIL.txt":
            print("SUCCESS: Pipeline is working!")
        else:
            print("WARNING: Pipeline ran but last entry doesn't match?")
    else:
        print("FAILURE: DB is still empty after scan.")

if __name__ == "__main__":
    test_pipeline()
