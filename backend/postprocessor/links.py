import re
from urllib.parse import urlparse

def validate_urls(text: str) -> list:
    """
    Finds and validates all URLs in the text. Returns a list of (url, is_valid) tuples.
    """
    url_pattern = re.compile(r'https?://\S+')
    urls = url_pattern.findall(text)
    results = []
    for url in urls:
        try:
            result = urlparse(url)
            is_valid = all([result.scheme, result.netloc])
        except Exception:
            is_valid = False
        results.append((url, is_valid))
    return results
