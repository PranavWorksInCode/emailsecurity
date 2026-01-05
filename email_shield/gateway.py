import os
import time
import shutil
import email_parser
from predictor import PhishingPredictor
from db_manager import DBManager

# Configuration
INCOMING_DIR = "email_shield/incoming"
INBOX_DIR = "email_shield/inbox"
QUARANTINE_DIR = "email_shield/quarantine"
MODEL_PATH = "model/phishing_model.pkl"

def ensure_dirs() -> None:
    """Creates necessary directories if they don't exist."""
    for d in [INCOMING_DIR, INBOX_DIR, QUARANTINE_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)

def scan_file(filepath: str, predictor: PhishingPredictor, db: DBManager) -> None:
    """
    Reads a file, extracts URLs, scans them using the AI predictor,
    and moves the file to the appropriate folder.
    
    Args:
        filepath: Absolute or relative path to the email file.
        predictor: Instance of PhishingPredictor class.
        db: Instance of DBManager for logging.
    """
    print(f"Scanning {filepath}...")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Extract Metadata
    urls = email_parser.extract_urls_from_text(content)
    user_email = email_parser.extract_recipient(content)
    filename = os.path.basename(filepath)
    
    if not urls:
        print(" -> No URLs found. Safe.")
        db.log_scan(filename, user_email, "SAFE", "N/A")
        move_file(filepath, INBOX_DIR)
        return

    print(f" -> Found {len(urls)} URLs. Checking against AI Model...")
    results = predictor.predict_urls(urls)
    
    is_malicious = False
    malicious_url = "N/A"
    
    for url, is_phishing in results.items():
        if is_phishing:
            print(f" [!!!] PHISHING DETECTED: {url}")
            is_malicious = True
            malicious_url = url
            break # Log the first malicious URL found
    
    if is_malicious:
        print(" -> Verdict: MALICIOUS. Moving to Quarantine.")
        db.log_scan(filename, user_email, "PHISHING", malicious_url)
        move_file(filepath, QUARANTINE_DIR)
    else:
        print(" -> Verdict: SAFE. Moving to Inbox.")
        db.log_scan(filename, user_email, "SAFE", "N/A")
        move_file(filepath, INBOX_DIR)

def move_file(src: str, dest_folder: str) -> None:
    """
    Moves a file to the destination folder, handling name collisions.
    """
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
    print("Loading AI Brain & Database...")
    # Adjust path to model since we run from root
    predictor = PhishingPredictor(model_path=MODEL_PATH)
    db = DBManager()
    
    print(f"Email Shield Gateway Active.")
    print(f"Monitoring '{INCOMING_DIR}'... (Press Ctrl+C to stop)")
    
    while True:
        # List files in incoming directory
        files = [f for f in os.listdir(INCOMING_DIR) if os.path.isfile(os.path.join(INCOMING_DIR, f))]
        
        for file in files:
            filepath = os.path.join(INCOMING_DIR, file)
            # Short sleep to ensure file write is complete
            time.sleep(0.5) 
            scan_file(filepath, predictor, db)
            
        time.sleep(2) # Check every 2 seconds

if __name__ == "__main__":
    main()
