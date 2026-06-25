<!-- ABOUTME: Sourced, defensible answer-key content for the MCP practice exam across five domains, with scenario questions and distractors.
ABOUTME: Verifies the repo's 12-question bank against official sources; flags revise/drop items. Re-verify RC-only facts when the 2026-07-28 spec is final. -->

# MCP Practice Exam: Verified Question Content (spike 2026-06-25)

Sourced against official/authoritative material only: modelcontextprotocol.io stable
`2025-11-25` spec pages, the `2026-07-28` Release Candidate blog, owasp.org MCP Top 10,
the NSA AISC CSI (press release plus PDF summaries; the PDF itself 403s automated
fetchers), IETF RFC 8707, the A2A protocol site, and the AAIF / Linux Foundation
governance posts.

Stable baseline is `2025-11-25`. The `2026-07-28` revision is a **Release Candidate**
(locked 2026-05-21, final 2026-07-28). Every RC-only fact below is labeled `[RC]` and
must be re-verified at GA before it appears on a published exam.

A label of `[CONFIRMED]` means the fact is quoted or paraphrased from a primary
normative source. `[PARAPHRASE]` means the source is authoritative but the wording is a
secondary summary (used only for the NSA CSI, whose PDF cannot be fetched directly).

---

## Domain 1: Fundamentals (message layer, lifecycle, mental model)

### Load-bearing facts

1. MCP encodes messages with JSON-RPC 2.0; messages **MUST** be UTF-8 encoded. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
2. MCP is an open protocol connecting AI applications (hosts) to external tools, data,
   and systems through clients and servers. Hosts run one or more clients; each client
   connects to one server. `[CONFIRMED]` https://modelcontextprotocol.io/
3. A client cannot use a capability the server never declared; client and server each
   advertise capabilities and commit only to what was negotiated. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/server/tools (server **MUST**
   declare the `tools` capability)
4. Over HTTP, the client **MUST** send `MCP-Protocol-Version` on every request after
   initialization; if absent, the server **SHOULD** assume `2025-03-26`; an invalid
   version gets `400 Bad Request`. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
5. MCP was created by Anthropic and first released November 2024; `2025-11-25` was the
   first-anniversary stable revision. `[CONFIRMED]`
   https://blog.modelcontextprotocol.io/posts/2025-11-25-first-mcp-anniversary/

### Misconceptions / near-miss distractors

- "MCP uses a custom binary wire format" or "gRPC at the message layer." Wrong: it is
  JSON-RPC 2.0 over a transport. gRPC is plausible because people associate it with RPC.
- "JSON-RPC messages may use any Unicode encoding." Wrong: UTF-8 is mandated. UTF-16 is
  the trap because it is also Unicode.
- "MCP is one-to-one host-to-server." Wrong: a host runs multiple clients, each bound to
  one server; the host aggregates many servers.
- "Capability negotiation is advisory; a client may call any method." Wrong: negotiated
  capabilities gate what each side may use.
- "The `MCP-Protocol-Version` default when missing is `2025-11-25`." Wrong: the spec says
  fall back to `2025-03-26`. This is a precise near-miss.

### Scenario questions

**F-S1 (Medium).** A developer's HTTP MCP client omits the `MCP-Protocol-Version` header
on requests after initialization, and the server has no record of a negotiated version.
Per the 2025-11-25 spec, how should the server behave?

- A. Reject every request with `400 Bad Request` until the header is supplied
- B. Assume protocol version `2025-03-26` and proceed *(correct)*
- C. Assume the latest version it supports
- D. Close the connection and require a fresh `initialize`

Rationale: The transport spec says when the server does not receive an
`MCP-Protocol-Version` header and has no other way to identify the version, it **SHOULD**
assume `2025-03-26`. A is the response to an *invalid* version, not a *missing* one. C and
D contradict the documented fallback. Source: 2025-11-25 transports.

**F-S2 (Easy/Medium).** A server logs human-readable debug lines and also returns
JSON-RPC results. Over stdio, where may the server write those debug lines without
corrupting the protocol stream?

