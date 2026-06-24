# ABOUTME: The token-passthrough anti-pattern vs the correct token-exchange flow.
# ABOUTME: Passthrough forwards a client token downstream (forbidden); exchange mints a new audience.
from __future__ import annotations

from mcp_oauth_demo.authz import AuthorizationServer, Token
from mcp_oauth_demo.resource_server import ResourceServer, ValidationResult


class TokenPassthroughForbidden(RuntimeError):
    """Raised by a conforming gateway that is asked to forward an inbound token downstream."""


def gateway_forward(token: Token, *, downstream_uri: str) -> None:
    """Model the structural prohibition: a conforming gateway refuses to forward an inbound token.

    The MCP authorization spec forbids token passthrough as an act, independent of whether the
    audience happens to match. A correct gateway never forwards the client's token to a downstream
    server; it performs token exchange instead. This function therefore always raises, encoding the
    rule as a rule rather than relying on a downstream audience check to catch it.
    """
    raise TokenPassthroughForbidden(
        f"refusing to forward an inbound token to {downstream_uri}; use token exchange (RFC 8707)"
    )


def attempt_passthrough(token: Token, *, downstream: ResourceServer, now: int) -> ValidationResult:
    """Demonstrate the consequence of passthrough if a non-conforming gateway did forward the token.

    The downstream rejects it on audience mismatch because the token was minted for a different
    server. This shows the side effect; gateway_forward above encodes the structural prohibition.
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
