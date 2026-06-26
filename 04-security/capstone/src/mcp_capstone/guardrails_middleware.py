# ABOUTME: FastMCP middleware that runs the guardrails on a tool result before it leaves the server.
# ABOUTME: Scans result text for injection signals and redacts secret/PII shapes (composes with the gateway).
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp_guardrails import redact, scan_for_injection


class GuardrailsMiddleware(Middleware):
    """Sanitize tool results on the way out: flag injection patterns, redact secrets and PII.

    Args:
        finding_sink: Receives each injection finding (default: discard). Wire to a logger or SIEM.
    """

    def __init__(self, *, finding_sink: Callable[[object], None] | None = None):
        self._finding_sink = finding_sink or (lambda _finding: None)

    def _sanitize(self, value: object) -> object:
        """Recursively scan and redact every string reachable in a value, rebuilding the structure.

        Strings are scanned for injection (findings go to the sink) and redacted; dicts, lists, and
        tuples are walked so a secret buried in nested structured output cannot slip past. Other scalar
        types pass through unchanged.
        """
        if isinstance(value, str):
            for finding in scan_for_injection(value):
                self._finding_sink(finding)
            return redact(value).text
        if isinstance(value, dict):
            return {key: self._sanitize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._sanitize(item) for item in value]
        if isinstance(value, tuple):
            return tuple(self._sanitize(item) for item in value)
        return value

    async def on_call_tool(
        self, context: MiddlewareContext, call_next: Callable[[MiddlewareContext], Awaitable[Any]]
    ) -> Any:
        """Forward the call, then scan and redact the returned content."""
        result = await call_next(context)

        for block in getattr(result, "content", None) or []:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                for finding in scan_for_injection(text):
                    self._finding_sink(finding)
                block.text = redact(text).text

        structured = getattr(result, "structured_content", None)
        if isinstance(structured, dict):
            # Rebuild in place so the (possibly model-held) reference stays the same object.
            sanitized = self._sanitize(structured)
            assert isinstance(sanitized, dict)  # a dict in always yields a dict out
            structured.clear()
            structured.update(sanitized)

        return result
