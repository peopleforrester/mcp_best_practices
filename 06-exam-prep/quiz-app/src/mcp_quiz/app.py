# ABOUTME: The FastAPI quiz service: serve questions without answers, score a submission.
# ABOUTME: The public app models the controls the portfolio teaches: strict CSP + security headers,
# ABOUTME: a request-body cap, and a per-client rate limit. create_app params make them testable.
from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from mcp_quiz.bank import load_bank
from mcp_quiz.models import Question, QuestionView, ScoreResult, SubmitRequest
from mcp_quiz.scoring import score_exam

_STATIC_DIR = Path(__file__).parent / "static"
_INDEX_HTML = (_STATIC_DIR / "index.html").read_text()

# The built-in Swagger/ReDoc UIs load assets from a CDN, so the strict CSP is not applied to them.
_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")
_STRICT_CSP = "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"


def _apply_security_headers(response: Response, path: str) -> Response:
    """Set security headers on a response; the strict CSP is skipped for the docs UI paths."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
    if not path.startswith(_DOCS_PATHS):
        response.headers.setdefault("Content-Security-Policy", _STRICT_CSP)
    return response


def create_app(
    questions: list[Question] | None = None,
    *,
    max_body_bytes: int = 64 * 1024,
    rate_limit: int = 120,
    rate_window_s: float = 60.0,
) -> FastAPI:
    """Build the quiz app over a question bank (defaults to the shipped bank).

    The hardening is demo-grade: rate state is in-memory per process and resets on restart, and the
    body cap is a coarse guard. Production would use an edge rate limiter and a shared store.
    """
    bank = questions if questions is not None else load_bank()
    app = FastAPI(title="MCP Exam", version="0.1.0")
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

    hits: dict[str, list[float]] = {}

    @app.middleware("http")
    async def guard(request: Request, call_next):
        path = request.url.path

        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit() and int(content_length) > max_body_bytes:
            return _apply_security_headers(
                JSONResponse({"detail": "request body too large"}, status_code=413), path
            )

        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        recent = [t for t in hits.get(client, []) if now - t < rate_window_s]
        if len(recent) >= rate_limit:
            return _apply_security_headers(
                JSONResponse({"detail": "rate limit exceeded"}, status_code=429), path
            )
        recent.append(now)
        hits[client] = recent

        return _apply_security_headers(await call_next(request), path)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        """Serve the browser quiz frontend (markup; styles and script load from /static)."""
        return _INDEX_HTML

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/exam", response_model=list[QuestionView])
    def get_exam() -> list[QuestionView]:
        """Serve the exam questions without answers or rationales."""
        return [QuestionView(**q.model_dump()) for q in bank]

    @app.post("/exam/submit", response_model=ScoreResult)
    def submit(request: SubmitRequest) -> ScoreResult:
        """Score a submitted exam and return totals plus a per-domain breakdown."""
        return score_exam(bank, request.answers)

    return app


# Entrypoint for `uvicorn mcp_quiz.app:app` (used by the Railway start command).
app = create_app()
