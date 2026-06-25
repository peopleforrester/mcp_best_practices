# ABOUTME: SIEM-ready audit record for a policy decision (NSA CSI rec 8: log every invocation).
# ABOUTME: Arguments are fingerprinted with sha256, never logged in plaintext (MCP01 mitigation).
from __future__ import annotations

import hashlib
import json

from mcp_policy_gateway.policy import PolicyRequest, PolicyResult


def arguments_fingerprint(arguments: dict) -> str:
    """Return a sha256 hex digest of the arguments.

    Canonicalizes with sorted keys so the digest is stable across argument ordering.
    The raw arguments are never emitted, so secrets passed as tool arguments do not
    leak into logs or a SIEM.
    """
    # No default= coercion: MCP tool arguments are JSON, so a non-serializable value is a real error
    # and must fail loudly rather than hash to a non-deterministic str() that defeats SIEM correlation.
    canonical = json.dumps(arguments, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audit_record(
    request: PolicyRequest,
    result: PolicyResult,
    *,
    correlation_id: str,
    timestamp: str,
) -> dict:
    """Build a structured audit record for one policy decision.

    Args:
        request: The evaluated request.
        result: The decision the engine returned.
        correlation_id: Trace id tying this record to the originating client turn
            (W3C Trace Context in the RC, SEP-414).
        timestamp: ISO-8601 timestamp, supplied by the caller for testability.

    Returns:
        A JSON-serializable dict suitable for emission to a SIEM. Contains a fingerprint
        of the arguments, not the arguments themselves.
    """
    return {
        "timestamp": timestamp,
        "correlation_id": correlation_id,
        "client_id": request.client_id,
        "server_id": request.server_id,
        "tool": request.tool_name,
        "tool_class": result.tool_class.value,
        "decision": result.decision.value,
        "reason": result.reason,
        "matched_rule": result.matched_rule,
        "arguments_sha256": arguments_fingerprint(request.arguments),
    }
