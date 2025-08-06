from .md_utils import validate_and_convert_markdown, detect_code_blocks, add_syntax_highlighting_hints
from .links import validate_urls
from .hallucination import basic_hallucination_detection
from .truncate import truncate_response

def postprocess_output(text: str, context=None, max_length=2048) -> str:
    # Validate and convert markdown
    html = validate_and_convert_markdown(text)
    # Add syntax highlighting hints
    text = add_syntax_highlighting_hints(text)
    # Truncate
    text = truncate_response(text, max_length)
    # Hallucination detection (if context provided)
    if context:
        halluc = basic_hallucination_detection(text, context)
        if halluc:
            text += "\n\n[Warning: Possible hallucinated content detected!]"
    return text
