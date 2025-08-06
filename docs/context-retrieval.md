# Context File Access & Retrieval

## Features
- Upload files (`.pdf`, `.docx`, `.txt`, `.md`) via `/api/context/upload`
- Extracts and chunks text for keyword search
- Indexes chunks in MongoDB with per-user isolation
- Simple keyword search with relevance scoring via `/api/context/search`
- Path traversal and extension checks for security

## API Usage
### Upload
`POST /api/context/upload`
- Form fields: `user_id`, `file` (single file)
- Only allowed extensions: pdf, docx, txt, md
- Returns: `{ status: "ok", chunks_indexed: N }`

### Search
`POST /api/context/search`
- JSON body: `{ "user_id": ..., "query": ... }`
- Returns: `{ results: [ {text, relevance, ...}, ... ] }`

## Security
- Only allows uploads to a dedicated folder
- Prevents path traversal by sanitizing filenames
- Rejects unsupported file types

## Implementation
- See `/backend/context/` for extraction and indexing logic
- See `/tests/test_context.py` for upload/search tests

## Extending
- Add more file types by extending `extract_text` in `file_utils.py`
- Improve search with embeddings or fulltext search as needed
