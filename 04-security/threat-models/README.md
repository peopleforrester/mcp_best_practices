<!-- ABOUTME: Index for the original STRIDE-per-component threat models of an MCP deployment.
ABOUTME: Each component file maps threats to OWASP MCP Top 10 IDs and NSA CSI recommendations. -->

# MCP Threat Models (STRIDE per component)

Original threat models for a Model Context Protocol deployment, decomposed by trust zone. The
decomposition follows the NSA guidance to treat agents, plugins, models, and users as separate trust
zones (NSA CSI recommendation 2). Each component is analyzed with STRIDE (Spoofing, Tampering,
Repudiation, Information disclosure, Denial of service, Elevation of privilege). Every threat is
mapped to an OWASP MCP Top 10 category and to the relevant NSA CSI recommendation, with a concrete
mitigation.

### Implemented here vs target design

The mitigation column describes the full defense-in-depth design for each threat, which is deliberately
larger than what this teaching repo ships. Read every mitigation as the target design; the parts this
portfolio actually implements are:

- **Policy gateway** (`policy-gateway/`, composed in `capstone/`): allowlist, per-client consent gate,
  OPA-style deny/allow rules, a token-bucket per-client rate limit, and a sha256 audit record per
  decision.
- **Audience-bound tokens** (`oauth-confused-deputy/`): RFC 8707 validation of signature, `iss`, `exp`,
  and `aud`, plus the passthrough-vs-exchange demonstration. This package is standalone; it is not
  imported by the gateway, so per-request token validation at the gateway is target design, not wired.
- **Signed provenance** (`signed-registry/`): Ed25519 verification and admission. cosign/sigstore is
  planned, not built; where a mitigation says "cosign" today it means the Ed25519 stand-in.
- **Guardrails** (`guardrails/`): injection detection and secret/PII redaction applied to tool results
  (egress).

Controls named in the mitigations but **not** implemented in this repo (they are target design): the
gateway validating tokens or re-checking audience per call, pinning tool descriptions and re-checking
on `tools/list`, per-session action or token budgets, URL-level egress allowlists and resource-URL
pinning, per-tool token scoping, and result hashing or tamper-evident chaining of audit records. These
are marked inline where they appear.

These models are the design input for the packages built in the rest of `04-security/`. They were
written against the `2025-11-25` baseline; where the now-final `2026-07-28` revision changes the attack
surface (the stateless core, removed handshake, new transport headers), that is noted inline. The shipped
security packages run on stable FastMCP 3.4.x (prior `2025-11-25` semantics); the stateless-core paths
are the labeled forward direction.

## Components

| File | Trust zone |
|---|---|
| [`host.md`](host.md) | Host application (Claude Desktop/Code, IDE, agent runtime) |
| [`client.md`](client.md) | MCP client (one per server, embedded in the host) |
| [`llm.md`](llm.md) | The model and the inference boundary |
| [`server.md`](server.md) | The MCP server |
| [`data-stores.md`](data-stores.md) | Backing data stores and downstream resources/APIs |
| [`auth-server.md`](auth-server.md) | The OAuth 2.1 authorization server |

## Reference frameworks

- **OWASP MCP Top 10** (beta, Phase 3): MCP01 Token Mismanagement & Secret Exposure, MCP02 Privilege
  Escalation via Scope Creep, MCP03 Tool Poisoning, MCP04 Supply Chain & Dependency Tampering, MCP05
  Command Injection & Execution, MCP06 Intent Flow Subversion, MCP07 Insufficient Authn/Authz, MCP08
  Lack of Audit & Telemetry, MCP09 Shadow MCP Servers, MCP10 Context Injection & Over-Sharing.
- **NSA AISC CSI** (May 2026) ten recommendations, summarized in
  `docs/research/mcp-sme-portfolio-research-2026-06.md`.

## Cross-component summary

How each OWASP MCP Top 10 category surfaces across the trust zones and which control closes it (built
in this repo unless a row says target design). Component models carry the per-threat detail; this is
the one-view map from risk to mitigation.

| OWASP | Risk | Primary zones | Control that closes it |
|---|---|---|---|
| MCP01 | Token mismanagement & secret exposure | server, host, auth-server, data-stores | Guardrails redaction; gateway audit fingerprints arguments (never raw) |
| MCP02 | Privilege escalation via scope creep | host, auth-server | Gateway consent gate; OAuth audience binding |
| MCP03 | Tool poisoning (description injection) | LLM, client, host | Guardrails injection detection; signed registry admission (tool-definition pinning is target design) |
| MCP04 | Supply chain & dependency tampering | server | Signed registry (provenance verification) |
| MCP05 | Command injection & execution | server | Schema-validated parameters (FastMCP/pydantic); gateway allowlist + per-client rate limit (sandboxing is target design) |
| MCP06 | Intent flow subversion | LLM, host | Guardrails injection detection; gateway per-action consent |
| MCP07 | Insufficient authn/authz | server, auth-server | OAuth resource-server validation; gateway policy |
| MCP08 | Lack of audit & telemetry | host, server | Gateway SIEM-ready audit record per decision |
| MCP09 | Shadow MCP servers | host, server | Signed registry admission; gateway allowlist |
| MCP10 | Context injection & over-sharing | LLM, data-stores | Guardrails redaction (egress); URL-level data-flow policy is target design |

NSA CSI recommendations map across the same controls: rec 2 (trust boundaries) is the zone
decomposition itself; rec 4 (validate parameters) and rec 5 (sandbox) are server-side; rec 6 (sign and
verify) is the signed registry; rec 7 (treat outputs as untrusted) is the guardrails posture; rec 8
(log invocations) is the gateway audit record.

