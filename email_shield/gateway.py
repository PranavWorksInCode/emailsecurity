import os
import time
import shutil
import email_parser
from predictor import PhishingPredictor

# Configuration
INCOMING_DIR = "email_shield/incoming"
INBOX_DIR = "email_shield/inbox"
QUARANTINE_DIR = "email_shield/quarantine"
MODEL_PATH = "model/phishing_model.pkl"

def ensure_dirs():
    for d in [INCOMING_DIR, INBOX_DIR, QUARANTINE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def scan_file(filepath, predictor):
    print(f"Scanning {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    urls = email_parser.extract_urls_from_text(content)
    
    if not urls:
        print(" -> No URLs found. Safe.")
        move_file(filepath, INBOX_DIR)
        return

    print(f" -> Found {len(urls)} URLs. Checking against AI Model...")
    results = predictor.predict_urls(urls)
    
    is_malicious = False
    for url, is_phishing in results.items():
        if is_phishing:
            print(f" [!!!] PHISHING DETECTED: {url}")
            is_malicious = True
    
    if is_malicious:
        print(" -> Verdict: MALICIOUS. Moving to Quarantine.")
        move_file(filepath, QUARANTINE_DIR)
    else:
        print(" -> Verdict: SAFE. Moving to Inbox.")
        move_file(filepath, INBOX_DIR)

def move_file(src, dest_folder):
    filename = os.path.basename(src)
    dest_path = os.path.join(dest_folder, filename)
    
    # Handle duplicate names
    counter = 1
    while os.path.exists(dest_path):
        name, ext = os.path.splitext(filename)
        dest_path = os.path.join(dest_folder, f"{name}_{counter}{ext}")
        counter += 1
        
    shutil.move(src, dest_path)

def main():
    ensure_dirs()
    print("Loading AI Brain...")
    # Adjust path to model since we run from root
    predictor = PhishingPredictor(model_path=MODEL_PATH)
    
    print(f"Email Shield Gateway Active.")
    print(f"Monitoring '{INCOMING_DIR}'... (Press Ctrl+C to stop)")
    
    while True:
        # List files in incoming directory
        files = [f for f in os.listdir(INCOMING_DIR) if os.path.isfile(os.path.join(INCOMING_DIR, f))]
        
        for file in files:
            filepath = os.path.join(INCOMING_DIR, file)
            # Short sleep to ensure file write is complete
            time.sleep(0.5) 
            scan_file(filepath, predictor)
            
        time.sleep(2) # Check every 2 seconds

if __name__ == "__main__":
    main()
