import re
from typing import Tuple
import importlib
md_lib = importlib.import_module('markdown')


def validate_and_convert_markdown(text: str) -> str:
    """
    Validates and converts markdown to HTML. Returns HTML string.
    Raises ValueError if invalid markdown is detected.
    """
    try:
        html = md_lib.markdown(text, extensions=["extra", "codehilite"])
        return html
    except Exception as e:
        raise ValueError(f"Invalid markdown: {e}")


def detect_code_blocks(text: str) -> list:
    """
    Detects code blocks and returns a list of (lang, code) tuples.
    """
    code_blocks = re.findall(r'```(\w+)?\n([\s\S]*?)```', text)
    return [(lang or "", code) for lang, code in code_blocks]


def add_syntax_highlighting_hints(text: str) -> str:
    """
    Adds syntax highlighting hints to code blocks if missing.
    """
    def replacer(match):
        lang, code = match.groups()
        lang = lang or "plaintext"
        return f"```{lang}\n{code}```"
    return re.sub(r'```(\w*)\n([\s\S]*?)```', replacer, text)
