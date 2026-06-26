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


def test_health_endpoint_reports_status_and_commit():
    body = TestClient(create_app()).get("/health").json()
    assert body["status"] == "ok"
    assert "commit" in body  # surfaces the live git SHA (set by the deploy)


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


def test_submit_rejects_an_overlong_answer_value():
    client = TestClient(create_app())
    assert client.post("/exam/submit", json={"answers": {"q1": "x" * 5000}}).status_code == 422


def test_chunked_oversized_body_is_rejected():
    # A Transfer-Encoding: chunked request has no Content-Length; the cap must enforce on the stream.
    client = TestClient(create_app(max_body_bytes=32))

    def streamed_body():
        yield b'{"answers": {"a": "'
        yield b"x" * 200
        yield b'"}}'

    assert client.post("/exam/submit", content=streamed_body()).status_code == 413


def test_rate_limit_is_enforced():
    client = TestClient(create_app(rate_limit=2))
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 429


def test_openapi_schema_never_exposes_answers_or_rationale():
    # The public OpenAPI schema must not advertise answer/rationale fields anywhere; otherwise a client
    # could learn the answer shape from the docs even though /exam strips them at runtime.
    schema = TestClient(create_app()).get("/openapi.json").json()
    components = schema.get("components", {}).get("schemas", {})
    for name, model in components.items():
        props = set(model.get("properties", {}))
        assert "answer" not in props, name
        assert "rationale" not in props, name


def test_rate_limit_buckets_are_evicted_when_over_cap(monkeypatch):
    # A flood of one-shot client ids must not grow the bucket map without bound: once it exceeds the
    # cap, buckets whose timestamps have aged past the window are swept.
    import mcp_quiz.app as appmod

    clock = {"now": 0.0}
    monkeypatch.setattr(appmod.time, "monotonic", lambda: clock["now"])

    app = create_app(rate_window_s=10.0, max_clients=2)
    client = TestClient(app)
    for ip in ("1.1.1.1", "2.2.2.2", "3.3.3.3"):
        client.get("/health", headers={"X-Forwarded-For": ip})
    assert len(app.state.rate_limit_buckets) == 3  # all fresh, nothing to evict yet

    clock["now"] = 1000.0  # age the existing buckets past the window
    client.get("/health", headers={"X-Forwarded-For": "4.4.4.4"})  # trips the sweep (len > cap)
    assert len(app.state.rate_limit_buckets) == 1  # the three stale buckets were evicted


def test_rate_limit_is_keyed_per_client_not_the_shared_proxy():
    # Behind Railway's edge, request.client.host is the proxy for everyone. The limiter must key on
    # the forwarded client, so one visitor cannot consume another's budget (or throttle everyone).
    client = TestClient(create_app(rate_limit=1))
    assert client.get("/health", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert client.get("/health", headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 429
    assert client.get("/health", headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200


def test_rate_limit_keys_on_the_trusted_rightmost_xff_hop():
    # The edge appends the real client IP on the right; the left-most entry is whatever the client sent
    # and is forgeable. The limiter must key on the right-most (trusted) entry, so an attacker rotating
    # the left-most value cannot mint a fresh bucket per request and slip the limit.
    client = TestClient(create_app(rate_limit=1))
    first = client.get("/health", headers={"X-Forwarded-For": "9.9.9.9, 5.5.5.5"})
    second = client.get("/health", headers={"X-Forwarded-For": "8.8.8.8, 5.5.5.5"})
    assert first.status_code == 200
    assert second.status_code == 429  # same trusted hop (5.5.5.5), spoofed left-most ignored
