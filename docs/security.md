# Security Measures Documentation

## Input Preprocessing & Validation
- **HTML/script removal:** All user messages are sanitized to remove HTML tags and script content before storage or processing.
- **Profanity filter:** Messages are checked against a basic word list and rejected if profanity is detected.
- **Prompt injection detection:** Common prompt injection patterns (e.g., "ignore previous instructions") are detected and blocked.
- **SQL injection detection:** Messages are scanned for SQL keywords and patterns; suspicious inputs are rejected.
- **Message length validation:** All messages are limited to 500 characters after sanitization.

## Rate Limiting
- **Per-user rate limit:** 10 messages per minute per user enforced in-memory.

## Unicode & Encoding
- **Unicode safe:** Sanitization and validation routines handle Unicode and edge cases.

## Storage
- **MongoDB indexes:** Indexes on `user_id` and `updated_at` for efficient lookups and to prevent abuse.

## Testing
- Comprehensive tests for XSS, SQL injection, prompt injection, profanity, and Unicode edge cases.

---
See `preprocessor/core.py` and `main.py` for implementation details.
