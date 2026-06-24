# ABOUTME: A minimal signed access token and authorization server for the OAuth demo.
# ABOUTME: Access tokens carry an audience claim (RFC 8707) and are Ed25519-signed by the issuer.
from __future__ import annotations

import json
from dataclasses import dataclass, replace

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_claims(claims: dict) -> bytes:
    """Return the canonical signed bytes for a claim set (stable key order)."""
    return json.dumps(claims, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class Token:
    """A signed access token: a claim set plus a detached signature over its canonical bytes.

    Claims include iss (issuer), sub (subject), aud (audience, RFC 8707), scope, and exp (epoch).
    """

    claims: dict
    signature: bytes

    @property
    def audience(self) -> str:
        return self.claims["aud"]

    def with_claim(self, key: str, value: object) -> Token:
        """Return a copy with one claim changed and the original signature retained.

        Used to model tampering: the signature no longer matches the mutated claims.
        """
        new_claims = dict(self.claims)
        new_claims[key] = value
        return replace(self, claims=new_claims)


class AuthorizationServer:
    """Issues Ed25519-signed access tokens bound to a specific audience.

    Args:
        issuer: The issuer identifier placed in the iss claim.
    """

    def __init__(self, issuer: str):
        self.issuer = issuer
        self._private_key = Ed25519PrivateKey.generate()

    @property
    def public_key(self) -> bytes:
        """The issuer's 32-byte raw Ed25519 public key, for resource servers to verify with."""
        return self._private_key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

    def issue(self, *, subject: str, audience: str, scope: str, expires_at: int) -> Token:
        """Issue a token audience-bound to a single resource server (RFC 8707)."""
        claims = {
            "iss": self.issuer,
            "sub": subject,
            "aud": audience,
            "scope": scope,
            "exp": expires_at,
        }
        signature = self._private_key.sign(canonical_claims(claims))
        return Token(claims=claims, signature=signature)
