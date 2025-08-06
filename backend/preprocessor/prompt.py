import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "../templates")
TEMPLATES = {
    "technical": "technical.txt",
    "code": "code.txt",
    "qa": "qa.txt",
    "report": "report.txt"
}

def build_prompt(user_message: str, query_type: str) -> str:
    fname = TEMPLATES.get(query_type, "qa.txt")
    path = os.path.join(TEMPLATE_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{user_message}", user_message)

def count_tokens(text: str) -> int:
    # Simple token count: split by whitespace (for demo, not LLM-accurate)
    return len(text.split())

def trim_to_max_tokens(text: str, max_tokens: int) -> str:
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return " ".join(tokens[:max_tokens])
