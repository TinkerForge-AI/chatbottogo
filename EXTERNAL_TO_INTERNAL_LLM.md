## LLM Provider Architecture

Currently, `GoogleAIProvider` is the chosen LLM for our system. The backend routes requests through this provider for all chat completions. In the future, once stakeholders approve, we plan to migrate to a self-hosted open-source LLM (e.g., Phi-3, StarCoder).

### Steps to Replace `GoogleAIProvider` with an Internal LLM Provider

#### 1. Identify All Usage of `GoogleAIProvider`
- **backend/providers/google_ai.py**: Main implementation of the provider.
- **backend/providers/__init__.py**: Imports and exposes the provider.
- **backend/main.py**: Where the provider is instantiated and used for chat endpoints.
- **backend/preprocessor/pipeline.py**: Any pipeline logic that calls the provider.
- **backend/tests/**: Any tests that mock or use `GoogleAIProvider`.

#### 2. Create Your Internal Provider
- Add a new file: `backend/providers/internal_llm.py`
  - Implement a class (e.g., `InternalLLMProvider`) with the same interface as `GoogleAIProvider`.
  - Example:
    ```python
    class InternalLLMProvider:
        def __init__(self, ...):
            # Initialize connection to your LLM server
        def chat(self, prompt: str, **kwargs):
            # Call your internal LLM and return the response
    ```

#### 3. Update Provider Imports
- **backend/providers/__init__.py**:
  - Import and expose `InternalLLMProvider`.
  - Optionally, use an environment variable or config to switch providers.

- **backend/main.py**:
  - Replace all instances of `GoogleAIProvider` with `InternalLLMProvider`.
  - If using dependency injection, update the provider factory.

#### 4. Update Pipeline Logic
- **backend/preprocessor/pipeline.py**:
  - Ensure any direct calls to `GoogleAIProvider` are replaced with the new provider.

#### 5. Update Tests
- **backend/tests/**:
  - Update or add tests for `InternalLLMProvider`.
  - Mock responses from your internal LLM as needed.

#### 6. Configuration
- Add configuration options to select the provider (e.g., via `.env` or `config.py`).
- Example:
  ```python
  PROVIDER = os.getenv("LLM_PROVIDER", "google")
  if PROVIDER == "internal":
      provider = InternalLLMProvider(...)
  else:
      provider = GoogleAIProvider(...)
  ```

#### 7. Validate Integration
- Run all unit and e2e tests to ensure the new provider works as expected.
- Test edge cases and performance with your internal LLM.

#### 8. Document the Change
- Update this README and any relevant docs to reflect the new provider.

---

**Summary Table**

| File/Location                        | Action Required                                  |
|--------------------------------------|--------------------------------------------------|
| backend/providers/google_ai.py       | Reference for interface                          |
| backend/providers/internal_llm.py    | Implement new provider                           |
| backend/providers/__init__.py        | Import/expose new provider                       |
| backend/main.py                      | Switch provider usage                            |
| backend/preprocessor/pipeline.py     | Update provider calls                            |
| backend/tests/                       | Update/add tests                                 |
| .env / config.py                     | Add provider selection config                    |
| README.md / docs                     | Document migration steps                         |

---

Once these steps are complete, the system will use your internal LLM provider for all chat