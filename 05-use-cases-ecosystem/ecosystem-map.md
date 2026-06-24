<!-- ABOUTME: An honest MCP ecosystem map separating verified facts from vendor/community claims.
ABOUTME: Adoption numbers are directional; the governance and protocol facts are the durable ones. -->

# MCP Ecosystem Map (2026-06)

A deliberately honest snapshot. Adoption metrics in this space are largely self-reported, so each row
is labeled. The durable facts are governance and protocol structure, not download counts.

## Governance and protocol (verified)

- MCP was donated by Anthropic to the Linux Foundation's Agentic AI Foundation (AAIF) on 2025-12-09.
- Latest stable spec is `2025-11-25`; `2026-07-28` is a Release Candidate (locked 2026-05-21, not final).
- A2A reached v1.0 (2026-03) and is also Linux Foundation governed. The consensus stack is MCP for
  agent-to-tool access and A2A for agent-to-agent coordination; they compose.
- Official SDKs are AAIF-governed across Python, TypeScript, Go, C#, Rust, Java, Kotlin, Ruby, Swift,
  PHP. Verified current pins are in `docs/research/version-currency-2026-06-23.md`.

## Reference servers (verified)

Seven are actively maintained by the steering group: Everything, Fetch, Filesystem, Git, Memory,
Sequential Thinking, Time. Roughly thirteen others (GitHub, GitLab, Slack, Google Drive, Postgres,
Sentry, SQLite, Puppeteer, and more) were archived to `servers-archived` and handed to vendor
maintenance. Many third-party tutorials still point at the archived code, so verify against the
current `modelcontextprotocol/servers` README before citing.

## Adoption (vendor or community self-reported)

Treat these as directional, not audited:

- ~97M monthly SDK downloads (Python + TypeScript), vendor-reported.
- Python SDK reportedly >164M monthly on PyPI by April 2026, vendor-reported.
- 10,000+ active public servers (Linux Foundation, Dec 2025).
- Independent census (Nerq, Q1 2026, via Knak): of 17,468 indexed servers, only 12.9% scored
  "high trust" (70+/100). This more conservative number is the useful counterweight.
- MCP Apps launched 2026-01-26 with day-one partners (Asana, Box, Canva, Figma, monday.com, Slack,
  and others), vendor-reported.

## What this track builds against the ecosystem

- `k8s.py`: a production-style, read-only server over a real CNCF API (Kubernetes), the kind of
  internal server an organization actually deploys. Read-only by default; a mutating tool would gate
  behind the security track's gateway and consent.
- `a2a_bridge.py`: the MCP plus A2A composition at its smallest, an MCP tool that delegates to another
  agent. The real transport (a2a-sdk) is documented in the spike; the seam is what matters.
