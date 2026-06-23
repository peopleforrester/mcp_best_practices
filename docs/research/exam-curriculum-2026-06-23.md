<!-- ABOUTME: Researched MCP learning curriculum and exam blueprint that drives the 06-exam-prep track.
ABOUTME: Seeds the ordered study path and the quiz-app question bank; refresh when the 2026-07-28 spec is final. -->

# MCP Exam Curriculum & Blueprint (researched 2026-06-23)

Built from official/authoritative sources (modelcontextprotocol.io spec pages, the RC blog,
owasp.org MCP Top 10, the NSA/defense.gov CSI, Linux Foundation/Anthropic governance posts, IETF
RFC 8707). Stable baseline is `2025-11-25`; the `2026-07-28` revision is a Release Candidate, so
all RC-derived specifics are flagged in "Notes on currency" for re-verification at GA. This drives
the `06-exam-prep/curriculum/` study path and the `quiz-app/` question bank.

## Body of knowledge (ordered, fundamentals to advanced)

1. **MCP overview & mental model** (competency: fundamentals)
   - What MCP is (open protocol connecting AI models/agents to tools, data, apps); the host/client/server roles; the "USB-C for AI" framing.
   - Origin (Anthropic, late 2024), donation to the Linux Foundation / AAIF (Dec 9, 2025), vendor-neutral governance; adoption scale (vendor-reported ~97M monthly downloads, >10,000 published servers).
   - Why a standard beats N×M bespoke integrations.
   - Sources: https://modelcontextprotocol.io/ , https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation

2. **JSON-RPC 2.0 message layer** (competency: fundamentals)
   - Requests, responses, notifications; the `id` correlation rule; batching expectations.
   - UTF-8 encoding requirement; standard vs MCP-custom error codes (RC change: `-32602` replaces `-32002` for missing-resource, SEP-2164).
   - Error envelopes; `_meta` field usage.
   - Source: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

3. **Lifecycle & capability negotiation** (competency: fundamentals)
   - The `initialize` to `InitializeResult` to `initialized` handshake (2025-11-25 baseline).
   - Version negotiation; the `MCP-Protocol-Version` header; fallback to `2025-03-26` when absent.
   - Capability maps: client and server advertise and commit to only-negotiated capabilities (a client cannot call a tool a server never declared).
   - Sources: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle , https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

4. **Transports: stdio and Streamable HTTP** (competency: architecture)
   - The two standard transports; clients SHOULD support stdio whenever possible.
   - Streamable HTTP replaced the old HTTP+SSE transport (from protocol version 2024-11-05); single MCP endpoint supporting POST and GET; optional SSE for server-streamed messages.
   - `MCP-Session-Id` header for optional stateful sessions; resumability via SSE event `id` + `Last-Event-ID`; 404 to re-initialize behavior.
   - Origin-header validation, localhost binding, and DNS-rebinding defenses.
   - Source: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

5. **Server primitives: tools, resources, prompts** (competency: tooling)
   - Tools (typed callable functions: name + JSON Schema input + description); Resources (read-only contextual data addressed by URI); Prompts (parameterized reusable templates).
   - `tools/list`, `tools/call`, `resources/list`, `resources/read`, `prompts/list`, `prompts/get`; list-changed notifications.
   - Tool/output schemas (RC: JSON Schema 2020-12 with `oneOf`/`anyOf`/`allOf`/`$ref`, SEP-2106).
   - Sources: https://modelcontextprotocol.io/docs/concepts , https://modelcontextprotocol.io/specification/2025-11-25/server/tools

6. **Client primitives: sampling, roots, elicitation** (competency: tooling)
   - Sampling (server delegates inference back to the client that owns the model/keys); Roots (filesystem/URI scoping); Elicitation (server requests structured user input, human-in-the-loop).
   - Why these are gated behind capability negotiation and consent.
   - RC deprecations to watch: Roots, Sampling, and Logging are deprecated (SEP-2577, 12-month window).
   - Sources: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling , https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation

