import time
import random
import os

INCOMING_DIR = "email_shield/incoming"

TEMPLATE_SAFE = """To: {user}
Subject: Safe Email {id}

Hello, check out this interesting article: https://www.wikipedia.org/wiki/{topic}
"""

TEMPLATE_PHISHING = """To: {user}
Subject: URGENT ACTION REQUIRED {id}

Your account is compromised! Click here to reset: http://secure-login-{bank}.com/reset-password
"""

TOPICS = ["Python", "Space", "History", "Cooking", "Travel"]
BANKS = ["chase-secure", "boa-verify", "wellsfargo-update", "paypal-security"]
EMPLOYEES = ["alice@company.com", "bob@company.com", "charlie@company.com", "david@company.com", "eve@company.com"]

def ensure_dir():
    if not os.path.exists(INCOMING_DIR):
        os.makedirs(INCOMING_DIR)

def generate_traffic():
    ensure_dir()
    print(f"--- Traffic Generator Started ---")
    print(f"Dropping files into '{INCOMING_DIR}' every 3 seconds...")
    print("Press Ctrl+C to stop.")

    count = 1
    while True:
        is_phishing = random.choice([True, False])
        user = random.choice(EMPLOYEES)
        
        if is_phishing:
            content = TEMPLATE_PHISHING.format(id=count, bank=random.choice(BANKS), user=user)
            filename = f"email_{count}_phishing.txt"
        else:
            content = TEMPLATE_SAFE.format(id=count, topic=random.choice(TOPICS), user=user)
            filename = f"email_{count}_safe.txt"
            
        filepath = os.path.join(INCOMING_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(content)
            
        print(f"[{count}] Generated: {filename} ({'PHISHING' if is_phishing else 'SAFE'})")
        count += 1
        time.sleep(3)

if __name__ == "__main__":
    generate_traffic()
