<!-- ABOUTME: Index for the original STRIDE-per-component threat models of an MCP deployment.
ABOUTME: Each component file maps threats to OWASP MCP Top 10 IDs and NSA CSI recommendations. -->

# MCP Threat Models (STRIDE per component)

Original threat models for a Model Context Protocol deployment, decomposed by trust zone. The
decomposition follows the NSA guidance to treat agents, plugins, models, and users as separate trust
zones (NSA CSI recommendation 2). Each component is analyzed with STRIDE (Spoofing, Tampering,
Repudiation, Information disclosure, Denial of service, Elevation of privilege). Every threat is
mapped to an OWASP MCP Top 10 category and to the relevant NSA CSI recommendation, with a concrete
mitigation that this portfolio's security track demonstrates in code.

These models are the design input for the policy gateway, guardrails, and signed registry built in
the rest of `04-security/`. They are written against the stable `2025-11-25` spec; where the
`2026-07-28` RC changes the attack surface (the stateless core, removed handshake, new transport
headers), that is noted inline as preview.

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

How each OWASP MCP Top 10 category surfaces across the trust zones and which built control closes it.
Component models carry the per-threat detail; this is the one-view map from risk to mitigation.

| OWASP | Risk | Primary zones | Control that closes it |
|---|---|---|---|
| MCP01 | Token mismanagement & secret exposure | server, host, auth-server, data-stores | Guardrails redaction; gateway audit hashes arguments |
| MCP02 | Privilege escalation via scope creep | host, auth-server | Gateway consent gate; OAuth audience binding |
| MCP03 | Tool poisoning (description injection) | LLM, client, host | Guardrails injection detection; signed registry; gateway tool-definition pinning |
| MCP04 | Supply chain & dependency tampering | server | Signed registry (provenance verification) |
| MCP05 | Command injection & execution | server | Schema validation + sandboxing (server-side); gateway allowlist |
| MCP06 | Intent flow subversion | LLM, host | Guardrails injection detection; gateway per-action consent |
| MCP07 | Insufficient authn/authz | server, auth-server | OAuth resource-server validation; gateway policy |
| MCP08 | Lack of audit & telemetry | host, server | Gateway SIEM-ready audit record per decision |
| MCP09 | Shadow MCP servers | host, server | Signed registry admission; gateway allowlist |
| MCP10 | Context injection & over-sharing | LLM, data-stores | Guardrails redaction; gateway per-server data-flow policy |

NSA CSI recommendations map across the same controls: rec 2 (trust boundaries) is the zone
decomposition itself; rec 4 (validate parameters) and rec 5 (sandbox) are server-side; rec 6 (sign and
verify) is the signed registry; rec 7 (treat outputs as untrusted) is the guardrails posture; rec 8
(log invocations) is the gateway audit record.

