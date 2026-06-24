# ABOUTME: Tests for the signed registry admission logic using real Ed25519 signatures.
# ABOUTME: Admit only trusted-signer, validly-signed entries; reject untrusted, tampered, unsigned.
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from mcp_signed_registry.registry import ServerEntry, SignedRegistry
from mcp_signed_registry.verifiers import Ed25519Verifier


def _keypair():
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw
    )
    return sk, pk


def _signed_entry(sk, name="fs-server", artifact="ghcr.io/acme/fs@sha256:abc", signer="acme"):
    payload = ServerEntry.canonical_payload(name, artifact, signer)
    return ServerEntry(name=name, artifact_ref=artifact, signer_id=signer, signature=sk.sign(payload))


def _registry(pk, signer="acme", trusted=("acme",)):
    return SignedRegistry(verifier=Ed25519Verifier({signer: pk}), trusted_signers=set(trusted))


def test_admits_valid_signed_entry_from_trusted_signer():
    sk, pk = _keypair()
    result = _registry(pk).admit(_signed_entry(sk))
    assert result.admitted is True


def test_rejects_untrusted_signer():
    sk, pk = _keypair()
    result = _registry(pk, trusted=()).admit(_signed_entry(sk))
    assert result.admitted is False
    assert "untrusted signer" in result.reason


def test_rejects_tampered_payload():
    sk, pk = _keypair()
    entry = _signed_entry(sk)
    tampered = ServerEntry(
        name=entry.name,
        artifact_ref="ghcr.io/evil/backdoor@sha256:bad",
        signer_id=entry.signer_id,
        signature=entry.signature,
    )
    result = _registry(pk).admit(tampered)
    assert result.admitted is False
    assert "signature" in result.reason


def test_rejects_unsigned_entry():
    sk, pk = _keypair()
    entry = ServerEntry(name="x", artifact_ref="r", signer_id="acme", signature=b"")
    result = _registry(pk).admit(entry)
    assert result.admitted is False
    assert "unsigned" in result.reason
