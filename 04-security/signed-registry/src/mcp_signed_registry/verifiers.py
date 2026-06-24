# ABOUTME: Signature verifiers for the signed registry; Ed25519 is the testable default.
# ABOUTME: A cosign/sigstore verifier (keyless OIDC, Rekor) is the planned container-image backend.
from __future__ import annotations

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class Ed25519Verifier:
    """Verifies detached Ed25519 signatures against a set of known signer public keys.

    Args:
        public_keys: Mapping of signer_id to that signer's 32-byte raw Ed25519 public key.

    An unknown signer or an invalid signature both return False; the registry treats either
    as a rejection.
    """

    def __init__(self, public_keys: dict[str, bytes]):
        self._keys = dict(public_keys)

    def verify(self, payload: bytes, signature: bytes, signer_id: str) -> bool:
        """Return True if signature is a valid Ed25519 signature over payload for signer_id."""
        raw_key = self._keys.get(signer_id)
        if raw_key is None:
            return False
        try:
            Ed25519PublicKey.from_public_bytes(raw_key).verify(signature, payload)
        except InvalidSignature:
            return False
        return True
