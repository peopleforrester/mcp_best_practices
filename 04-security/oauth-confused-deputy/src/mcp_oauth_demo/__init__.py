# ABOUTME: Public API for the OAuth confused-deputy demo (RFC 8707 audience binding).
# ABOUTME: Shows audience-bound tokens defeating cross-server replay and why passthrough is forbidden.
from mcp_oauth_demo.flows import attempt_passthrough, exchange_token_for_audience
from mcp_oauth_demo.resource_server import ResourceServer, ValidationResult
from mcp_oauth_demo.authz import AuthorizationServer, Token

__all__ = [
    "AuthorizationServer",
    "ResourceServer",
    "Token",
    "ValidationResult",
    "attempt_passthrough",
    "exchange_token_for_audience",
]
