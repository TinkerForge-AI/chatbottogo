def truncate_response(text: str, max_length: int = 2048) -> str:
    """
    Truncates the response to a maximum length (in characters).
    """
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text
