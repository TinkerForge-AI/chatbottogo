import os
import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app, db

client = TestClient(app)
USER_ID = "contextuser"

@pytest.fixture(autouse=True)
def clear_context():
    db.context_chunks.delete_many({"user_id": USER_ID})

TEST_FILES = [
    ("test.txt", b"This is a test file. It contains some text for context indexing."),
    ("test.md", b"# Markdown\nThis is a markdown file.\n- Item 1\n- Item 2"),
]

def test_upload_and_search_txt_md():
    for fname, content in TEST_FILES:
        resp = client.post(
            "/api/context/upload",
            data={"user_id": USER_ID},
            files={"file": (fname, io.BytesIO(content), "application/octet-stream")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["chunks_indexed"] > 0
    # Search for a keyword
    resp = client.post(
        "/api/context/search",
        json={"user_id": USER_ID, "query": "markdown"}
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert any("markdown" in r["text"].lower() for r in results)

def test_upload_rejects_bad_extension():
    resp = client.post(
        "/api/context/upload",
        data={"user_id": USER_ID},
        files={"file": ("bad.exe", b"fake", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "Unsupported file type" in resp.json()["detail"]

def test_path_traversal_rejected():
    resp = client.post(
        "/api/context/upload",
        data={"user_id": USER_ID},
        files={"file": ("../evil.txt", b"bad", "application/octet-stream")},
    )
    assert resp.status_code == 200 or resp.status_code == 400
    # Should not write outside upload folder
    assert not os.path.exists(os.path.abspath(os.path.join("../", "evil.txt")))
