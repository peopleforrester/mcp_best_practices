# ABOUTME: An OAuth 2.1 resource server that enforces RFC 8707 audience binding on access tokens.
# ABOUTME: Rejecting a token whose audience is not this server is the confused-deputy defense.
from __future__ import annotations

from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from mcp_oauth_demo.authz import Token, canonical_claims


@dataclass(frozen=True)
class ValidationResult:
    """Whether a token is accepted by a resource server, with the reason."""

    accepted: bool
    reason: str


class ResourceServer:
    """Validates access tokens for one resource (an MCP server acting as OAuth resource server).

    A token is accepted only if its signature verifies under the issuer key, it is not expired,
    the issuer matches, and its audience equals this server's canonical URI (RFC 8707). The
    audience check is what stops a token minted for another server being replayed here.

    Args:
        resource_uri: This server's canonical URI, the expected aud claim.
        issuer_public_key: The issuer's raw Ed25519 public key.
        issuer: The expected iss claim.
    """

    def __init__(self, *, resource_uri: str, issuer_public_key: bytes, issuer: str):
        self.resource_uri = resource_uri
        self._issuer_key = Ed25519PublicKey.from_public_bytes(issuer_public_key)
        self._issuer = issuer

    def validate(self, token: Token, *, now: int) -> ValidationResult:
        """Validate a token at the current time."""
        try:
            self._issuer_key.verify(token.signature, canonical_claims(token.claims))
        except InvalidSignature:
            return ValidationResult(False, "signature invalid: claims do not match the issuer signature")

        if token.claims.get("iss") != self._issuer:
            return ValidationResult(False, "issuer mismatch")
        if token.claims.get("exp", 0) <= now:
            return ValidationResult(False, "token expired")
        # RFC 8707 permits aud to be a single string or an array; this server must be one of them.
        aud = token.claims.get("aud")
        audiences = [aud] if isinstance(aud, str) else list(aud or [])
        if self.resource_uri not in audiences:
            return ValidationResult(
                False,
                f"audience mismatch (RFC 8707): token bound to {audiences}, not {self.resource_uri}",
            )
        return ValidationResult(True, "accepted: valid signature, correct issuer and audience, not expired")
