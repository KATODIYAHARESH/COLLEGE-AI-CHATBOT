"""API tests for College Helpdesk Chatbot (offline TF-IDF RAG)."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert data["documents"] >= 6


def test_docs_list():
    docs = client.get("/documents").json()
    sources = [d["source"] for d in docs]
    assert "library.md" in sources
    assert "exams.md" in sources


def test_ask_library_hours():
    res = client.post("/ask", json={"question": "What are the library hours?"})
    assert res.status_code == 200
    data = res.json()
    assert "8:00 AM" in data["answer"]
    assert any(s["source"] == "library.md" for s in data["sources"])


def test_ask_unknown_topic_falls_back():
    res = client.post("/ask", json={"question": "What is the capital of Mars?"})
    data = res.json()
    assert "couldn't find" in data["answer"]
    assert data["sources"] == []


def test_add_doc_then_ask():
    res = client.post(
        "/documents",
        json={"title": "Sports", "content": "The annual sports meet is held in December on the college ground."},
    )
    assert res.status_code == 200
    assert res.json()["source"] == "sports.md"
    res = client.post("/ask", json={"question": "When is the annual sports meet?"})
    assert "December" in res.json()["answer"]
