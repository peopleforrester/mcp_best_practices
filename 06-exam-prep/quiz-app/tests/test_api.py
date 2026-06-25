# ABOUTME: Tests the FastAPI surface: /exam hides answers, /exam/submit scores, and the hardening.
# ABOUTME: Covers security headers, the strict CSP (and its docs exemption), body cap, and rate limit.
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


def test_submit_ignores_unknown_question_ids():
    client = TestClient(create_app())
    response = client.post("/exam/submit", json={"answers": {"does-not-exist": "whatever"}})
    assert response.status_code == 200
    assert response.json()["correct"] == 0


def test_submit_rejects_oversized_answer_map():
    client = TestClient(create_app())
    answers = {f"q{i}": "x" for i in range(501)}  # over the model's 500-entry cap
    assert client.post("/exam/submit", json={"answers": answers}).status_code == 422


def test_health_endpoint():
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok"}


def test_root_serves_the_browser_quiz():
    response = TestClient(create_app()).get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "MCP Exam" in response.text
    assert "/static/app.js" in response.text
    assert "/static/styles.css" in response.text


def test_frontend_script_builds_dom_without_innerhtml():
    # XSS-safety guard on the actual script asset: createElement/textContent, never .innerHTML.
    js = TestClient(create_app()).get("/static/app.js").text
    assert ".innerHTML" not in js
    assert "createElement" in js


def test_security_headers_present():
    response = TestClient(create_app()).get("/exam")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "default-src 'self'" in response.headers["content-security-policy"]


def test_strict_csp_is_exempted_on_docs_assets():
    # The Swagger UI loads CDN assets, so the strict CSP is not applied there, but other headers are.
    response = TestClient(create_app()).get("/openapi.json")
    assert "content-security-policy" not in response.headers
    assert response.headers["x-content-type-options"] == "nosniff"


def test_oversized_request_body_is_rejected():
    client = TestClient(create_app(max_body_bytes=10))
    assert client.post("/exam/submit", json={"answers": {"a": "bbbbbbb"}}).status_code == 413


def test_rate_limit_is_enforced():
    client = TestClient(create_app(rate_limit=2))
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 429