- A. Interleaved on stdout between JSON-RPC messages
- B. On stderr as UTF-8 strings *(correct)*
- C. In a `debug` field appended to each JSON-RPC response
- D. On stdout, base64-encoded so the client can skip it

Rationale: In stdio the server **MUST NOT** write anything to stdout that is not a valid
MCP message, and **MAY** write UTF-8 logging to stderr. A and D pollute stdout. C invents
a field. Source: 2025-11-25 transports (stdio).

---

## Domain 2: Architecture (transports, sessions, scaling, the RC)

### Load-bearing facts

1. Two standard transports: stdio and Streamable HTTP. Clients **SHOULD** support stdio
   whenever possible. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
2. Streamable HTTP **replaced** the HTTP+SSE transport from protocol version 2024-11-05.
   It uses one MCP endpoint supporting both POST and GET, with optional SSE. `[CONFIRMED]`
   same page.
3. Stateful sessions: the server **MAY** assign a session ID in the `MCP-Session-Id`
   response header on the `InitializeResult`; the client **MUST** then echo it on all
   subsequent requests. On HTTP 404 the client **MUST** start a new session with a fresh
   `InitializeRequest` (no session ID). `[CONFIRMED]` same page. (Note: the header name is
   `MCP-Session-Id` with that casing in the spec.)
4. Resumability: servers **MAY** attach an `id` to SSE events; the client resumes by
   issuing an HTTP GET with the `Last-Event-ID` header; the server replays only on the
   same stream. `[CONFIRMED]` same page.
5. `[RC]` Stateless core: the `initialize`/`initialized` handshake is removed (SEP-2575)
   and `Mcp-Session-Id`/protocol-level sessions are removed (SEP-2567). Protocol version,
   client info, and capabilities travel in `_meta` per request; a new `server/discover`
   method fetches server capabilities. Any request can land on any instance. `[CONFIRMED
   as RC]` https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
6. `[RC]` Server-to-client requests move from SSE to Multi Round-Trip Requests (SEP-2322,
   `InputRequiredResult` with `inputRequests`/`requestState`; client retries with
   `inputResponses`). `Mcp-Method`/`Mcp-Name` routing headers (SEP-2243). `[CONFIRMED as
   RC]` same blog.

### Misconceptions / near-miss distractors

- "WebSocket replaced HTTP+SSE." Wrong, and the most attractive distractor: Streamable
  HTTP is the replacement. WebSocket is not a standard MCP transport.
- "gRPC" or "long-polling" as the replacement transport. Plausible-sounding, both wrong.
- "The session ID rides a URL query string / a JSON-RPC param / the SSE `retry` field."
  Wrong: it is the `MCP-Session-Id` HTTP header.
- "On a 404 the client retries the same session ID." Wrong: 404 means the session is gone;
  the client **MUST** re-initialize without a session ID.
- `[RC]` "In the stateless core, version/capabilities ride the `Mcp-Session-Id` header on
  each request." Wrong and self-contradicting: sessions are removed; data rides `_meta`.
- `[RC]` "The RC is the current stable spec." Wrong: `2025-11-25` is stable; the RC is not
  final.

### Scenario questions

**A-S1 (Medium).** A horizontally scaled Streamable HTTP deployment (2025-11-25) puts
several server replicas behind a load balancer. A client initializes, gets a session ID,
then its next request is routed to a *different* replica that has no record of that
session and returns 404. What must a spec-compliant client do, and what is the underlying
fix for the deployment?

- A. Retry the same request with the same `MCP-Session-Id`; the LB will eventually hit the
  right replica
- B. Start a new session with a fresh `InitializeRequest` and no session ID; fix the
  deployment with sticky routing or a shared session store *(correct)*
- C. Downgrade to the HTTP+SSE transport, which is stateless
- D. Move the session ID into a URL query parameter so any replica can read it

