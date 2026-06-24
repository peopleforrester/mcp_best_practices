# ABOUTME: Pydantic models for the quiz: a validated Question, a taker-facing view, and score shapes.
# ABOUTME: Question validates that its answer is one of its options, so a bad bank fails on load.
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator

Difficulty = Literal["easy", "medium", "hard"]


class Question(BaseModel):
    """One exam question, including the answer key (never served to the taker)."""

    id: str
    domain: str
    difficulty: Difficulty
    stem: str
    options: list[str]
    answer: str
    rationale: str

    @model_validator(mode="after")
    def _answer_must_be_an_option(self) -> Question:
        if self.answer not in self.options:
            raise ValueError(f"answer is not among options for question {self.id!r}")
        if len(self.options) < 2:
            raise ValueError(f"question {self.id!r} needs at least two options")
        return self


class QuestionView(BaseModel):
    """The taker-facing view of a question: no answer, no rationale."""

    id: str
    domain: str
    difficulty: Difficulty
    stem: str
    options: list[str]


class SubmitRequest(BaseModel):
    """A submitted exam: a mapping of question id to the chosen option."""

    answers: dict[str, str]


class DomainScore(BaseModel):
    """Per-domain breakdown of a score."""

    domain: str
    correct: int
    total: int


class ScoreResult(BaseModel):
    """The result of scoring a submission."""

    total: int
    correct: int
    score_pct: float
    by_domain: list[DomainScore]
