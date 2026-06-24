# ABOUTME: Public API for the OAuth confused-deputy demo (RFC 8707 audience binding).
# ABOUTME: Shows audience-bound tokens defeating cross-server replay and why passthrough is forbidden.
from mcp_oauth_demo.authz import AuthorizationServer, Token
from mcp_oauth_demo.flows import (
    TokenPassthroughForbidden,
    attempt_passthrough,
    exchange_token_for_audience,
    gateway_forward,
)
from mcp_oauth_demo.resource_server import ResourceServer, ValidationResult

__all__ = [
    "AuthorizationServer",
    "ResourceServer",
    "Token",
    "TokenPassthroughForbidden",
    "ValidationResult",
    "attempt_passthrough",
    "exchange_token_for_audience",
    "gateway_forward",
]
