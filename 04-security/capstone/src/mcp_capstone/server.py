# ABOUTME: The composed capstone server: registry admission gates the build; the policy gateway
# ABOUTME: denies/audits each call; guardrails redact the result. The four controls in one path.
from __future__ import annotations

from collections.abc import Callable

from fastmcp import FastMCP
from mcp_policy_gateway import PolicyEngine, ToolClass
from mcp_policy_gateway.adapter import PolicyMiddleware
from mcp_signed_registry import ServerEntry, SignedRegistry

from mcp_capstone.guardrails_middleware import GuardrailsMiddleware

_CLIENT_ID = "client-a"
_SERVER_ID = "security-capstone"


def build_capstone_server(
    *,
    registry: SignedRegistry,
    registry_entry: ServerEntry,
    consents_for: Callable[[str], frozenset[str]],
    audit_sink: Callable[[dict], None],
    finding_sink: Callable[[object], None] | None = None,
) -> FastMCP:
    """Build a server only if the signed registry admits it, with policy + guardrails in the path.

    The build is gated on provenance: a server whose entry no trusted signer vouches for never starts.
    Once built, every tool call passes through the policy gateway (allowlist + consent + audit) and
    then the guardrails (injection scan + secret/PII redaction of the result).
    """
    admission = registry.admit(registry_entry)
    if not admission.admitted:
        raise RuntimeError(f"capstone server refused admission: {admission.reason}")

    mcp = FastMCP("security-capstone")

    @mcp.tool
    def lookup_record(record_id: str) -> str:
        """Read a record by id (read-only). The 'leaky' record returns secret-shaped text on purpose."""
        if record_id == "leaky":
            return f"record {record_id}: api key sk-abcdef0123456789abcdef0123 owner ada@example.com"
        return f"record {record_id}: status active"

    @mcp.tool
    def delete_record(record_id: str) -> str:
        """Delete a record by id (destructive; requires per-client consent)."""
        return f"deleted record {record_id}"

    engine = PolicyEngine(
        allowlist={(_CLIENT_ID, _SERVER_ID): {"lookup_record", "delete_record"}},
        tool_classes={"lookup_record": ToolClass.READ_ONLY, "delete_record": ToolClass.DESTRUCTIVE},
    )
    # Order is an onion: the policy gateway is outermost, so it denies and audits before the tool runs;
    # the guardrails are innermost, so they sanitize the result on the way back out.
    mcp.add_middleware(
        PolicyMiddleware(
            engine,
            client_id=_CLIENT_ID,
            server_id=_SERVER_ID,
            consents_for=consents_for,
            audit_sink=audit_sink,
        )
    )
    mcp.add_middleware(GuardrailsMiddleware(finding_sink=finding_sink))
    return mcp
