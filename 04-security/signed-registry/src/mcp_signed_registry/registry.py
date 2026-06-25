# ABOUTME: Provenance-verifying registry: admit an MCP server only with a trusted, valid signature.
# ABOUTME: Mitigates supply-chain tampering and shadow servers (OWASP MCP04/MCP09, NSA CSI rec 6).
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol


class Verifier(Protocol):
    """Verifies that a signature over a payload was produced by a given signer."""

    def verify(self, payload: bytes, signature: bytes, signer_id: str) -> bool:
        """Return True if the signature is valid for the payload under signer_id."""
        ...


@dataclass(frozen=True)
class ServerEntry:
    """A registry entry describing an MCP server and its provenance.

    Args:
        name: Logical server name.
        artifact_ref: Immutable artifact reference (for example a digest-pinned image).
        signer_id: Identity claimed to have signed this entry.
        signature: Detached signature over the canonical payload. Empty means unsigned.
    """

    name: str
    artifact_ref: str
    signer_id: str
    signature: bytes

    @staticmethod
    def canonical_payload(name: str, artifact_ref: str, signer_id: str) -> bytes:
        """Return the canonical bytes that get signed and verified for an entry.

        JSON-encodes the fields as a list so the encoding is injective: a delimiter or newline inside
        a field cannot shift the boundary and make two distinct entries serialize to the same bytes.
        """
        return json.dumps([name, artifact_ref, signer_id], separators=(",", ":")).encode()

    @property
    def payload(self) -> bytes:
        """The canonical payload for this entry."""
        return self.canonical_payload(self.name, self.artifact_ref, self.signer_id)


@dataclass(frozen=True)
class AdmissionResult:
    """Whether an entry may be admitted, with the reason."""

    admitted: bool
    reason: str


@dataclass
class SignedRegistry:
    """Admits MCP servers only when a trusted signer produced a valid signature.

    The check is, in order: the signer must be trusted, the entry must be signed, and the
    signature must verify over the entry's canonical payload. Any failure rejects the entry.
    """

    verifier: Verifier
    trusted_signers: set[str]

    def admit(self, entry: ServerEntry) -> AdmissionResult:
        """Decide whether to admit a server entry."""
        if entry.signer_id not in self.trusted_signers:
            return AdmissionResult(False, f"untrusted signer: {entry.signer_id}")
        if not entry.signature:
            return AdmissionResult(False, "unsigned entry: no signature present")
        if not self.verifier.verify(entry.payload, entry.signature, entry.signer_id):
            return AdmissionResult(False, "signature invalid for entry payload")
        return AdmissionResult(True, "admitted: trusted signer, valid signature")
