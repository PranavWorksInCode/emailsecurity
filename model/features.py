import re
from urllib.parse import urlparse

from typing import Dict, Any

def extract_features(url: str) -> Dict[str, Any]:
    """
    Extracts numerical features from a URL string for ML processing.
    
    Args:
        url: The URL string to analyze.
        
    Returns:
        Dictionary containing features:
        - url_length (int)
        - hostname_length (int)
        - dot_count (int)
        - ...and other pattern matches.
    """
    features = {}
    
    # 1. Length Features
    features['url_length'] = len(url)
    features['hostname_length'] = 0
    
    try:
        parsed = urlparse(url)
        features['hostname_length'] = len(parsed.netloc)
    except:
        pass

    # 2. Character Counts (Phishers often use many dots or hyphens)
    features['dot_count'] = url.count('.')
    features['hyphen_count'] = url.count('-')
    features['at_count'] = url.count('@')
    features['qmark_count'] = url.count('?')
    features['slash_count'] = url.count('/')
    features['digits_count'] = sum(c.isdigit() for c in url)

    # 3. Pattern Matching
    # Check if IP address is used instead of domain (common in phishing)
    ip_pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.){3}([01]?\d\d?|2[0-4]\d|25[0-5])'
    features['has_ip'] = 1 if re.search(ip_pattern, url) else 0

    # Check for "https" (Phishers increasingly use https, but absence is still a signal)
    features['is_https'] = 1 if url.startswith('https') else 0

    return features
