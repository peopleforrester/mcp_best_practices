<!-- ABOUTME: Provenance-verifying MCP server registry: admit only trusted, validly-signed servers.
ABOUTME: Ed25519 is the testable default verifier; a cosign/sigstore backend is the container path. -->

# Signed MCP Registry

Admission control for MCP servers based on provenance. A server is admitted only when a trusted
signer produced a valid signature over the server's registry entry. This is the supply-chain control
the threat models call for (OWASP MCP04 supply-chain tampering, MCP09 shadow servers, NSA CSI
recommendation 6: sign and verify).

## Design

The admission logic is separated from the signature scheme behind a `Verifier` protocol, so the core
is provable and the cryptographic backend is swappable.

- **`registry.py`** : `SignedRegistry.admit(entry)` decides in order: the signer must be trusted, the
  entry must be signed, and the signature must verify over the entry's canonical payload. Any failure
  rejects. `ServerEntry.canonical_payload(...)` defines exactly what gets signed (name, artifact
  reference, signer id), so a tampered artifact reference invalidates the signature.
- **`verifiers.py`** : `Ed25519Verifier` is the default, a real asymmetric verifier over known signer
  public keys. It is the unit-tested path (tests generate real keypairs and sign real entries; no
  mocks).

## cosign / sigstore backend (planned)

The production provenance path for container-packaged servers is cosign/sigstore: keyless OIDC
signing via Fulcio, the Rekor transparency log, and admission enforcement via sigstore
policy-controller or Kyverno. That arrives as a `CosignVerifier` implementing the same `Verifier`
protocol, shelling out to `cosign verify` (cosign 3.x). It is an integration concern (external CLI,
network, transparency log), so it is covered by an integration test rather than the unit suite, and
is not wired in yet.

## Develop

```bash
cd 04-security/signed-registry
uv run pytest -q
uv run ruff check .
```
