# LLM Chatbot Monorepo Setup

## Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB instance (local or remote)

## Backend Setup
1. `cd backend`
2. Create a `.env` file with:
   ```
   MONGODB_URI=mongodb://localhost:27017/llmchatbot
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the FastAPI server:
   ```
   uvicorn main:app --reload
   ```

## Frontend Setup
1. `cd frontend`
2. Install dependencies:
   ```
   npm install
   ```
3. Run the dev server:
   ```
   npm run dev
   ```

## Testing
- Backend tests: `pytest ../tests`
- Health check: Visit `http://localhost:8000/api/health`

## MongoDB
- Ensure MongoDB is running and accessible at the URI in `.env`.

---
See README.md for more details.
