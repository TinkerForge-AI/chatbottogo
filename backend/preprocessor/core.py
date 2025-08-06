import re
from html import unescape

# Basic profanity list (expand as needed)
PROFANITY = {"badword", "anotherbadword", "testword"}

PROMPT_INJECTION_PATTERNS = [
    r"ignore (all|previous)? ?instructions",
    r"do as i say",
    r"disregard (all|previous)? ?instructions",
    r"you are now",
    r"pretend to be",
    r"act as",
    r"system:"
]

SQL_PATTERNS = [
    r"(;|\b)(drop|select|insert|delete|update|alter|create|truncate|exec|union|--|#|\bOR\b|\bAND\b)\b"
]

SCRIPT_TAG_RE = re.compile(r"<script.*?>.*?</script>", re.IGNORECASE | re.DOTALL)
HTML_TAG_RE = re.compile(r"<.*?>", re.DOTALL)


def sanitize_input(text: str) -> str:
    text = unescape(text)
    text = SCRIPT_TAG_RE.sub("", text)
    text = HTML_TAG_RE.sub("", text)
    return text.strip()

def contains_profanity(text: str) -> bool:
    words = set(re.findall(r"\w+", text.lower()))
    return not PROFANITY.isdisjoint(words)

def contains_prompt_injection(text: str) -> bool:
    for pat in PROMPT_INJECTION_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def contains_sql_injection(text: str) -> bool:
    for pat in SQL_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False

def validate_length(text: str, max_length: int = 500) -> bool:
    return len(text) <= max_length
