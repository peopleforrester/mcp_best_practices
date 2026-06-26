# ABOUTME: The FastAPI quiz service: serve questions without answers, score a submission.
# ABOUTME: Models the controls the portfolio teaches: strict CSP + headers, body cap, rate limit,
# ABOUTME: structured request logging, env-gated OpenTelemetry, and the live commit at /health.
from __future__ import annotations

import os
import time
from collections.abc import Awaitable, Callable
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from mcp_quiz.bank import load_bank
from mcp_quiz.models import Question, QuestionView, ScoreResult, SubmitRequest
from mcp_quiz.scoring import score_exam

_STATIC_DIR = Path(__file__).parent / "static"
_INDEX_HTML = (_STATIC_DIR / "index.html").read_text()

# The live git commit, so /health answers "what is actually running". Railway's GitHub-connected
# deploys set RAILWAY_GIT_COMMIT_SHA automatically; a manual GIT_SHA var covers a CLI deploy; else dev.
GIT_SHA = (os.environ.get("RAILWAY_GIT_COMMIT_SHA") or os.environ.get("GIT_SHA") or "dev")[:12]

_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")
_STRICT_CSP = "default-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"


class BodySizeLimitMiddleware:
    """Cap the request body at the ASGI layer by buffering it under a hard ceiling, then replaying it.

    A Content-Length header check alone is bypassable: a Transfer-Encoding: chunked request carries no
    Content-Length, so the body would be buffered unbounded before any handler runs. This reads the
    incoming stream chunk by chunk and stops the moment the running total crosses the limit, so memory
    is bounded by the cap itself (max_bytes + one chunk) regardless of what length the client declared.
    A within-limit body is replayed to the app as a single request event; an over-limit body never
    reaches the app at all, it gets a 413. Raising through the inner stack is avoided on purpose: the
    BaseHTTPMiddleware guard downstream rewrites a receive-side exception into a 400, so the limit is
    enforced here, before that stack, instead.
    """

    def __init__(self, app: object, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: dict, receive: object, send: object) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)  # type: ignore[operator]
            return

        body = b""
        more_body = True
        while more_body:
            message = await receive()  # type: ignore[operator]
            if message["type"] != "http.request":
                break
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
            if len(body) > self.max_bytes:
                response = JSONResponse({"detail": "request body too large"}, status_code=413)
                await response(scope, receive, send)  # type: ignore[arg-type]
                return

        replayed = False

        async def replay() -> dict:
            nonlocal replayed
            if not replayed:
                replayed = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()  # type: ignore[operator]

        await self.app(scope, replay, send)  # type: ignore[operator]

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
_log = structlog.get_logger("mcp_quiz")


def _apply_security_headers(response: Response, path: str) -> Response:
    """Set security headers on a response; the strict CSP is skipped for the docs UI paths."""
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
    if not path.startswith(_DOCS_PATHS):
        response.headers.setdefault("Content-Security-Policy", _STRICT_CSP)
    return response


def _configure_telemetry(app: FastAPI) -> None:
    """Instrument the app with OpenTelemetry when an OTLP endpoint is configured; otherwise no-op.

    Production sets OTEL_EXPORTER_OTLP_ENDPOINT to point at a collector; locally and in tests it is
    unset, so there is no exporter and no overhead. Imports are local so the SDK loads only when used.
    """
    if not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)


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
    _configure_telemetry(app)

    hits: dict[str, list[float]] = {}

    @app.middleware("http")
    async def guard(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        path = request.url.path
        # Behind Railway's edge, request.client.host is the proxy for every visitor, so keying the
        # limiter on it throttles everyone into one bucket and lets an IP-rotating attacker past. The
        # platform edge is a trusted hop, so use the left-most X-Forwarded-For entry (the real client).
        # Demo-grade: a forgeable header is acceptable only because the one trusted hop sets it; in
        # production the rate limit belongs at the edge.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            client = forwarded.split(",")[0].strip()
        else:
            client = request.client.host if request.client else "unknown"
        start = time.monotonic()

        def finish(response: Response) -> Response:
            _apply_security_headers(response, path)
            _log.info(
                "request",
                method=request.method,
                path=path,
                status=response.status_code,
                duration_ms=round((time.monotonic() - start) * 1000, 1),
                commit=GIT_SHA,
            )
            return response

        now = time.monotonic()
        recent = [t for t in hits.get(client, []) if now - t < rate_window_s]
        if len(recent) >= rate_limit:
            return finish(JSONResponse({"detail": "rate limit exceeded"}, status_code=429))
        recent.append(now)
        hits[client] = recent

        return finish(await call_next(request))

    # Added last so it is the outermost middleware: it counts the raw request stream before the guard
    # or any handler can buffer it, which is what makes the cap hold for chunked (no Content-Length)
    # uploads. A rejected oversized body returns a bare 413 without the per-response security headers,
    # which is acceptable for an abort that never reaches application logic.
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=max_body_bytes)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        """Serve the browser quiz frontend (markup; styles and script load from /static)."""
        return _INDEX_HTML

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "commit": GIT_SHA}

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
