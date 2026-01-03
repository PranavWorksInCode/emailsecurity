import re

def extract_urls_from_text(text):
    """
    Finds all HTTP/HTTPS URLs in a text string.
    Returns a list of URLs.
    """
    # Regex pattern for finding URLs
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*'
    
    urls = re.findall(url_pattern, text)
    
    # Clean up trailing punctuation often caught by regex (like period at end of sentence)
    clean_urls = []
    for url in urls:
        if url.endswith('.') or url.endswith(','):
            url = url[:-1]
        clean_urls.append(url)
        
    return list(set(clean_urls)) # Return unique URLs