7. **Clients & hosts in practice** (competency: tooling)
   - How a host app (IDE, chat client, agent) orchestrates multiple servers; multi-server capability aggregation.
   - Official SDKs and tiers: Tier 1 = TypeScript, Python, C#, Go; Tier 2 = Java, Rust; Tier 3 = Swift, Ruby, PHP; Kotlin TBD.
   - Building a minimal server and client; local vs remote transport selection.
   - Sources: https://modelcontextprotocol.io/docs/sdk , https://github.com/modelcontextprotocol/python-sdk

8. **Architecture: stateful vs stateless, scaling, registry** (competency: architecture)
   - Stateful sessions (sticky routing + shared session store) under 2025-11-25 vs the RC stateless direction.
   - Horizontal scaling, load balancing, and where to hold application state (explicit handles like `basket_id` passed as tool args).
   - The MCP Registry as a discovery surface for published servers.
   - Sources: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports , https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/

9. **The 2026-07-28 Release Candidate (stateless core + extensions)** (competency: architecture)
   - Stateless core: removal of `initialize`/`initialized` handshake (SEP-2575) and `Mcp-Session-Id`/protocol-level session (SEP-2567); protocol version/client info/capabilities now travel inline in `_meta` per request; `server/discover` for capabilities.
   - Multi round-trip requests replacing SSE for server-to-client (`InputRequiredResult`, SEP-2322); `Mcp-Method`/`Mcp-Name` routing headers; client-side caching (`ttlMs`/`cacheScope`); W3C Trace Context (SEP-414).
   - Extensions framework (SEP-2133); MCP Apps (sandboxed HTML UIs, SEP-1865); redesigned Tasks; formal deprecation policy; SDK conformance tiers.
   - RC, not final: locked 2026-05-21, final 2026-07-28.
   - Sources: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ , https://aaif.io/blog/mcp-is-growing-up/

10. **Authorization: OAuth 2.1 + RFC 8707** (competency: security)
    - MCP server as OAuth 2.1 resource server; token validation per OAuth 2.1 §5.2; audience binding.
    - RFC 8707 Resource Indicators: the client MUST send `resource` (canonical MCP server URI) on authorization AND token requests so tokens are audience-scoped, defeating the confused-deputy / token-ambiguity attack.
    - Token passthrough is forbidden: servers MUST only accept tokens issued for themselves; clients MUST NOT send other-issuer tokens; servers MUST NOT transit foreign tokens.
    - RC authz hardening: `iss` validation per RFC 9207 (SEP-2468), credential-to-AS binding (SEP-2352), `.well-known` discovery (SEP-2351).
    - Sources: https://modelcontextprotocol.io/specification/draft/basic/authorization , https://datatracker.ietf.org/doc/html/rfc8707

11. **Threat model: OWASP MCP Top 10** (competency: security)
    - MCP01 Token Mismanagement & Secret Exposure; MCP02 Privilege Escalation via Scope Creep; MCP03 Tool Poisoning (description injection); MCP04 Supply Chain & Dependency Tampering; MCP05 Command Injection & Execution.
    - MCP06 Intent Flow Subversion; MCP07 Insufficient Authn/Authz; MCP08 Lack of Audit & Telemetry; MCP09 Shadow MCP Servers; MCP10 Context Injection & Over-Sharing.
    - Project status: Beta (Phase 3), living document; lead Vandana Verma Sehgal.
    - Source: https://owasp.org/www-project-mcp-top-10/

12. **NSA AISC CSI security design considerations** (competency: security)
    - CSI "MCP: Security Design Considerations for AI-Driven Automation," May 2026, v1.0 (U/OO/6030316-26).
    - Protocol-inversion risk; authentication optional + no RBAC in the protocol; novel risks (dynamic tool invocation, implicit trust, context sharing).
    - Recommendations: treat every session untrusted until verified; least-privilege per-action/per-tool tokens; signed provenance for dynamically discovered servers; filtering outbound proxy / DLP with pinned resource URLs.
    - Sources: https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF , https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/

13. **Ecosystem, governance & A2A** (competency: use-cases-ecosystem)
    - AAIF / Linux Foundation stewardship; Platinum founders (AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI); maintainer-led governance unchanged.
    - MCP vs A2A: MCP = agent-to-tool/system; A2A = agent-to-agent (also Linux Foundation, originally Google); they compose.
    - SEP process / Extensions Track; deprecation policy; production use cases.
    - Sources: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation , https://a2a-protocol.org/latest/

