# ABOUTME: Public API for the MCP exam quiz app: models, bank loader, scoring, and the FastAPI factory.
# ABOUTME: Scoring is a pure function; the bank is validated on load so a bad question fails fast.
from mcp_quiz.bank import load_bank
from mcp_quiz.models import Question, QuestionView, ScoreResult, SubmitRequest
from mcp_quiz.scoring import score_exam

__all__ = [
    "Question",
    "QuestionView",
    "ScoreResult",
    "SubmitRequest",
    "load_bank",
    "score_exam",
]