Rationale: 404 on a session-bearing request means the client **MUST** re-initialize
without a session ID (2025-11-25 transports). Stateful Streamable HTTP needs sticky
routing or a shared session store across replicas. A ignores the spec. C is false (HTTP+SSE
is not "stateless" and is deprecated). D is not how the spec carries the session ID.
Sources: 2025-11-25 transports; RC blog (which removes sessions precisely to avoid this).

**A-S2 (Hard) `[RC]`.** A team wants any MCP request to land on any stateless replica with
no sticky routing and no shared session store. Which 2026-07-28 RC change makes this
possible at the protocol layer?

- A. A mandatory `Mcp-Session-Id` header that every replica validates against a shared store
- B. Removal of the initialize handshake and protocol-level sessions; version, client info,
  and capabilities travel in per-request `_meta`, with `server/discover` for capabilities
  *(correct)*
- C. A WebSocket upgrade that pins each client to one replica
- D. TLS client-certificate pinning that encodes the session

Rationale: The RC stateless core (SEP-2575 removes the handshake, SEP-2567 removes
sessions) lets any instance serve any request because per-request `_meta` carries the
context. A reintroduces the session it removed. C/D are inventions. Label `[RC]`: not
final. Source: RC blog.

---

## Domain 3: Tooling (primitives, SDK usage)

### Load-bearing facts

1. A tool has a unique `name`, a `description`, and an `inputSchema` (a valid JSON Schema
   object, defaulting to 2020-12). Discovery is `tools/list`; invocation is `tools/call`.
   `[CONFIRMED]` https://modelcontextprotocol.io/specification/2025-11-25/server/tools
2. Clients **MUST** consider tool annotations (for example `destructiveHint`,
   `readOnlyHint`) to be untrusted unless they come from trusted servers. Annotations
   describe behavior; they are not enforced guarantees. `[CONFIRMED]` same page.
3. Tools are model-controlled, but there **SHOULD** always be a human in the loop able to
   deny invocations. `[CONFIRMED]` same page.
4. Sampling (`sampling/createMessage`) lets a server request LLM completions *through the
   client*, so the client controls model access and no server API keys are needed. There
   **SHOULD** always be a human able to deny sampling requests. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
5. Client-side primitives are sampling, roots, and elicitation; each is gated behind
   capability declaration (for example clients supporting sampling **MUST** declare the
   `sampling` capability). `[CONFIRMED]` sampling page.
6. `[RC]` Roots, Sampling, and Logging are annotation-only deprecations under a new
   lifecycle policy (SEP-2577); they keep working for at least 12 months. Suggested
   replacements: sampling to direct LLM provider API integration; logging to stderr or
   OpenTelemetry. `[CONFIRMED as RC]`
   https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/

### Misconceptions / near-miss distractors

- "`destructiveHint` is an enforced guarantee the server cannot violate." Wrong, and the
  best distractor: annotations are advisory and untrusted from untrusted servers.
- "Sampling means the server runs its own model with its own API keys." Exactly backwards:
  the point of sampling is the *client* owns the model and keys.
- "Resources or Prompts let a server request inference." Wrong primitive: that is Sampling.
  Resources are read-only URI-addressed context; Prompts are parameterized templates.
- "Roots is how a server requests inference." Wrong: Roots scopes filesystem/URI access.
- `[RC]` "Sampling was removed in the RC." Wrong precision trap: it is *deprecated*
  (annotation-only), still functional for at least 12 months, not removed.

### Scenario questions

**T-S1 (Medium).** A connected (but not independently audited) MCP server exposes a
`delete_records` tool whose annotations claim `readOnlyHint: true` and
`destructiveHint: false`. How must a well-behaved client treat those annotations?

- A. As guarantees: skip the confirmation prompt because the tool is marked read-only
- B. As untrusted hints, since the server is not trusted; still apply destructive-action
  safeguards and keep a human in the loop *(correct)*
- C. As required fields the client validates for schema correctness only
- D. As client-only metadata the server never actually sees

