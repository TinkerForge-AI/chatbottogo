import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from main import app

client = TestClient(app)
USER_ID = "testuser"

@pytest.fixture(autouse=True)
def clear_convo():
    from main import db
    db.conversations.delete_many({"user_id": USER_ID})

def test_technical_prompt():
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "How do I install Python?", "query_type": "technical"})
    assert resp.status_code == 200
    assert resp.json()["query_type"] == "technical"
    assert "technical documentation search" in resp.json()["echo"].lower()

def test_code_prompt():
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "Show me a Python loop", "query_type": "code"})
    assert resp.status_code == 200
    assert resp.json()["query_type"] == "code"
    assert "code assistant" in resp.json()["echo"].lower()

def test_qa_prompt():
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "What is the capital of France?", "query_type": "qa"})
    assert resp.status_code == 200
    assert resp.json()["query_type"] == "qa"
    assert "q&a assistant" in resp.json()["echo"].lower()

def test_report_prompt():
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "Generate a report on sales.", "query_type": "report"})
    assert resp.status_code == 200
    assert resp.json()["query_type"] == "report"
    assert "structured reports" in resp.json()["echo"].lower()

def test_context_window():
    long_text = "word " * 500
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": long_text, "query_type": "qa"})
    assert resp.status_code == 200
    # Should be trimmed to 200 tokens
    assert len(resp.json()["echo"].split()) <= 200
