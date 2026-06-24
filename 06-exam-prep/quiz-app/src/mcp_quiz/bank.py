# ABOUTME: Loads and validates the versioned question bank from questions.yaml.
# ABOUTME: Each entry is parsed into a Question, so a malformed bank raises on load (fail fast).
from __future__ import annotations

from pathlib import Path

import yaml

from mcp_quiz.models import Question

_DEFAULT_BANK = Path(__file__).parent / "questions.yaml"


def load_bank(path: Path | None = None) -> list[Question]:
    """Load the question bank from YAML and validate every entry."""
    source = path or _DEFAULT_BANK
    data = yaml.safe_load(source.read_text())
    return [Question(**entry) for entry in data["questions"]]
