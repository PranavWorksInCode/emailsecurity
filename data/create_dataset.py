import pandas as pd
import random

def generate_dataset():
    # Safe URLs (Benign)
    safe_urls = [
        "https://www.google.com",
        "https://www.youtube.com",
        "https://www.facebook.com",
        "https://en.wikipedia.org",
        "https://twitter.com",
        "https://www.amazon.com",
        "https://www.linkedin.com",
        "https://github.com",
        "https://stackoverflow.com",
        "https://www.microsoft.com",
        "http://example.com/page",
        "https://www.nytimes.com/section/world",
        "https://www.reddit.com/r/programming",
        "https://docs.python.org/3/library/index.html",
        "https://pypi.org/project/pandas/",
    ]
    
    # Phishing URLs (Malicious) - simulating common patterns
    phishing_urls = [
        "http://secure-login-bank.com.update-info.xyz",
        "http://paypal-verify-account.su",
        "https://x.co/suspicious",
        "http://192.168.1.1/login.php",
        "http://google-drive-secure-share.tk",
        "http://apple-id-reset.com.user-data.info",
        "http://verify-netflix-payment.net",
        "http://cryptocurrency-giveaway.biz/claim",
        "http://login.amazon.security-update.com",
        "http://w3b-f4ke-s1te.ru/index.html",
        "http://account-update-required.gq",
        "http://free-iphone-winner.com",
        "http://wellsfargo.secure-banking.com.phishing.site",
        "http://chaselogin-verify.com",
        "http://irs-tax-refund-claim.org",
    ]

    # Expand the dataset by adding random variations
    data = []
    
    for url in safe_urls:
        data.append({"url": url, "label": 0}) # 0 = Safe
        # Add some variations
        data.append({"url": url + "/contact", "label": 0})
        data.append({"url": url + "/about", "label": 0})

    for url in phishing_urls:
        data.append({"url": url, "label": 1}) # 1 = Phishing
        # Add some variations
        data.append({"url": url + "?token=12345", "label": 1})
        data.append({"url": url + "/login", "label": 1})

    df = pd.DataFrame(data)
    df.to_csv("data/dataset.csv", index=False)
    print(f"Created data/dataset.csv with {len(df)} samples.")

if __name__ == "__main__":
    generate_dataset()
