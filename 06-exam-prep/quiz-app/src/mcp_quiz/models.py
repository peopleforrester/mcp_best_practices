# ABOUTME: Pydantic models for the quiz: a validated Question, a taker-facing view, and score shapes.
# ABOUTME: Question validates that its answer is one of its options, so a bad bank fails on load.
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

Difficulty = Literal["easy", "medium", "hard"]
Cognitive = Literal["recall", "application"]


class Question(BaseModel):
    """One exam question, including the answer key (never served to the taker).

    Item-writing rules from docs/research/spikes/exam-item-writing.md are enforced here so the bank
    cannot silently regress: exactly four distinct options, the answer among them, and a rationale
    substantive enough to explain why the distractors are wrong (not just assert the key).
    """

    id: str
    domain: str
    difficulty: Difficulty
    cognitive: Cognitive
    stem: str
    options: list[str]
    answer: str
    rationale: str

    @model_validator(mode="after")
    def _validate_item(self) -> Question:
        if len(self.options) != 4:
            raise ValueError(f"question {self.id!r} must have exactly four options")
        if len(set(self.options)) != 4:
            raise ValueError(f"question {self.id!r} has duplicate options")
        if self.answer not in self.options:
            raise ValueError(f"answer is not among options for question {self.id!r}")
        if len(self.rationale.strip()) < 40:
            raise ValueError(f"question {self.id!r} rationale is too short to explain the distractors")
        return self

    @property
    def answer_index(self) -> int:
        """Zero-based position (A=0) of the correct answer, for bank-level balance checks."""
        return self.options.index(self.answer)


class QuestionView(BaseModel):
    """The taker-facing view of a question: no answer, no rationale."""

    id: str
    domain: str
    difficulty: Difficulty
    stem: str
    options: list[str]


class SubmitRequest(BaseModel):
    """A submitted exam: a mapping of question id to the chosen option.

    Bounded so an unauthenticated caller cannot post an arbitrarily large object; a real exam has far
    fewer than 500 questions, and the body-size cap in the app is the coarser outer guard.
    """

    answers: dict[str, str] = Field(max_length=500)


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
