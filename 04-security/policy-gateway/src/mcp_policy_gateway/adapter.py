# ABOUTME: FastMCP middleware that enforces the policy engine on every tool call and audits it.
# ABOUTME: Denies with a clean ToolError; the policy + audit core stays framework-independent.
from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

from mcp_policy_gateway.audit import audit_record
from mcp_policy_gateway.policy import Decision, PolicyEngine, PolicyRequest


def _utc_now() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


class PolicyMiddleware(Middleware):
    """Enforce the policy engine on each tool call and emit a SIEM-ready audit record.

    The middleware translates a FastMCP tool call into a PolicyRequest, evaluates it, writes
    one audit record per decision, and either denies the call with a ToolError or forwards it
    to the upstream. All security logic lives in the framework-independent core; this class is
    only the transport adapter.

    Args:
        engine: The policy decision engine.
        client_id: Identity attributed to the calling client for this connection.
        server_id: Identity of the upstream server whose tools are being gated.
        consents_for: Returns the set of tool names the client has consented to, given a client id.
        audit_sink: Receives each audit record (default: discard). Wire to a logger or SIEM.
        clock: Returns the timestamp string for audit records (injected for testability).
        correlation_ids: Returns a correlation id per call (injected for testability).
    """

    def __init__(
        self,
        engine: PolicyEngine,
        *,
        client_id: str,
        server_id: str,
        consents_for: Callable[[str], frozenset[str]],
        audit_sink: Callable[[dict], None] | None = None,
        clock: Callable[[], str] = _utc_now,
        correlation_ids: Callable[[], str] | None = None,
    ):
        self._engine = engine
        self._client_id = client_id
        self._server_id = server_id
        self._consents_for = consents_for
        self._audit_sink = audit_sink or (lambda _record: None)
        self._clock = clock
        self._correlation_ids = correlation_ids or (lambda: uuid.uuid4().hex)

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        """Evaluate policy for a tool call, audit it, then deny or forward."""
        request = PolicyRequest(
            client_id=self._client_id,
            server_id=self._server_id,
            tool_name=context.message.name,
            arguments=dict(context.message.arguments or {}),
            consents=self._consents_for(self._client_id),
        )
        result = self._engine.evaluate(request)
        self._audit_sink(
            audit_record(
                request,
                result,
                correlation_id=self._correlation_ids(),
                timestamp=self._clock(),
            )
        )
        if result.decision is Decision.DENY:
            raise ToolError(f"policy denied: {result.reason}")
        return await call_next(context)
