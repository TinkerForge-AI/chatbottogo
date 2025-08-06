import logging
from backend.preprocessor.core import sanitize_input
from backend.preprocessor.prompt import build_prompt
from backend.postprocessor.core import postprocess_output
def test_full_chat_flow_verbose(monkeypatch):
    # Patch provider to log prompt and output
    from backend.orchestrator.orchestrator import PROVIDER_REGISTRY
    from backend.providers.googleai import GoogleAIProvider

    class LoggingProvider(GoogleAIProvider):
        def generate(self, prompt, **kwargs):
            logging.info(f"PROMPT SENT TO LLM: {prompt}")
            result = super().generate(prompt, **kwargs)
            logging.info(f"RAW LLM OUTPUT: {result}")
            return result

    PROVIDER_REGISTRY["gemini"] = LoggingProvider
    monkeypatch.setenv("LLM_PROVIDER", "gemini")

    user_input = "<script>alert('x')</script> badword please help!"
    payload = {
        "user_id": USER_ID,
        "text": user_input,
        "query_type": "qa"
    }

    # Step 1: Sanitize input
    sanitized = sanitize_input(user_input)
    logging.info(f"SANITIZED INPUT: {sanitized}")
    # Only HTML/script tags are removed by sanitize_input; profanity is checked separately
    assert "<script>" not in sanitized

    # Step 2: Prompt framing
    prompt = build_prompt(sanitized, "qa")
    logging.info(f"PROMPT: {prompt}")
    assert sanitized in prompt

    # Step 3: API call
    resp = client.post("/api/chat/message", json=payload)
    assert resp.status_code == 400 or resp.status_code == 200
    if resp.status_code == 400:
        assert "Profanity" in resp.json()["detail"]
        return
    data = resp.json()

    # Step 4: Postprocessing
    postprocessed = postprocess_output(data["response"])
    logging.info(f"POSTPROCESSED OUTPUT: {postprocessed}")
    assert isinstance(postprocessed, str)
    assert len(postprocessed) > 0

    # Step 5: Conversation history
    hist_resp = client.get(f"/api/chat/history?user_id={USER_ID}")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert any(sanitized in m["text"] for m in hist["messages"])

import os
import sys
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import app, convos
client = TestClient(app)
USER_ID = "e2euser"

@pytest.fixture(autouse=True)
def clear_convo():
    convos.delete_many({"user_id": USER_ID})

def test_end_to_end_chat_flow(monkeypatch):
    # Patch orchestrator to use MockLLMProvider for deterministic output
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
    from backend.orchestrator.orchestrator import PROVIDER_REGISTRY
    from backend.providers.mock import MockLLMProvider
    canned = "[MOCK] LLM output."
    class DeterministicMock(MockLLMProvider):
        def generate(self, prompt, **kwargs):
            return canned
    PROVIDER_REGISTRY["mock"] = DeterministicMock
    monkeypatch.setenv("LLM_PROVIDER", "mock")
def test_full_chat_flow_verbose(monkeypatch):
    import sys, os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
    from backend.preprocessor.core import sanitize_input
    from backend.preprocessor.prompt import build_prompt
    from backend.postprocessor.core import postprocess_output
    from backend.orchestrator.orchestrator import PROVIDER_REGISTRY
    from backend.providers.googleai import GoogleAIProvider
    import logging
    class LoggingProvider(GoogleAIProvider):
        def generate(self, prompt, **kwargs):
            logging.info(f"PROMPT SENT TO LLM: {prompt}")
            result = super().generate(prompt, **kwargs)
            logging.info(f"RAW LLM OUTPUT: {result}")
            return result
    PROVIDER_REGISTRY["gemini"] = LoggingProvider
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    user_input = "<script>alert('x')</script> badword please help!"
    payload = {
        "user_id": USER_ID,
        "text": user_input,
        "query_type": "qa"
    }
    sanitized = sanitize_input(user_input)
    logging.info(f"SANITIZED INPUT: {sanitized}")
    assert "<script>" not in sanitized
    prompt = build_prompt(sanitized, "qa")
    logging.info(f"PROMPT: {prompt}")
    assert sanitized in prompt
    resp = client.post("/api/chat/message", json=payload)
    assert resp.status_code == 400 or resp.status_code == 200
    if resp.status_code == 400:
        assert "Profanity" in resp.json()["detail"]
        return
    data = resp.json()
    postprocessed = postprocess_output(data["response"])
    logging.info(f"POSTPROCESSED OUTPUT: {postprocessed}")
    assert isinstance(postprocessed, str)
    assert len(postprocessed) > 0
    hist_resp = client.get(f"/api/chat/history?user_id={USER_ID}")
    assert hist_resp.status_code == 200
    hist = hist_resp.json()
    assert any(sanitized in m["text"] for m in hist["messages"])

    # Step 1: Send a message with XSS and profanity
    payload = {
        "user_id": USER_ID,
        "text": "<script>alert('x')</script> badword please help!",
        "query_type": "qa"
    }
    resp = client.post("/api/chat/message", json=payload)
    # Should be blocked for profanity
    assert resp.status_code == 400
    assert "Profanity" in resp.json()["detail"]

    # Step 2: Send a message with XSS only (should be sanitized)
    payload["text"] = "<script>alert('x')</script> How do I install Python?"
    resp = client.post("/api/chat/message", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    # Step 3: Check prompt framing
    assert "q&a assistant" in data["echo"].lower()
    # Step 4: Check output is from MockLLMProvider
    # (In real integration, this would be the LLM output, here it's the prompt)
    # Step 5: Check conversation history
    resp = client.get(f"/api/chat/history?user_id={USER_ID}")
    assert resp.status_code == 200
    history = resp.json()
    assert history["user_id"] == USER_ID
    assert len(history["messages"]) == 1
    assert "q&a assistant" in history["messages"][0]["text"].lower()
