# ABOUTME: End-to-end tests that the four security controls compose in one server request path.
# ABOUTME: Registry admission gates the build; the gateway denies/audits; guardrails redact results.
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastmcp import Client
from fastmcp.exceptions import ToolError
from mcp_signed_registry import Ed25519Verifier, ServerEntry, SignedRegistry

from mcp_capstone.server import build_capstone_server

_NAME = "security-capstone"
_ARTIFACT = "ghcr.io/acme/capstone@sha256:abc"
_SIGNER = "acme"


def _entry(sk):
    payload = ServerEntry.canonical_payload(_NAME, _ARTIFACT, _SIGNER)
    return ServerEntry(name=_NAME, artifact_ref=_ARTIFACT, signer_id=_SIGNER, signature=sk.sign(payload))


def _trusted_registry():
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    registry = SignedRegistry(verifier=Ed25519Verifier({_SIGNER: pk}), trusted_signers={_SIGNER})
    return registry, _entry(sk)


def _build(*, consents=frozenset(), audit=None):
    registry, entry = _trusted_registry()
    return build_capstone_server(
        registry=registry,
        registry_entry=entry,
        consents_for=lambda _client: frozenset(consents),
        audit_sink=(audit.append if audit is not None else lambda _record: None),
    )


def test_unadmitted_server_is_refused_to_build():
    # A server whose entry no trusted signer vouches for must not start (provenance gate).
    sk = Ed25519PrivateKey.generate()
    registry = SignedRegistry(verifier=Ed25519Verifier({}), trusted_signers=set())
    with pytest.raises(RuntimeError):
        build_capstone_server(
            registry=registry,
            registry_entry=_entry(sk),
            consents_for=lambda _c: frozenset(),
            audit_sink=lambda _r: None,
        )


async def test_read_tool_is_allowed_and_audited():
    audit: list[dict] = []
    async with Client(_build(audit=audit)) as client:
        result = await client.call_tool("lookup_record", {"record_id": "r1"})
    assert "r1" in result.data
    assert audit[-1]["decision"] == "ALLOW"


async def test_destructive_tool_denied_without_consent_and_audited():
    audit: list[dict] = []
    async with Client(_build(audit=audit)) as client:
        with pytest.raises(ToolError):
            await client.call_tool("delete_record", {"record_id": "r1"})
    assert audit[-1]["decision"] == "DENY"


async def test_destructive_tool_allowed_with_consent():
    async with Client(_build(consents={"delete_record"})) as client:
        result = await client.call_tool("delete_record", {"record_id": "r1"})
    assert "r1" in result.data


async def test_guardrails_redact_a_secret_in_the_tool_result():
    async with Client(_build()) as client:
        result = await client.call_tool("lookup_record", {"record_id": "leaky"})
    assert "sk-" not in result.data
    assert "REDACTED" in result.data


async def test_guardrails_redact_a_secret_nested_in_structured_content():
    # A secret buried inside a nested dict/list of structured output must be redacted too, not just
    # top-level string values. Otherwise a tool can leak by returning {"meta": {"notes": ["sk-..."]}}.
    async with Client(_build()) as client:
        result = await client.call_tool("lookup_record_detail", {"record_id": "leaky"})
    blob = json.dumps(result.data)
    assert "sk-" not in blob
    assert "ada@example.com" not in blob
    assert "REDACTED" in blob
