
import os
import sys
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from main import app
from orchestrator.orchestrator import LLMOrchestrator

client = TestClient(app)
USER_ID = "googleaiuser"

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="No Gemini API key set")
def test_googleai_prompt_types(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "googleai")
    for query_type, text in [
        ("qa", "What is the capital of Japan?"),
        ("technical", "How do I install Python?"),
        ("code", "Show me a Python for loop."),
        ("report", "Generate a report on sales.")
    ]:
        resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": text, "query_type": query_type})
        assert resp.status_code == 200
        data = resp.json()
        assert data["query_type"] == query_type
        assert isinstance(data["echo"], str)
        assert len(data["echo"]) > 0

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="No Gemini API key set")
def test_googleai_streaming(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "googleai")
    orch = LLMOrchestrator(["googleai"])
    prompt = "List three animals."
    stream = orch.generate(prompt, stream=True, user_id=USER_ID)
    chunks = list(stream)
    # Robust: just check we got some output
    assert sum(len(c) for c in chunks) > 0
