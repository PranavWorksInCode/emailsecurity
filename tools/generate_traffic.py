import time
import random
import os

INCOMING_DIR = "email_shield/incoming"

TEMPLATE_SAFE = """Subject: Safe Email {id}
Hello, check out this interesting article: https://www.wikipedia.org/wiki/{topic}
"""

TEMPLATE_PHISHING = """Subject: URGENT ACTION REQUIRED {id}
Your account is compromised! Click here to reset: http://secure-login-{bank}.com/reset-password
"""

TOPICS = ["Python", "Space", "History", "Cooking", "Travel"]
BANKS = ["chase-secure", "boa-verify", "wellsfargo-update", "paypal-security"]

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
        
        if is_phishing:
            content = TEMPLATE_PHISHING.format(id=count, bank=random.choice(BANKS))
            filename = f"email_{count}_phishing.txt"
        else:
            content = TEMPLATE_SAFE.format(id=count, topic=random.choice(TOPICS))
            filename = f"email_{count}_safe.txt"
            
        filepath = os.path.join(INCOMING_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(content)
            
        print(f"[{count}] Generated: {filename} ({'PHISHING' if is_phishing else 'SAFE'})")
        count += 1
        time.sleep(3)

if __name__ == "__main__":
    generate_traffic()
