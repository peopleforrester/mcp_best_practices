# ABOUTME: FastMCP middleware that runs the guardrails on a tool result before it leaves the server.
# ABOUTME: Scans result text for injection signals and redacts secret/PII shapes (composes with the gateway).
from __future__ import annotations

from collections.abc import Callable

from fastmcp.server.middleware import Middleware, MiddlewareContext
from mcp_guardrails import redact, scan_for_injection


class GuardrailsMiddleware(Middleware):
    """Sanitize tool results on the way out: flag injection patterns, redact secrets and PII.

    Args:
        finding_sink: Receives each injection finding (default: discard). Wire to a logger or SIEM.
    """

    def __init__(self, *, finding_sink: Callable[[object], None] | None = None):
        self._finding_sink = finding_sink or (lambda _finding: None)

    async def on_call_tool(self, context: MiddlewareContext, call_next):
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
            for key, value in list(structured.items()):
                if isinstance(value, str):
                    structured[key] = redact(value).text

        return result
