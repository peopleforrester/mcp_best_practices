<!-- ABOUTME: The policy-enforcing MCP gateway: a testable policy core plus a FastMCP transport adapter.
ABOUTME: This is the spine of the security track; guardrails and the signed registry plug into it. -->

# MCP Policy Gateway

A policy-enforcing gateway that sits between an MCP client and one or more upstream MCP servers. It
decides, per tool call, whether to allow or deny, and emits a SIEM-ready audit record for every
decision. It is the control point the threat models in `../threat-models/` call for.

## Design

The gateway separates the policy decision (original, framework-independent, fully unit-tested) from
the transport (a thin FastMCP adapter). This keeps the security logic provable and portable.

- **`policy.py` (the core).** `PolicyEngine.evaluate(request)` returns an allow/deny decision with a
  reason. Evaluation is secure default-deny, in order:
  1. **Allowlist**: deny any tool not allowlisted for the `(client_id, server_id)` pair (mitigates
     shadow servers and tool-name shadowing, OWASP MCP09; with definition pinning, rug-pulls, MCP03).
  2. **Explicit deny rules** (OPA-style predicates): a deny wins over any later allow.
  3. **Consent gate**: deny a non-read-only tool the client has not consented to (mitigates
     over-broad consent and scope creep, MCP02). Undeclared tools default to needing consent.
  4. Default allow only for an allowlisted, consented tool.
- **`audit.py`.** `audit_record(...)` builds a structured record (NSA CSI recommendation 8). Arguments
  are fingerprinted with sha256, never logged in plaintext, so secrets passed as arguments do not
  leak (OWASP MCP01).
- **FastMCP adapter (next).** A FastMCP 3.x middleware that intercepts each `tools/call`, builds a
  `PolicyRequest`, consults the engine, denies with a clean protocol error or forwards to the
  upstream, and writes the audit record. The exact 3.x middleware/proxy API is being confirmed by a
  research spike before this layer is written (per the research-before-adopting rule).

## Develop

```bash
cd 04-security/policy-gateway
uv run pytest -q     # run the test suite
uv run ruff check .  # lint
```

Built against the stable `2025-11-25` spec. The `2026-07-28` RC moves session state into explicit
tool-argument handles and adds `Mcp-Method`/`Mcp-Name` routing headers, both of which suit a gateway;
that path will be added as labeled preview.
