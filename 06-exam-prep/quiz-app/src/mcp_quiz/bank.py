# ABOUTME: Loads and validates the versioned question bank from questions.yaml.
# ABOUTME: Each entry is parsed into a Question, so a malformed bank raises on load (fail fast).
from __future__ import annotations

from pathlib import Path

import yaml

from mcp_quiz.models import Question

_DEFAULT_BANK = Path(__file__).parent / "questions.yaml"


def load_bank(path: Path | None = None) -> list[Question]:
    """Load the question bank from YAML, validate every entry, and enforce unique ids.

    The id uniqueness check is in the loader, not only the test suite, so any bank (not just the
    shipped one) fails fast: a duplicate id would otherwise be double-counted by the scorer.
    """
    source = path or _DEFAULT_BANK
    try:
        data = yaml.safe_load(source.read_text())
    except yaml.YAMLError as exc:
        raise ValueError(f"question bank {source} is not valid YAML: {exc}") from exc
    if not isinstance(data, dict) or "questions" not in data:
        raise ValueError(f"question bank {source} must be a mapping with a 'questions' key")
    entries = data["questions"]
    if not isinstance(entries, list):
        raise ValueError(f"'questions' in {source} must be a list, got {type(entries).__name__}")
    questions = [Question(**entry) for entry in entries]
    ids = [q.id for q in questions]
    duplicates = sorted({qid for qid in ids if ids.count(qid) > 1})
    if duplicates:
        raise ValueError(f"duplicate question ids in bank: {duplicates}")
    return questions
