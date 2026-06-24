# ABOUTME: The token-passthrough anti-pattern vs the correct token-exchange flow.
# ABOUTME: Passthrough forwards a client token downstream (forbidden); exchange mints a new audience.
from __future__ import annotations

from mcp_oauth_demo.authz import AuthorizationServer, Token
from mcp_oauth_demo.resource_server import ResourceServer, ValidationResult


def attempt_passthrough(token: Token, *, downstream: ResourceServer, now: int) -> ValidationResult:
    """Model the forbidden passthrough: forward a client's token to a different downstream server.

    The MCP authorization spec forbids token passthrough. This function performs it anyway so a
    test can demonstrate the consequence: the downstream rejects the token on audience mismatch,
    because the token was minted for a different server. A real gateway must never do this.
    """
    return downstream.validate(token, now=now)


def exchange_token_for_audience(
    auth: AuthorizationServer,
    *,
    subject: str,
    audience: str,
    scope: str,
    expires_at: int,
) -> Token:
    """The correct flow: obtain a fresh token whose audience is the downstream server.

    Instead of forwarding the inbound token, the gateway requests a new token audience-bound to the
    downstream resource (token exchange). The downstream then accepts it because the aud claim matches.
    """
    return auth.issue(subject=subject, audience=audience, scope=scope, expires_at=expires_at)
