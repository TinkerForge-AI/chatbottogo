# Output Formatting Rules

## Markdown Formatting
- All responses should be valid Markdown.
- Use fenced code blocks for code, with language hints (e.g., ```python).
- Support nested lists, tables, and inline code.
- Use headings, bold, italics, and blockquotes as needed.

## Code Blocks
- Detect and annotate code blocks with language for syntax highlighting.
- If language is missing, default to `plaintext`.

## URL Links
- All URLs must be valid (http/https) and parseable.
- Invalid or malformed URLs should be flagged or removed.

## Hallucination Detection
- Responses should not contain facts not present in the provided context.
- Obvious factual errors or unsupported claims should be flagged.

## Truncation
- Responses must be truncated to a safe length (default: 2048 chars).
- Truncated responses should end with `...`.

## Edge Cases
- Handle nested lists, tables, and code blocks robustly.
- Validate Markdown for complex structures.

---

See `/backend/postprocessor/` for implementation details and `/tests/test_postprocessor.py` for test coverage.
