# ABOUTME: Tests the FastAPI surface: /exam hides answers, /exam/submit scores a submission.
# ABOUTME: Uses the FastAPI TestClient; no network or running server required.
from fastapi.testclient import TestClient

from mcp_quiz.app import create_app
from mcp_quiz.bank import load_bank


def test_get_exam_hides_answers_and_rationale():
    client = TestClient(create_app())
    response = client.get("/exam")
    assert response.status_code == 200
    first = response.json()[0]
    assert "options" in first
    assert "answer" not in first
    assert "rationale" not in first


def test_submit_scores_a_perfect_submission():
    questions = load_bank()
    client = TestClient(create_app(questions))
    answers = {q.id: q.answer for q in questions}
    response = client.post("/exam/submit", json={"answers": answers})
    assert response.status_code == 200
    assert response.json()["score_pct"] == 100.0


def test_health_endpoint():
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}


def test_root_serves_the_browser_quiz():
    client = TestClient(create_app())
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MCP Exam" in response.text
    assert "/exam" in response.text  # the page calls the API to load and submit


def test_frontend_builds_dom_without_innerhtml():
    # XSS-safety guard: question content is set via textContent/createElement, never assigned to
    # .innerHTML (the sink). Matching the property access avoids tripping on the word in a comment.
    html = TestClient(create_app()).get("/").text
    assert ".innerHTML" not in html
    assert "createElement" in html
