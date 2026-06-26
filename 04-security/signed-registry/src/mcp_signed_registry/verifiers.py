# ABOUTME: Signature verifiers for the signed registry; Ed25519 is the testable default.
# ABOUTME: A cosign/sigstore verifier (keyless OIDC, Rekor) is the planned container-image backend.
from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class Ed25519Verifier:
    """Verifies detached Ed25519 signatures against a set of known signer public keys.

    Args:
        public_keys: Mapping of signer_id to that signer's 32-byte raw Ed25519 public key.

    Keys are parsed once at construction. A malformed key (wrong length) is stored as unusable
    rather than raising, so admission fails closed for that signer (verify returns False) instead
    of throwing in the request path. An unknown signer or an invalid signature also return False.
    """

    def __init__(self, public_keys: dict[str, bytes]):
        self._keys: dict[str, Ed25519PublicKey | None] = {}
        for signer_id, raw_key in public_keys.items():
            try:
                self._keys[signer_id] = Ed25519PublicKey.from_public_bytes(raw_key)
            except (ValueError, TypeError):
                # Malformed key material (wrong length raises ValueError, wrong type raises TypeError):
                # keep the signer known but unusable so verify fails closed instead of throwing later.
                self._keys[signer_id] = None

    def verify(self, payload: bytes, signature: bytes, signer_id: str) -> bool:
        """Return True if signature is a valid Ed25519 signature over payload for signer_id."""
        key = self._keys.get(signer_id)
        if key is None:
            return False
        try:
            key.verify(signature, payload)
        except InvalidSignature:
            return False
        return True
