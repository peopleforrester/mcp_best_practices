# ABOUTME: Secret/PII redaction for text such as tool results before it is logged or re-shared.
# ABOUTME: Best-effort on known secret shapes (MCP01), not exhaustive; a Presidio backend can be added.
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
# This is a best-effort set of high-confidence shapes, not an exhaustive secret scanner. Shapes not
# listed here (Slack, Google, generic high-entropy strings) pass through; wire Presidio for breadth.
_RULES: list[tuple[str, str, re.Pattern[str]]] = [
    ("pem_private_key", "[REDACTED_PRIVATE_KEY]", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github_pat", "[REDACTED_GITHUB_PAT]", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("github_token", "[REDACTED_GITHUB_TOKEN]", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("aws_access_key", "[REDACTED_AWS_KEY]", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("jwt", "[REDACTED_JWT]", re.compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")),
    # Covers legacy sk-<alnum> and modern sk-proj-/sk-svcacct-/sk-admin- (hyphen and underscore allowed).
    ("api_key", "[REDACTED_API_KEY]", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}")),
    ("bearer_token", "Bearer [REDACTED_TOKEN]", re.compile(r"\bBearer\s+[A-Za-z0-9._\-]+", re.I)),
    (
        "email",
        "[REDACTED_EMAIL]",
        # Host and TLD lengths are bounded to avoid pathological backtracking on adversarial input.
        re.compile(r"\b[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,255}\.[A-Za-z]{2,24}\b"),
    ),
]


def redact(text: str) -> RedactionResult:
    """Redact known secret and PII shapes from text.

    Returns the redacted text and the redactions applied, one Redaction per matched occurrence (so a
    repeated kind is reported as many times as it appears). Clean text is returned unchanged with an
    empty redaction list. The raw value never survives in the output, so a secret passing through a
    tool does not reach logs or a downstream stage. The pattern set is best-effort, not exhaustive.
    """
    redactions: list[Redaction] = []
    redacted = text
    for kind, placeholder, pattern in _RULES:
        redacted, count = pattern.subn(placeholder, redacted)
        redactions.extend(Redaction(kind, placeholder) for _ in range(count))
    return RedactionResult(redacted, redactions)
