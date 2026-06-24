# ABOUTME: Tests the pure scoring function: totals, percentage, and per-domain breakdown.
# ABOUTME: Scoring has no FastAPI or IO, so it is unit-tested directly.
from mcp_quiz.bank import load_bank
from mcp_quiz.scoring import score_exam


def test_perfect_score():
    questions = load_bank()
    answers = {q.id: q.answer for q in questions}
    result = score_exam(questions, answers)
    assert result.correct == result.total
    assert result.score_pct == 100.0


def test_zero_score():
    questions = load_bank()
    result = score_exam(questions, {})
    assert result.correct == 0
    assert result.score_pct == 0.0


def test_per_domain_totals_sum_to_question_count():
    questions = load_bank()
    answers = {questions[0].id: questions[0].answer}
    result = score_exam(questions, answers)
    assert result.correct == 1
    assert sum(d.total for d in result.by_domain) == len(questions)
