# ABOUTME: Public API for the provenance-verifying MCP server registry.
# ABOUTME: Admit a server only if a trusted signer produced a valid signature over its entry.
from mcp_signed_registry.registry import AdmissionResult, ServerEntry, SignedRegistry, Verifier
from mcp_signed_registry.verifiers import Ed25519Verifier

__all__ = [
    "AdmissionResult",
    "Ed25519Verifier",
    "ServerEntry",
    "SignedRegistry",
    "Verifier",
]
