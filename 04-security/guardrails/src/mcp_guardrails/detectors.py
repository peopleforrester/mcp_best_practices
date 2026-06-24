# ABOUTME: Heuristic detector for indirect-prompt-injection patterns in untrusted text.
# ABOUTME: Advisory signal for the gateway; treat tool results as untrusted input (NSA CSI rec 7).
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Relative confidence/risk of a detected pattern."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Finding:
    """A single detected injection signal.

    Args:
        category: Coarse class of the signal (instruction_override, exfiltration, prompt_leak).
        pattern: Name of the pattern that matched, for triage.
        severity: Relative risk of the match.
        snippet: The matched text, for human review and audit.
    """

    category: str
    pattern: str
    severity: Severity
    snippet: str


# Each entry: (category, pattern_name, severity, compiled regex). Ordering is not significant;
# all patterns are evaluated so multiple signals in one string are all reported.
_PATTERNS: list[tuple[str, str, Severity, re.Pattern[str]]] = [
    (
        "instruction_override",
        "ignore-previous-instructions",
        Severity.HIGH,
        re.compile(r"\bignore\s+(?:all\s+|any\s+)?(?:previous|prior|above)\s+instructions\b", re.I),
    ),
    (
        "instruction_override",
        "disregard-prior",
        Severity.HIGH,
        re.compile(r"\bdisregard\s+(?:the\s+)?(?:above|prior|previous|earlier)\b", re.I),
    ),
    (
        "instruction_override",
        "new-instructions",
        Severity.MEDIUM,
        re.compile(r"\b(?:new instructions:|you are now\b)", re.I),
    ),
    (
        "exfiltration",
        "send-to-url",
        Severity.HIGH,
        re.compile(r"\b(?:send|post|upload|exfiltrate|forward)\b.{0,40}\bhttps?://", re.I | re.S),
    ),
    (
        "prompt_leak",
        "reveal-system-prompt",
        Severity.MEDIUM,
        re.compile(r"\b(?:reveal|print|repeat|show)\b.{0,30}\b(?:system prompt|your instructions)\b", re.I),
    ),
]


def scan_for_injection(text: str) -> list[Finding]:
    """Scan untrusted text for indirect-prompt-injection patterns.

    Returns a list of findings, one per matched pattern occurrence. An empty list means no
    pattern matched. This is a heuristic advisory signal, not proof of malice; the gateway
    decides how to act on it (block, flag, require confirmation).
    """
    findings: list[Finding] = []
    for category, name, severity, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            findings.append(Finding(category, name, severity, match.group(0)))
    return findings
