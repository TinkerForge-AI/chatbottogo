# Database Schema Documentation

## conversations Collection

Each document represents a user's conversation history.

### Schema
```
{
  "_id": ObjectId,           // MongoDB document ID
  "user_id": string,         // Unique user identifier
  "messages": [              // List of message objects
    {
      "text": string,        // Message content
      "timestamp": string    // ISO timestamp
    }
  ],
  "created_at": string,      // ISO timestamp
  "updated_at": string       // ISO timestamp
}
```

### Indexes
- `user_id` (unique or non-unique, depending on multi-session support)
- `updated_at` (for recent activity queries)

### Notes
- All timestamps are stored as ISO 8601 strings (UTC).
- Messages are validated for max length and required fields.
- Rate limiting is enforced per user (10 messages/minute).

---
See `main.py` for implementation details.
