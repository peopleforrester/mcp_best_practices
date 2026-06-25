# ABOUTME: The FastAPI quiz service: serve questions without answers, score a submission.
# ABOUTME: create_app builds the app from a bank; module-level app is the uvicorn/Railway entrypoint.
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from mcp_quiz.bank import load_bank
from mcp_quiz.models import Question, QuestionView, ScoreResult, SubmitRequest
from mcp_quiz.scoring import score_exam

_INDEX_HTML = (Path(__file__).parent / "static" / "index.html").read_text()


def create_app(questions: list[Question] | None = None) -> FastAPI:
    """Build the quiz app over a question bank (defaults to the shipped bank)."""
    bank = questions if questions is not None else load_bank()
    app = FastAPI(title="MCP Exam", version="0.1.0")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        """Serve the browser quiz frontend."""
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
