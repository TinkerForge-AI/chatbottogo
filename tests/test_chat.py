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
    # Clear test user's conversation before each test
    from main import db
    db.conversations.delete_many({"user_id": USER_ID})

def test_post_message_and_history():
    # Post a message
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "Hello!"})
    assert resp.status_code == 200
    assert resp.json()["echo"] == "Hello!"
    # Retrieve history
    resp = client.get(f"/api/chat/history?user_id={USER_ID}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == USER_ID
    assert len(data["messages"]) == 1
    assert data["messages"][0]["text"] == "Hello!"

    # Post another message
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "How are you?"})
    assert resp.status_code == 200
    # Retrieve history again
    resp = client.get(f"/api/chat/history?user_id={USER_ID}")
    data = resp.json()
    assert len(data["messages"]) == 2
    assert data["messages"][1]["text"] == "How are you?"

def test_message_validation():
    # Missing user_id
    resp = client.post("/api/chat/message", json={"text": "hi"})
    assert resp.status_code == 400
    # Missing text
    resp = client.post("/api/chat/message", json={"user_id": USER_ID})
    assert resp.status_code == 400
    # Too long
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "x"*501})
    assert resp.status_code == 400

def test_rate_limiting():
    # Reset rate limiter for this user
    from main import user_message_times
    user_message_times[USER_ID].clear()
    # Send 10 messages quickly
    for i in range(10):
        resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": f"msg{i}"})
        assert resp.status_code == 200
    # 11th should fail
    resp = client.post("/api/chat/message", json={"user_id": USER_ID, "text": "overflow"})
    assert resp.status_code == 429
    assert "Rate limit" in resp.json()["detail"]
