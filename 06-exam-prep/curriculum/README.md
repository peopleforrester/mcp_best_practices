<!-- ABOUTME: The ordered MCP study path: modules from primitives to advanced, mapped to competencies.
ABOUTME: Derived from the researched curriculum; the quiz app tests this body of knowledge. -->

# MCP Curriculum (ordered study path)

The body of knowledge an MCP exam tests, ordered from primitives to systems. Each module maps to a
portfolio competency, so a learner can study the topic and then read the corresponding track's code.
The full researched version with sources is in `docs/research/exam-curriculum-2026-06-23.md`; the quiz
app's question bank draws from these domains.

| # | Module | Competency / track | Key topics |
|---|--------|--------------------|------------|
| 1 | MCP overview & mental model | fundamentals | host/client/server roles, why a standard beats N×M integrations, governance |
| 2 | JSON-RPC 2.0 message layer | fundamentals | requests/responses/notifications, UTF-8, error codes, `_meta` |
| 3 | Lifecycle & capability negotiation | fundamentals | initialize handshake (stable), version negotiation, capability maps |
| 4 | Transports: stdio & Streamable HTTP | architecture | stdio vs Streamable HTTP, HTTP+SSE legacy, sessions, rebinding defenses |
| 5 | Server primitives: tools, resources, prompts | tooling | registration, list/call, output schemas |
| 6 | Client primitives: sampling, roots, elicitation | tooling | client-side capabilities, consent, RC deprecations |
| 7 | Clients & hosts in practice | tooling | multi-server aggregation, SDK tiers, minimal client |
| 8 | Architecture: stateful vs stateless, scaling, registry | architecture | sessions vs handles, load balancing, the registry |
| 9 | The 2026-07-28 RC (stateless core + extensions) | architecture | no handshake, `_meta`, `server/discover`, extensions, MCP Apps, Tasks |
| 10 | Authorization: OAuth 2.1 + RFC 8707 | security | resource server, audience binding, token passthrough forbidden |
| 11 | Threat model: OWASP MCP Top 10 | security | MCP01 to MCP10 |
| 12 | NSA AISC CSI security design considerations | security | trust boundaries, least privilege, signed provenance, egress control |
| 13 | Ecosystem, governance & A2A | use-cases-ecosystem | AAIF/LF, MCP vs A2A, SEP process |

## Exam blueprint (summary)

A 50-question exam weighted toward security (about 30%), with the rest spread across fundamentals,
architecture, tooling, and ecosystem. The full blueprint (weights and difficulty mix) is in the
research doc. The shipped question bank (`quiz-app/src/mcp_quiz/questions.yaml`) is a seed sample
across these domains; grow it toward the blueprint weights.

## Currency

Version-sensitive items (the RC stateless core, deprecations, new extensions) must be re-verified when
`2026-07-28` goes final. See `docs/spec-currency.md` and the research doc's currency notes.
