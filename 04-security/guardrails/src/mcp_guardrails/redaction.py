# ABOUTME: Secret/PII redaction for tool inputs and results before they are logged or re-shared.
# ABOUTME: Default-deny on known secret shapes (MCP01); a Presidio backend can be added later.
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Redaction:
    """A single redaction that was applied.

    Args:
        kind: The class of value redacted (email, api_key, github_token, aws_access_key, bearer_token).
        placeholder: The token substituted in place of the value.
    """

    kind: str
    placeholder: str


@dataclass(frozen=True)
class RedactionResult:
    """The redacted text plus the list of redactions applied."""

    text: str
    redactions: list[Redaction]


# Order matters: more specific token shapes run before the generic ones so they win the match.
_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("github_token", "[REDACTED_GITHUB_TOKEN]", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("aws_access_key", "[REDACTED_AWS_KEY]", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("api_key", "[REDACTED_API_KEY]", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("bearer_token", "Bearer [REDACTED_TOKEN]", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]+", re.I)),
    (
        "email",
        "[REDACTED_EMAIL]",
        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    ),
]


def redact(text: str) -> RedactionResult:
    """Redact known secret and PII shapes from text.

    Returns the redacted text and the redactions applied. Clean text is returned unchanged with
    an empty redaction list. Redaction is applied to a copy; the raw value never survives in the
    output, so a secret passed through a tool does not reach logs or a downstream stage.
    """
    redactions: list[Redaction] = []
    redacted = text
    for kind, placeholder, pattern in _RULES:
        if pattern.search(redacted):
            redacted = pattern.sub(placeholder, redacted)
            redactions.append(Redaction(kind, placeholder))
    return RedactionResult(redacted, redactions)
