# ABOUTME: Tests that the shipped question bank loads, validates, and has unique ids.
# ABOUTME: A malformed question (answer not among options) must fail validation.
import pytest
from pydantic import ValidationError

from mcp_quiz.bank import load_bank
from mcp_quiz.models import Question


def test_bank_loads_and_has_enough_questions():
    questions = load_bank()
    assert len(questions) >= 10


def test_question_ids_are_unique():
    ids = [q.id for q in load_bank()]
    assert len(ids) == len(set(ids))


def test_every_question_answer_is_one_of_its_options():
    for q in load_bank():
        assert q.answer in q.options


def test_malformed_question_is_rejected():
    with pytest.raises(ValidationError):
        Question(
            id="bad",
            domain="fundamentals",
            difficulty="easy",
            stem="?",
            options=["a", "b"],
            answer="c",
            rationale="answer not in options",
        )
