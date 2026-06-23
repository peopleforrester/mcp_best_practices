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

The cross-component summary table (every threat in one view) lives at the bottom of this file once
the component models are complete.
