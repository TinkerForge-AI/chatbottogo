# API Documentation

## Endpoints

### GET /api/health
- **Description:** Health check and MongoDB connection test
- **Response:**
  - 200 OK: `{ "status": "ok", "db": "connected" }`
  - 200 OK: `{ "status": "fail", "db": "not connected" }` or `{ "status": "fail", "error": "..." }`

### GET /api/status
- **Description:** Returns server status and current UTC timestamp
- **Response:**
  - 200 OK: `{ "status": "running", "timestamp": "..." }`

### POST /api/echo
- **Description:** Echoes back the JSON payload sent in the request
- **Request Body:** JSON object
- **Response:**
  - 200 OK: `{ "echo": <your_payload> }`
  - 400 Bad Request: `{ "detail": "Invalid JSON" }`

## Error Handling
- All unhandled errors return: `{ "detail": "Internal Server Error" }` with status 500
- Invalid endpoints return 404
- Invalid methods return 405 or 404

## CORS
- Configured to allow requests from the Vue frontend (default: http://localhost:5173)

---
See `main.py` for implementation details.
