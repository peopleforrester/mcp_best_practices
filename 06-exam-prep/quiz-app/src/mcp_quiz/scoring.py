# ABOUTME: Pure scoring for a submitted exam: total, percentage, and per-domain breakdown.
# ABOUTME: No IO and no FastAPI, so it is unit-tested directly and reused by the API.
from __future__ import annotations

from mcp_quiz.models import DomainScore, Question, ScoreResult


def score_exam(questions: list[Question], answers: dict[str, str]) -> ScoreResult:
    """Score a submission against the question bank.

    Args:
        questions: The questions that were on the exam.
        answers: A mapping of question id to the chosen option. Missing or wrong answers score zero.

    Returns:
        Totals, a rounded percentage, and a per-domain breakdown sorted by domain.
    """
    per_domain: dict[str, list[int]] = {}
    correct = 0
    for question in questions:
        bucket = per_domain.setdefault(question.domain, [0, 0])
        bucket[1] += 1
        if answers.get(question.id) == question.answer:
            correct += 1
            bucket[0] += 1

    total = len(questions)
    score_pct = round(100 * correct / total, 1) if total else 0.0
    by_domain = [
        DomainScore(domain=domain, correct=c, total=t)
        for domain, (c, t) in sorted(per_domain.items())
    ]
    return ScoreResult(total=total, correct=correct, score_pct=score_pct, by_domain=by_domain)
