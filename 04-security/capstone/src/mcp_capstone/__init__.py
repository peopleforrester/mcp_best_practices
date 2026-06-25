# ABOUTME: The composed security capstone: registry admission + policy gateway + guardrails + audit.
# ABOUTME: Proves the four controls actually compose in one request path, not just in prose.
from mcp_capstone.guardrails_middleware import GuardrailsMiddleware
from mcp_capstone.server import build_capstone_server

__all__ = ["GuardrailsMiddleware", "build_capstone_server"]
