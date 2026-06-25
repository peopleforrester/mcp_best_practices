<!-- ABOUTME: The composed capstone: registry admission + policy gateway + guardrails + audit in one server.
ABOUTME: This is the artifact that proves the security track's controls compose, not just in prose. -->

# Security Capstone (composed)

The other security packages each demonstrate one control in isolation. This package wires them into a
single FastMCP server so the request path runs every control together, and the tests prove they compose.

`build_capstone_server(...)`:

1. **Provenance gate (signed registry).** The build calls `SignedRegistry.admit(entry)` first; a server
   whose entry no trusted signer vouches for raises and never starts. (OWASP MCP04/MCP09.)
2. **Policy gateway (outermost middleware).** `PolicyMiddleware` evaluates each call against the
   allowlist, OPA-style rules, and the consent gate, and writes a SIEM-ready audit record. A
   destructive tool without consent is denied with a `ToolError` before it runs. (MCP02/MCP08/MCP09.)
3. **Guardrails (innermost middleware).** `GuardrailsMiddleware` scans the returned text for
   indirect-prompt-injection signals and redacts secret/PII shapes before the result leaves the
   server. (MCP01/MCP03/MCP10.)

The middleware order is an onion: policy is added first (outermost, so it denies and audits before the
tool runs), guardrails second (innermost, so they sanitize the result on the way back out).

The tests (`tests/test_capstone.py`) show, end to end over the in-memory client: an unadmitted server
refuses to build, a read tool is allowed and audited, a destructive tool is denied without consent and
allowed with it, and a secret in a tool result is redacted before return. Real Ed25519 signatures, no
mocks. This package depends on the three sibling packages via `[tool.uv.sources]` path deps; it is the
one package that intentionally composes the others.

```bash
uv run pytest -q
uv run ruff check .
```