## Exam blueprint

Target: 50 questions. Security weighted heaviest (the portfolio's flagship).

| # | Domain | Competency | Weight | Approx. Qs | Difficulty mix (E / M / H) |
|---|--------|-----------|--------|-----------|----------------------------|
| 1 | Fundamentals & message layer (JSON-RPC, lifecycle, capability negotiation) | fundamentals | 18% | 9 | 50 / 40 / 10 |
| 2 | Transports & connection (stdio, Streamable HTTP, sessions, SSE) | architecture | 14% | 7 | 30 / 50 / 20 |
| 3 | Primitives & SDK usage (tools/resources/prompts, sampling/roots/elicitation) | tooling | 18% | 9 | 40 / 45 / 15 |
| 4 | Architecture & the 2026-07-28 RC (stateful vs stateless, scaling, extensions, registry) | architecture | 14% | 7 | 20 / 50 / 30 |
| 5 | Security & authorization (OAuth 2.1, RFC 8707, confused-deputy, token passthrough) | security | 22% | 11 | 25 / 45 / 30 |
| 6 | Security frameworks (OWASP MCP Top 10, NSA CSI) | security | 8% | 4 | 30 / 50 / 20 |
| 7 | Ecosystem & governance (AAIF/LF, A2A, SDK tiers) | use-cases-ecosystem | 6% | 3 | 60 / 30 / 10 |
| | **Total** | | **100%** | **50** | ~**35% E / 44% M / 21% H** |

Security domains (5 + 6) = 30% of the exam.

## Sample questions (seed the question bank)

**Q1 (Transports, Medium).** In MCP 2025-11-25, which transport officially replaced the HTTP+SSE transport from protocol version 2024-11-05?
- A. WebSocket transport
- B. Streamable HTTP ✅
- C. gRPC transport
- D. Long-polling HTTP

Rationale: The spec marks Streamable HTTP as the replacement for the 2024-11-05 HTTP+SSE transport, using one endpoint for POST and GET with optional SSE.

**Q2 (Security/authz, Hard).** RFC 8707 Resource Indicators are mandated by MCP authorization primarily to prevent which attack?
- A. DNS rebinding against local servers
- B. The confused-deputy / token-ambiguity attack, by binding a token's audience to a specific MCP server ✅
- C. Prompt injection via tool descriptions
- D. SSE stream replay

Rationale: The `resource` parameter pins the token's intended audience (canonical server URI), so a token for a low-privilege server cannot be replayed at a high-privilege one.

**Q3 (Security/authz, Medium).** Why does the MCP authorization spec forbid token passthrough?
- A. It increases JSON-RPC payload size
- B. A server must only accept tokens issued for itself; accepting or forwarding foreign-issued tokens breaks audience validation and least privilege ✅
- C. Passthrough tokens cannot be cached
- D. OAuth 2.1 has no refresh tokens

Rationale: MCP servers MUST validate that tokens were issued for them and MUST NOT accept or transit other tokens.

**Q4 (Architecture/RC, Hard).** In the 2026-07-28 release candidate's stateless core, how do protocol version, client info, and capabilities reach the server now that the initialize handshake and `Mcp-Session-Id` are removed?
- A. In a one-time `initialized` notification
- B. Inline in a `_meta` field on each request; servers call `server/discover` for capabilities ✅
- C. In the `MCP-Session-Id` header on every request
- D. They are inferred from the TLS certificate

Rationale: SEP-2567/SEP-2575 remove sessions and the handshake; per-request `_meta` lets any instance serve any request behind a plain load balancer.

**Q5 (Fundamentals, Easy).** Which encoding MUST all MCP JSON-RPC messages use?
- A. UTF-16
- B. ASCII only
- C. UTF-8 ✅
- D. Base64

Rationale: The transport spec requires JSON-RPC messages to be UTF-8 encoded.

**Q6 (Primitives, Medium).** Which MCP primitive lets a server delegate LLM inference back to the client that owns the model and API keys?
- A. Resources
- B. Prompts
- C. Sampling ✅
- D. Roots

Rationale: Sampling is the client-side primitive for server-requested inference; it is also deprecated in the 2026-07-28 RC.

**Q7 (Security/OWASP, Medium).** "Tool poisoning" in the OWASP MCP Top 10 refers to what?
- A. Overloading a server with tool-call requests
- B. Embedding malicious instructions in a tool's description that the LLM then follows ✅
- C. Registering duplicate tool names
- D. Exhausting a tool's rate limit

Rationale: MCP03 (Tool Poisoning) is description/metadata injection that hijacks model behavior.

**Q8 (Security/NSA, Hard).** The NSA AISC CSI on MCP recommends which posture for external MCP connections?
- A. Allow all outbound traffic to maximize tool availability
- B. Disable authentication for trusted internal servers
- C. A filtering outbound proxy / DLP with resource URLs and access methods pinned tightly; treat sessions as untrusted until verified ✅
- D. Rely solely on TLS for trust

Rationale: The CSI flags optional auth and no protocol-level RBAC, recommending least-privilege per-action tokens, signed provenance, and filtering proxies.

**Q9 (Transports, Medium).** A Streamable HTTP server that wants stateful sessions assigns the session ID how, and what must the client then do?
- A. In a JSON-RPC param on initialize; ignore it afterward
- B. In the `MCP-Session-Id` response header on the `InitializeResult`; the client MUST echo it on all subsequent requests ✅
- C. In a URL query string regenerated per request
- D. In the SSE `retry` field

Rationale: The session ID rides the `MCP-Session-Id` header; a 404 signals the client to re-initialize.

**Q10 (Ecosystem, Easy).** As of 2026, which body governs MCP, and how does it relate to A2A?
- A. MCP is proprietary to Anthropic; A2A is unrelated
- B. Both are Linux Foundation projects (MCP under the AAIF); MCP connects agents to tools/systems while A2A connects agents to each other ✅
- C. MCP and A2A are the same protocol under two names
- D. A2A governs MCP as a sub-specification

Rationale: Anthropic donated MCP to the AAIF (Dec 2025); A2A (originally Google) is also LF-stewarded; the two compose rather than compete.

## Notes on currency

Version-sensitive facts to re-verify when the 2026-07-28 spec goes final (RC locked 2026-05-21; not final as of 2026-06-23):

- **Stateless core.** Removal of `initialize`/`initialized` and `Mcp-Session-Id`; `_meta`-carried version/capabilities; `server/discover`. All RC, could shift before final. Modules 8 and 9 and Q4 depend on this.
- **Deprecations.** Roots, Sampling, Logging deprecation (SEP-2577) and the 12-month window. Confirm they ship as final. Affects module 6 and Q6.
- **New extensions.** MCP Apps (SEP-1865), Tasks redesign, Extensions framework (SEP-2133). Exact APIs (`tasks/get|update|cancel`, `tasks/list` removal) may change.
- **Authz hardening SEPs.** `iss`/RFC 9207 (SEP-2468), credential-to-AS binding (SEP-2352), `.well-known` suffix (SEP-2351). Currently draft/authorization; verify against the final authorization spec page.
- **Error-code change.** Missing-resource `-32002` to `-32602` (SEP-2164). RC only.
- **JSON Schema 2020-12** for tool/output schemas (SEP-2106). RC only.
- **SDK tiers.** Tier assignments (TS/Python/C#/Go = Tier 1; Java/Rust = Tier 2; Swift/Ruby/PHP = Tier 3; Kotlin TBD) and the conformance-suite scoring may move; TypeScript v2 expected Q3 2026.
- **Adoption numbers** (~97M monthly downloads, >10,000 servers) are point-in-time marketing figures, not spec facts. Refresh before quoting.

## Claims not fully pinned to a primary/normative source (flag before exam publish)

- The exact `server/discover` method name and the precise `_meta` field layout come from the official RC blog post summary, not yet from a published normative spec page. Verify against the final spec text.
- OWASP MCP Top 10 item titles were read from the OWASP project page rendering; the IDs are labeled both `MCP01:2025` and informally "2026" across sources. Confirm the canonical numbering/year on owasp.org at exam-publish time.
- NSA CSI page count and identifier came from secondary summaries plus the press release; the PDF on defense.gov is authoritative for the recommendations. Re-read the PDF directly before citing specifics verbatim.
