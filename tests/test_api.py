import sys
import os
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from main import app

client = TestClient(app)

def test_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "timestamp" in data

def test_echo():
    payload = {"message": "hello", "value": 123}
    response = client.post("/api/echo", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "echo" in data
    assert data["echo"] == payload

def test_echo_invalid_json():
    response = client.post("/api/echo", data="notjson", headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Invalid JSON"

def test_error_handling():
    # Invalid endpoint
    response = client.get("/api/doesnotexist")
    assert response.status_code == 404
    # Invalid method
    response = client.put("/api/status")
    assert response.status_code in (405, 404)
