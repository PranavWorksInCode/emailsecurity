import time
import random
import os

INCOMING_DIR = "email_shield/incoming"

TEMPLATE_SAFE = """From: HR@company.com
To: {user}
Subject: Safe Email {id}

Hello, check out this interesting article: https://www.wikipedia.org/wiki/{topic}
"""

TEMPLATE_PHISHING = """From: security@{bank}.com
To: {user}
Subject: URGENT ACTION REQUIRED {id}

Your account is compromised! Click here to reset: http://secure-login-{bank}.com/reset-password
"""

TEMPLATE_MALWARE = """From: hacker@darkweb.net
To: {user}
Subject: Invoice {id}
Attachment: invoice_copy.exe

Please open the attached invoice.
"""

TEMPLATE_SPOOF = """From: sneaky@apt-group.org
To: {user}
Subject: Resume {id}
Attachment: my_resume.pdf
Magic: 4D 5A

Here is my resume.
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
        choice = random.choice(["SAFE", "PHISHING", "MALWARE", "SPOOF"])
        user = random.choice(EMPLOYEES)
        
        if choice == "PHISHING":
            content = TEMPLATE_PHISHING.format(id=count, bank=random.choice(BANKS), user=user)
            filename = f"email_{count}_phishing.txt"
        elif choice == "MALWARE":
            content = TEMPLATE_MALWARE.format(id=count, user=user)
            filename = f"email_{count}_malware.txt"
        elif choice == "SPOOF":
            content = TEMPLATE_SPOOF.format(id=count, user=user)
            filename = f"email_{count}_spoof.txt"
        else: # SAFE
            content = TEMPLATE_SAFE.format(id=count, topic=random.choice(TOPICS), user=user)
            filename = f"email_{count}_safe.txt"
            
        filepath = os.path.join(INCOMING_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(content)
            
        print(f"[{count}] Generated: {filename} ({choice})")
        count += 1
        time.sleep(3)

if __name__ == "__main__":
    generate_traffic()