Rationale: Clients **MUST** consider annotations untrusted unless from trusted servers,
and tools **SHOULD** keep a human in the loop. A trusts attacker-supplied metadata, the
exact failure annotations warn against. C and D misstate what annotations are. Source:
2025-11-25 server/tools.

**T-S2 (Medium).** A server wants to summarize a document using an LLM but must hold no
model API keys of its own and must let the user review the prompt first. Which MCP
primitive fits, and what control is required?

- A. Resources, with the client auto-approving reads
- B. Sampling via `sampling/createMessage`, with a human-in-the-loop able to review and
  deny the request *(correct)*
- C. Prompts, which execute inference server-side
- D. Roots, which grant the server model access scoped to a directory

Rationale: Sampling routes inference through the client (no server keys) and **SHOULD**
keep a human able to deny the request. Resources are read-only data, Prompts are templates
(no inference), Roots is URI scoping. Source: 2025-11-25 client/sampling. (If used on an
RC-aligned exam, add a note that sampling is deprecated in the RC.)

---

## Domain 4: Security (authorization, OAuth 2.1, RFC 8707)

### Load-bearing facts

1. Authorization is **OPTIONAL** in MCP; when used over HTTP the MCP server acts as an
   OAuth 2.1 resource server and the client as an OAuth 2.1 client. `[CONFIRMED]`
   https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization
2. MCP clients **MUST** implement RFC 8707 Resource Indicators: the `resource` parameter
   **MUST** be sent on both authorization and token requests, **MUST** identify the target
   MCP server, and **MUST** use the server's canonical URI. The client **MUST** send it
   even if the authorization server does not support it. `[CONFIRMED]` same page.
3. Servers **MUST** validate that tokens were issued specifically for them (audience), and
   **MUST** reject tokens not issued for them. `[CONFIRMED]` same page.
4. Token passthrough is explicitly forbidden: servers **MUST NOT** accept or transit
   tokens not issued for them, and when calling upstream APIs **MUST NOT** pass through the
   client's token; clients **MUST NOT** send tokens other than ones issued by the server's
   authorization server. The failure this prevents is audience-validation breakage feeding
   a confused-deputy condition. `[CONFIRMED]` same page.
5. RFC 8707 itself: the `resource` parameter is an absolute URI that audience-restricts the
   issued token, preventing token replay across services. `[CONFIRMED]`
   https://datatracker.ietf.org/doc/html/rfc8707
6. Clients **MUST** implement PKCE with `S256`; MCP servers **MUST** implement RFC 9728
   Protected Resource Metadata for authorization-server discovery. `[CONFIRMED]` 2025-11-25
   authorization.

### Misconceptions / near-miss distractors

- "RFC 8707 prevents DNS rebinding / prompt injection / SSE replay." Wrong: those are real
  MCP concerns addressed elsewhere (Origin validation, tool-description trust, stream
  resumability). RFC 8707 binds token audience to defeat confused-deputy / token reuse.
  These adjacent-but-wrong options are strong distractors.
- "Token passthrough is forbidden because it bloats payloads / breaks caching / OAuth 2.1
  lacks refresh tokens." All false rationales; the real reason is audience validation and
  least privilege.
- "Authorization is mandatory in MCP." Wrong: it is OPTIONAL; stdio implementations
  **SHOULD NOT** use it and instead read credentials from the environment.
- "DNS-rebinding defense is the `resource` parameter." Wrong: that is `Origin` header
  validation plus localhost binding (a transport-layer control, not authorization).
- "The MCP server forwards the client's token to upstream APIs." Wrong: the server gets a
  *separate* token from the upstream AS; passing the client token through is forbidden.

### Scenario questions

**S-S1 (Hard).** An MCP server proxies to a high-privilege internal billing API. An
attacker obtains a token that a *different*, low-privilege service issued and presents it
to the billing MCP server. Which spec-mandated control stops this, and how?

