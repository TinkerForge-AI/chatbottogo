# ChatbotToGo Monorepo

This monorepo hosts a modular LLM-powered chatbot:

- **backend/**: FastAPI application (Python 3.11+, MongoDB); request sanitization, injection checks, preprocessing pipeline
- **frontend/**: Vue 3 SPA (TypeScript, Bootstrap 5) with composables (`useCodeHighlight`), components (`ChatUI`, `ContextProvider`)
- **e2e/**: Playwright end-to-end tests for UI workflows

## Setup & Development

1. Clone repository:
   ```bash
   git clone <repo-url>
   cd chatbottogo-2
   ```

2. Backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Testing

### Unit Tests
- **Backend**: pytest
  ```bash
  cd backend
  pytest
  ```
- **Frontend**: Vitest
  ```bash
  cd frontend
  npm test
  ```

### End-to-End Tests
Install Playwright and run tests:
```bash
cd frontend
npx playwright install
npx playwright test
```

## Cleanup & Maintenance
- Remove unused files/directories:
  - `frontend/README.md`
  - `backend/venv/`, `backend/__pycache__/`
- Open issues or pull requests for new features or bug fixes.
