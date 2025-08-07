"""
Backend API for Modular LLM Chatbot
===================================

This FastAPI backend provides endpoints for:
- Chat messaging with preprocessing, prompt framing, rate limiting, and context window management
- Conversation history retrieval
- File upload for user context (PDF, DOCX, TXT, MD)
- Context chunking, indexing, and secure search
- Health and status checks

Pipeline Overview:
------------------
1. /api/chat/message: User message is sanitized, checked for profanity/injection, rate-limited, framed, and stored.
2. /api/context/upload: User uploads a file. File type is validated, path traversal is prevented, text is extracted, chunked, and indexed for search.
3. /api/context/search: User queries their indexed context. Results are cleaned of internal DB fields and returned.
4. /api/chat/history: Retrieve conversation history for a user.

Security Practices:
-------------------
- Only specific file types allowed for upload (PDF, DOCX, TXT, MD)
- Path traversal protection on file uploads
- Rate limiting per user (10 messages/minute)
- Input sanitization and injection/profanity detection
- All endpoints return sanitized, non-leaky error messages
- MongoDB ObjectIds and internal fields are stripped from API responses

See /docs/context-retrieval.md for more details on the context system.
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request, Response, status, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, ASCENDING
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from typing import List, Optional
from starlette.requests import Request as StarletteRequest
from fastapi import UploadFile, File, Form
from backend.context.file_utils import allowed_file, extract_text
from backend.context.indexer import chunk_text, index_chunks, search_chunks



# Pydantic Settings for env vars

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017/llmchatbot"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    GEMINI_API_KEY: str = ""
    model_config = ConfigDict(env_file=".env", extra="allow")

settings = Settings()


app = FastAPI()

# File upload endpoint (must be after app is defined)
@app.post("/api/context/upload")
async def upload_context_file(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Upload a context file (PDF, DOCX, TXT, MD) for a user.
    - Validates file type and prevents path traversal.
    - Enforces file size limit (10MB).
    - Saves file with unique name to prevent overwrites.
    - Extracts text, chunks, and indexes for later search.
    - Returns number of chunks indexed.
    """
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if not allowed_file(file.filename):
        logger.warning(f"Rejected upload: {file.filename} (user={user_id}) - unsupported type")
        return JSONResponse(status_code=400, content={"detail": "Unsupported file type"})
    # Prevent path traversal and ensure unique filename
    orig_filename = os.path.basename(file.filename)
    unique_filename = f"{user_id}_{int(datetime.utcnow().timestamp())}_{orig_filename}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        logger.warning(f"Rejected upload: {orig_filename} (user={user_id}) - file too large")
        return JSONResponse(status_code=400, content={"detail": "File too large (max 10MB)"})
    try:
        with open(save_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return JSONResponse(status_code=500, content={"detail": f"Failed to save file: {e}"})
    try:
        text = extract_text(orig_filename, contents)
    except Exception as e:
        logger.warning(f"Extraction failed for {orig_filename} (user={user_id}): {e}")
        return JSONResponse(status_code=400, content={"detail": f"Extraction failed: {e}"})
    try:
        chunks = chunk_text(text)
        index_chunks(chunks, unique_filename, user_id, context_collection)
    except Exception as e:
        logger.error(f"Indexing failed for {unique_filename} (user={user_id}): {e}")
        return JSONResponse(status_code=500, content={"detail": f"Indexing failed: {e}"})
    logger.info(f"File uploaded and indexed: {unique_filename} (user={user_id}, chunks={len(chunks)})")
    return {"status": "ok", "chunks_indexed": len(chunks)}

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Search endpoint
@app.post("/api/context/search")
async def search_context(user_id: str = Body(...), query: str = Body(...)):
    """
    Search indexed context chunks for a user.
    - Returns a list of matching chunks (internal DB fields removed).
    """
    try:
        results = search_chunks(query, user_id, context_collection)
        def clean(doc):
            d = dict(doc)
            d.pop('_id', None)
            return d
        clean_results = [clean(r) for r in results]
        return {"results": clean_results}
    except Exception as e:
        logger.error(f"Context search error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Context search failed"})

# Logging config
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# MongoDB client and ensure indexes
client = MongoClient(settings.MONGODB_URI)
db = client.get_database()
convos = db.conversations
convos.create_index([("user_id", ASCENDING)])
convos.create_index([("updated_at", ASCENDING)])

# Secure upload folder (must be after os and db are defined)
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
context_collection = db.context_chunks

# In-memory rate limit tracker: {user_id: [timestamps]}
from collections import defaultdict, deque
import time
rate_limit_window = 60  # seconds
rate_limit_count = 10
user_message_times = defaultdict(lambda: deque(maxlen=rate_limit_count))

# Import preprocessor
from backend.preprocessor.core import (
    sanitize_input, contains_profanity, contains_prompt_injection, contains_sql_injection, validate_length
)
from backend.preprocessor.prompt import build_prompt, count_tokens, trim_to_max_tokens

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url} at {datetime.utcnow().isoformat()}")
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Error: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    logger.info(f"Response: {response.status_code} at {datetime.utcnow().isoformat()}")
    return response