- A. `Origin` header validation, by rejecting cross-origin browser requests
- B. RFC 8707 audience binding plus server-side audience validation: the server **MUST**
  reject a token not issued for it as the intended audience *(correct)*
- C. PKCE `S256`, by preventing authorization-code interception
- D. SSE resumability, by replaying only on the originating stream

Rationale: The attack is token reuse across audiences (a confused-deputy setup). RFC 8707
binds the token to a resource and the server **MUST** validate it was issued for itself.
A defends against DNS rebinding, not token reuse. C protects the code exchange. D is a
transport concern. Sources: 2025-11-25 authorization; RFC 8707.

**S-S2 (Medium).** An MCP server needs to call an upstream SaaS API on the user's behalf.
A developer proposes forwarding the same access token the MCP client presented. Why does
the spec forbid this, and what is the compliant alternative?

- A. It is allowed if the token has not expired; just check expiry first
- B. Forbidden: the server **MUST NOT** pass through the client's token; it must obtain a
  separate token from the upstream authorization server, acting as an OAuth client to it
  *(correct)*
- C. Forbidden only because forwarding inflates the JSON-RPC payload
- D. Forbidden because OAuth 2.1 removed refresh tokens, so the token cannot be reused

Rationale: The server **MUST NOT** pass through the received token; the upstream call uses
a separate token issued by the upstream AS. Passthrough breaks audience validation and can
create a confused deputy. A permits the forbidden behavior. C and D give fabricated
reasons (OAuth 2.1 keeps refresh tokens). Source: 2025-11-25 authorization.

---

## Domain 5: Security frameworks and ecosystem (OWASP, NSA, governance, A2A)

### Load-bearing facts

1. OWASP MCP Top 10 canonical IDs use the `MCP##:2025` format. MCP03:2025 is **Tool
   Poisoning**, officially defined as occurring "when an adversary compromises the tools,
   plugins, or their outputs that an AI model depends on" (broader than description-only
   injection). Project status: Beta / Pilot Testing (Phase 3). `[CONFIRMED]`
   https://owasp.org/www-project-mcp-top-10/
   - The ten: MCP01 Token Mismanagement & Secret Exposure; MCP02 Privilege Escalation via
     Scope Creep; MCP03 Tool Poisoning; MCP04 Software Supply Chain Attacks & Dependency
     Tampering; MCP05 Command Injection & Execution; MCP06 Intent Flow Subversion; MCP07
     Insufficient Authentication & Authorization; MCP08 Lack of Audit and Telemetry; MCP09
     Shadow MCP Servers; MCP10 Context Injection & Over-Sharing.
2. NSA AISC CSI "Model Context Protocol (MCP): Security Design Considerations for AI-Driven
   Automation" (U/OO/6030316-26, May 2026 v1.0). Core concern: the protocol reverses the
   familiar pattern (servers query and act for clients), authentication is optional, and
   RBAC is not part of the protocol. `[CONFIRMED]` press release:
   https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/
3. NSA recommended mitigations: treat every session as untrusted until verified;
   least-privilege per-action/per-tool tokens; signed provenance for dynamically discovered
   servers; outbound filtering proxy and registry pinning; audit logging on all tool/model
   invocations. `[PARAPHRASE]` (PDF 403s automated fetchers; wording from press release and
   CSI summaries). PDF: https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF
4. Governance: Anthropic donated MCP to the Agentic AI Foundation (AAIF), a directed fund
   under the Linux Foundation, announced December 9, 2025. MCP's maintainer-led technical
   governance is unchanged; the AAIF board handles strategy/budget/membership. `[CONFIRMED]`
   https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
   and https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/
5. A2A (Agent2Agent) originated at Google, was donated to the Linux Foundation, and handles
   agent-to-agent communication; MCP handles agent-to-tool. They compose rather than
   compete. `[CONFIRMED]` https://a2a-protocol.org/latest/

### Misconceptions / near-miss distractors

- "Tool Poisoning means overloading a server with calls / registering duplicate names /
  exhausting a rate limit." All wrong; those describe DoS or naming collisions, not the
  OWASP definition (compromising tools, plugins, or their outputs).
