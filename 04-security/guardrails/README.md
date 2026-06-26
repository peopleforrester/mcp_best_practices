<!-- ABOUTME: Guardrails for MCP traffic: injection detection and secret/PII redaction.
ABOUTME: Framework-independent functions; the shipped middleware applies them to tool results (egress). -->

# MCP Guardrails

Content-level defenses applied to the text that crosses an MCP boundary: arguments going into a
tool, and results coming back from one. The policy gateway decides allow/deny on structure
(allowlist, consent, rules); guardrails inspect and sanitize content. Together they implement the
NSA CSI principle of treating every tool and model output as untrusted input to the next stage
(recommendation 7).

## Modules

- **`detectors.py`** : `scan_for_injection(text)` returns findings for indirect-prompt-injection
  patterns (instruction override, exfiltration-to-URL, system-prompt-leak attempts). Each finding
  carries a category, pattern name, severity, and the matched snippet. This is an advisory signal;
  the gateway decides whether to block, flag, or require confirmation. Mitigates the injection paths
  in the LLM and host threat models (MCP03, MCP06, MCP10).
- **`redaction.py`** : `redact(text)` removes known secret and PII shapes (emails, OpenAI-style API
  keys, GitHub tokens, AWS access keys, Bearer tokens), returning the sanitized text and the list of
  redactions applied. The raw value never survives in the output, so a secret passing through a tool
  does not reach logs or a downstream stage (MCP01, MCP10).

## Scope and honesty

The detectors are heuristics, not a complete injection defense; no such thing exists, which is why
the threat models push the real control to least-privilege tool design and the gateway. The redactor
covers common high-confidence secret shapes by regex. A Presidio backend (named in the research) can
be added later as an alternative redaction engine for broader PII coverage; it is not a default
dependency yet.

## Develop

```bash
cd 04-security/guardrails
uv run pytest -q
uv run ruff check .
```