# Error handler for 422
# Error handler for 422
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# --- Conversation Models ---
class Message(BaseModel):
    text: str = Field(..., max_length=500)
    timestamp: Optional[str] = None

class Conversation(BaseModel):
    user_id: str
    messages: List[Message] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# --- Rate Limiting Helper ---
def check_rate_limit(user_id: str) -> bool:
    now = time.time()
    dq = user_message_times[user_id]
    # Remove timestamps outside window
    while dq and now - dq[0] > rate_limit_window:
        dq.popleft()
    if len(dq) >= rate_limit_count:
        return False
    dq.append(now)
    return True
@app.post("/api/chat/message")
async def post_message(request: StarletteRequest, body: dict = Body(...)):
    """
    Process a user chat message:
    - Sanitizes input, checks for profanity/injection, rate-limits, trims to context window, frames prompt.
    - Stores message in conversation history.
    - Returns the framed prompt and query type.
    """
    user_id = body.get("user_id")
    text = body.get("text")
    query_type = body.get("query_type", "qa")
    if not user_id or not text:
        return JSONResponse(status_code=400, content={"detail": "user_id and text required"})
    # If this is the first message in a new conversation, clear rate-limit history
    if convos.find_one({"user_id": user_id}) is None:
        user_message_times[user_id].clear()
    sanitized = sanitize_input(text)
    if contains_profanity(sanitized):
        logger.warning(f"Profanity detected from user {user_id}")
        return JSONResponse(status_code=400, content={"detail": "Profanity detected"})
    if contains_prompt_injection(sanitized):
        logger.warning(f"Prompt injection detected from user {user_id}")
        return JSONResponse(status_code=400, content={"detail": "Prompt injection detected"})
    if contains_sql_injection(sanitized):
        logger.warning(f"SQL injection detected from user {user_id}")
        return JSONResponse(status_code=400, content={"detail": "Possible SQL injection detected"})
    if not check_rate_limit(user_id):
        logger.warning(f"Rate limit exceeded for user {user_id}")
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded (10 messages/min)"})
    max_tokens = 200
    # Compute original token count for echo logic
    original_tokens = len(sanitized.split())
    sanitized_trimmed = trim_to_max_tokens(sanitized, max_tokens)
    prompt = build_prompt(sanitized_trimmed, query_type)
    while not validate_length(prompt, 500) and len(sanitized_trimmed.split()) > 1:
        sanitized_trimmed = trim_to_max_tokens(sanitized_trimmed, len(sanitized_trimmed.split()) - 1)
        prompt = build_prompt(sanitized_trimmed, query_type)
    if not validate_length(prompt, 500):
        logger.warning(f"Message too long after framing/context for user {user_id}")
        return JSONResponse(status_code=400, content={"detail": "Message too long (max 500) after framing/context"})
    now = datetime.utcnow().isoformat()
    # Store sanitized and trimmed user text for conversation history
    msg_to_store = sanitized_trimmed
    msg = {"text": msg_to_store, "timestamp": now, "query_type": query_type}
    try:
        convo = convos.find_one({"user_id": user_id})
        if convo:
            convos.update_one({"user_id": user_id}, {"$push": {"messages": msg}, "$set": {"updated_at": now}})
        else:
            convos.insert_one({"user_id": user_id, "messages": [msg], "created_at": now, "updated_at": now})
    except Exception as e:
        logger.error(f"Failed to update conversation for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Failed to update conversation"})

    # Call the LLM using GoogleAIProvider
    try:
        from backend.providers.googleai import GoogleAIProvider
        import markdown as md
        # You may want to cache this instance in production
        google_llm = GoogleAIProvider()
        llm_response = google_llm.generate(prompt)
        # Convert markdown to HTML for frontend rendering
        llm_html = md.markdown(llm_response, extensions=["extra", "codehilite", "nl2br"])
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        llm_html = "[Error: LLM unavailable]"

    return {"response": llm_html, "query_type": query_type}

@app.get("/api/chat/history")
def get_history(user_id: str):
    """
    Retrieve conversation history for a user.
    """
    try:
        convo = convos.find_one({"user_id": user_id})
        if not convo:
            return {"user_id": user_id, "messages": []}
        return {"user_id": user_id, "messages": convo.get("messages", [])}
    except Exception as e:
        logger.error(f"Failed to retrieve history for user {user_id}: {e}")
        return JSONResponse(status_code=500, content={"detail": "Failed to retrieve history"})

@app.get("/api/health")
def health_check():
    """
    Health check for API and DB connection.
    """
    try:
        db.test.insert_one({"status": "ok"})
        result = db.test.find_one({"status": "ok"})
        db.test.delete_many({"status": "ok"})
        if result:
            return {"status": "ok", "db": "connected"}
        else:
            return {"status": "fail", "db": "not connected"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "fail", "error": str(e)}

@app.get("/api/status")
def get_status():
    """
    Returns API running status and current timestamp.
    """
    return {"status": "running", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/echo")
async def echo(request: Request):
    """
    Echoes back the received JSON payload. For testing only.
    """
    try:
        data = await request.json()
    except Exception:
        logger.warning("Invalid JSON received at /api/echo")
        return JSONResponse(status_code=400, content={"detail": "Invalid JSON"})
    return {"echo": data}