- "Tool Poisoning is *only* malicious text in a tool description." This is the repo's
  current framing. It is a common *instance* but narrower than the official MCP03 wording.
  A defensible exam should not present the narrow definition as the whole of MCP03.
- "MCP remains proprietary to Anthropic." Wrong since December 2025 (AAIF/LF).
- "A2A governs MCP" or "MCP and A2A are the same protocol." Wrong: distinct, complementary
  LF projects.
- "The NSA CSI says to allow all outbound traffic / disable auth for internal servers /
  trust TLS alone." All contradict the CSI; they are good distractors precisely because
  each inverts a real recommendation.
- "MCP has built-in RBAC." Wrong, and a key NSA point: RBAC is not in the protocol.

### Scenario questions

**E-S1 (Medium/Hard).** A platform team is hardening external MCP connections per the NSA
AISC CSI. The CSI flags that MCP authentication is optional and the protocol has no
built-in RBAC. Which posture aligns with the CSI's recommendations?

- A. Allow all outbound traffic so any discovered tool stays reachable
- B. Treat each session as untrusted until verified, issue least-privilege per-tool tokens,
  pin the server registry, and route egress through a filtering proxy with audit logging
  *(correct)*
- C. Disable authentication for servers on the internal network to reduce friction
- D. Rely on TLS for trust, since transport encryption authenticates the server

Rationale: The CSI's mitigations are untrusted-by-default sessions, least-privilege tokens,
signed provenance / registry pinning, outbound filtering, and audit logging. A, C, and D
each invert one of those. Source: NSA CSI (press release + summaries). Label the verbatim
recommendation wording as paraphrase until the PDF is re-read directly.

**E-S2 (Medium).** An architect must let a specialized internal agent both use a database
tool and delegate subtasks to a separate fraud-analysis agent built on another framework.
Which protocols fit which job?

- A. MCP for both, since MCP covers agent-to-agent too
- B. MCP to connect the agent to the database tool; A2A to let it collaborate with the
  other agent across frameworks *(correct)*
- C. A2A for both, since A2A subsumes tool access
- D. Neither; this requires a single proprietary Anthropic protocol

Rationale: MCP is agent-to-tool; A2A is agent-to-agent; they compose. A and C overstate one
protocol's scope. D is false since MCP is an open LF project and A2A exists. Sources:
a2a-protocol.org; AAIF governance posts.

---

## Verdict on the repo's current 12 questions

Scored for answer defensibility, distractor plausibility, recall-vs-application, and
RC-currency risk.

| ID | Domain | Verdict | Reason |
|----|--------|---------|--------|
| q-transport-streamable | architecture | **Keep** | Answer (Streamable HTTP replaced HTTP+SSE) is directly confirmed; distractors (WebSocket/gRPC/long-polling) are plausible and all wrong. Solid. |
| q-rfc8707-purpose | security | **Keep** | Confused-deputy / audience-binding answer is confirmed; distractors are real adjacent MCP concerns (DNS rebinding, prompt injection, SSE replay). One of the best items in the bank. |
| q-token-passthrough | security | **Revise (minor)** | Answer is correct and confirmed. But add that authorization is OPTIONAL in MCP so the stem is not misread as "always required." Distractor "OAuth 2.1 has no refresh tokens" is factually false (OAuth 2.1 keeps refresh tokens) which makes it an implausible throwaway. Consider swapping it for a plausible-but-wrong rationale such as "to keep tokens out of server logs." |
| q-rc-stateless-core | architecture | **Keep, keep `[RC]` label** | Matches the RC blog (SEP-2575/2567, per-request `_meta`, `server/discover`). The stem already flags the RC. Re-verify method/field names at GA. Distractor C says `Mcp-Session-Id` which the RC removes, a clean trap. |
| q-json-encoding | fundamentals | **Keep** | UTF-8 requirement directly confirmed. Easy recall item, appropriate for the difficulty mix. |
| q-sampling-primitive | tooling | **Keep (watch RC note)** | Sampling-as-client-delegation is confirmed; distractors (Resources/Prompts/Roots) are the right near-misses. Rationale's "deprecated in the RC" is correct but RC-only; keep it in the rationale, not the answer. |
| q-tool-poisoning | security | **Revise** | The answer ("embedding malicious instructions in a tool's description") is the *narrow* reading. OWASP MCP03 is officially broader: "an adversary compromises the tools, plugins, or their outputs that an AI model depends on." Description injection is a common instance, not the definition. Either broaden the correct option to match OWASP wording, or reframe the stem as "Which is an example of tool poisoning (MCP03)?" so the narrow answer is defensible. As written, a knowledgeable test-taker can argue the option is incomplete. |
| q-nsa-egress | security | **Keep (flag source)** | Posture (filtering outbound proxy/DLP, untrusted-until-verified) matches the CSI summaries and press release. Mark internally that the verbatim CSI wording is paraphrase (PDF 403s fetchers); the recommendation substance is sound. Distractors invert real recommendations. Good item. |
| q-session-id-mechanics | architecture | **Keep (fix header casing)** | Mechanics confirmed (`MCP-Session-Id` on `InitializeResult`, client echoes, 404 to re-init). The spec uses casing `MCP-Session-Id`; the option text uses `Mcp-Session-Id`. Harmonize to the spec casing for defensibility. Otherwise strong. |
| q-governance-a2a | ecosystem | **Keep** | AAIF/LF governance and MCP-vs-A2A composition are confirmed. Distractors are clean. Note "Dec 2025" donation date in the rationale is correct (Dec 9, 2025). |
| q-annotations-untrusted | tooling | **Keep** | "Advisory, untrusted unless from a trusted server" is a near-verbatim match to the spec **MUST** warning. Excellent, defensible item. |
| q-streamable-not-sse | fundamentals | **Revise (stem date)** | The claim is right (HTTP+SSE is the deprecated/legacy transport) but the stem's framing "legacy/deprecated as of 2025-03-26" is loose. HTTP+SSE dates from 2024-11-05 and was superseded by Streamable HTTP introduced in 2025-03-26. Reword to "Which transport did Streamable HTTP (introduced 2025-03-26) supersede?" so the date attaches to the right event. Answer (HTTP+SSE) stays. Also note this item overlaps heavily with q-transport-streamable; consider differentiating or dropping one to avoid redundancy. |

### Summary of flags

- **Revise:** q-token-passthrough (weak/false distractor; add OPTIONAL-auth context),
  q-tool-poisoning (narrow vs official OWASP definition), q-streamable-not-sse (stem date
  framing plus redundancy with q-transport-streamable).
- **Minor fixes:** q-session-id-mechanics (header casing to `MCP-Session-Id`),
  q-nsa-egress (mark NSA wording as paraphrase pending direct PDF read).
- **Drop:** none outright. q-streamable-not-sse is the only drop *candidate* if the bank
  needs to shed redundancy with q-transport-streamable.
- **RC-dependent (re-verify at GA 2026-07-28):** q-rc-stateless-core, and the RC notes in
  q-sampling-primitive.

### Not confirmable from a primary source (flag before publishing)

- The exact `server/discover` method name and the precise `_meta` field layout come from
  the RC blog summary, not a published normative spec page. `[RC]`
- NSA CSI recommendation wording is paraphrased from the press release and secondary
  summaries; the defense.gov / nsa.gov PDFs return HTTP 403 to automated fetchers. The
  substance is corroborated across sources; verbatim quotes need a manual PDF read.
- OWASP MCP Top 10 IDs render as `MCP##:2025` on the project page even in 2026; confirm the
  canonical year label at publish time, since the project is still Beta (Phase 3).
- Adoption figures (97M+ monthly SDK downloads, connector counts) are vendor marketing
  numbers, point-in-time, not spec facts. Do not test them as fixed values.
