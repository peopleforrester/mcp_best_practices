<!-- ABOUTME: STRIDE threat model for the MCP client trust zone (one connector per server, embedded in the host).
ABOUTME: Maps client-specific threats to OWASP MCP Top 10 IDs and NSA CSI recommendations with concrete mitigations. -->

# Threat Model: MCP Client

The MCP client is the per-server connector the host instantiates: one client object per connected server, bound to that server's lifecycle. It negotiates the capability map during the `initialize` handshake (or, under the 2026-07-28 RC, advertises version and capabilities inline via `_meta` and `server/discover`), drives `tools/call` and `resources/read`, owns the transport (stdio for local processes, Streamable HTTP for remote), and runs the OAuth 2.1 + PKCE flow that produces the access token a remote server expects. Because the client sits between a trusted host and a server that the NSA CSI says must be treated as a separate, untrusted trust zone (recommendation 2), it is the enforcement point for what the host will believe and what credentials the host will release. This model assumes the 2025-11-25 baseline and flags RC deltas inline.

## STRIDE

### Spoofing

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Client connects to an impostor server (typosquatted package, hijacked endpoint, or a shadow server that registered the same name) and treats its identity as established. | MCP09 | 1 | Resolve servers only through the signed registry; verify the cosign/sigstore signature and server-card provenance before the first `initialize`. Pin the canonical server URI used for OAuth `resource` so a substituted endpoint fails token audience binding. |
| Server spoofs a TLS or transport identity for a remote Streamable HTTP endpoint to harvest the OAuth token. | MCP07 | 6 | Enforce TLS with certificate validation; route remote connections through the policy gateway, which pins resource URLs (CSI rec 3) so the client never opens an unverified host. |

### Tampering

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Server mutates a previously approved tool definition after consent (rug pull): the client re-reads `tools/list` and silently uses the changed schema or description. | MCP03 | 7 | Hash each tool definition at approval time; the policy gateway re-checks the hash on every `tools/list` and requires fresh consent on drift. Treat list-changed notifications as a re-approval trigger, not an auto-accept. |
| Server-provided tool annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) are tampered to mislabel a destructive tool as read-only. | MCP03 | 4 | The spec states annotations are untrusted unless the server is trusted; the client must not relax confirmation based on an annotation alone. Guardrails enforce action class from the gateway policy, not from the annotation. |
| In-transit tampering of JSON-RPC messages on a path TLS does not cover end-to-end (proxy hop, local socket). | MCP05 | 6 | Per CSI rec 6, sign messages with expiration timestamps and replay protection where the deployment supports it; otherwise constrain the transport so no untrusted hop exists. |

### Repudiation

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Tool invocations and consent grants pass through the client without an auditable record, so a malicious or buggy server's actions cannot be attributed after the fact. | MCP08 | 8 | The policy gateway emits SIEM-ready JSON for every `tools/call` with parameters, the resolved server identity, the granting principal, and a result hash (CSI rec 8). Correlate with W3C Trace Context (`traceparent`) propagated in `_meta` under the RC. |

### Information disclosure

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Client sends an OAuth token scoped for server A to server B (token leaked across servers, or a confused-deputy where a proxy server relays the wrong audience). | MCP01 | 2 | Send RFC 8707 `resource` on both authorization and token requests so the token is audience-bound to one canonical server URI; never reuse a token across clients/servers. The oauth-confused-deputy demo shows the passthrough anti-pattern and the audience-bound fix. |
| Client echoes or logs the `MCP-Session-Id` (or RC inline session handle) and the OAuth bearer token in transcripts, debug output, or shared logs. | MCP01 | 8 | Treat the session id and tokens as secrets: never write them to model context, prompt history, or unredacted logs. Store tokens in the OS keychain or process memory, redacted at the log boundary. |
| Over-sharing: client forwards full server resource payloads into model context, exposing more data than the task needs. | MCP10 | 3 | Filter and minimize resource reads at the gateway; pin resource URLs and access methods (CSI rec 3) so the client cannot pull beyond the allowed scope. |

### Denial of service

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Server floods the client with oversized results, unbounded list pages, or rapid list-changed notifications, exhausting host memory or context budget. | MCP10 | 3 | Enforce client-side size and rate limits, paginate `*/list`, and cap result bytes per call at the gateway; drop or coalesce notification storms. |
| Resumability abuse: a malformed or hostile `Last-Event-ID` forces the server (or a buggy client) into repeated reconnection loops. | MCP08 | 9 | Bound reconnection attempts and validate that resumed event ids belong to the current session; on a 404 re-initialize cleanly rather than retrying indefinitely. Track and patch transport CVEs (CSI rec 9). |

### Elevation of privilege

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Capability-negotiation downgrade: a server lies about or withholds capabilities so the client falls back to a weaker mode (e.g., omitting structured output to force unvalidated text, or advertising a lower protocol version to dodge newer security requirements). | MCP06 | 2 | Treat the negotiated capability map as a security boundary: refuse to call anything not jointly negotiated, reject protocol-version downgrades below the host's required floor, and fail closed when a server omits an expected capability. Under the RC, validate the `_meta`-carried version per request. |
| Scope creep: client accumulates broad OAuth scopes across step-up flows and reuses an over-privileged token for narrow tool calls. | MCP02 | 2 | Request least-privilege, per-action scopes; the gateway enforces per-tool token scoping (CSI rec 2) and rejects calls whose token grants more than the action needs. |
| Confused-deputy escalation: client is coerced (via injected tool output or a crafted server prompt) into invoking a high-privilege tool on the user's behalf. | MCP06 | 7 | Treat every tool/model output as untrusted input to the next stage (CSI rec 7); guardrails screen tool results for injected instructions, and destructive actions require explicit human confirmation independent of any server-supplied annotation. |

## Client-specific notes

- **Capability negotiation downgrade and lying.** The handshake commits both sides to a capability map; a client must never call a tool a server did not declare, and equally must not let a server suppress a capability to escape a control. Pin a minimum protocol version and fail closed on omission. The RC removes the handshake and carries version/capabilities in `_meta` per request (SEP-2567/SEP-2575), which moves this check from once-per-session to every request: validate it each time.
- **Untrusted tool annotations.** Annotations are hints, not guarantees. The 2025-11-25 spec is explicit that annotations are untrusted unless they come from a trusted server, so a `readOnlyHint: true` from an unverified server must not relax confirmation, sandboxing, or audit. Derive action class from gateway policy and from schema validation (CSI rec 4), not from the server's self-description.
- **Transport gaps.** A local Streamable HTTP server bound to a predictable port is reachable by any web page in the user's browser; DNS rebinding lets a malicious site re-point a hostname at `127.0.0.1` and drive the local MCP endpoint. Mitigate with Origin-header validation, binding to loopback only, and rejecting requests whose `Host`/`Origin` do not match the expected local identity. CVE-2025-49596 (MCP Inspector, CVSS 9.4, fixed in 0.14.1) is the canonical instance of this class: an unauthenticated local endpoint that let a browser-driven request launch MCP commands over stdio. Clients that embed or ship inspector-style debug servers inherit the same exposure.
- **Token handling.** The `MCP-Session-Id` is session-bearing state, not a secret to broadcast: never echo it into model context or logs, and treat it as one more credential at the redaction boundary. OAuth tokens are audience-bound by construction (RFC 8707 `resource`), and the client is responsible for keeping them that way: one token per server audience, no passthrough to a downstream or sibling server, no reuse across clients. Token passthrough is forbidden by the authorization spec precisely because it defeats audience validation and least privilege.

## Residual risk

A client that verifies provenance, refuses downgrades, ignores untrusted annotations, audience-binds tokens, and validates transport origins still inherits residual risk from a fully trusted-but-compromised server, from prompt-injection content that survives guardrail screening, and from transport hops where message signing (CSI rec 6) is not deployed; these are reduced, not eliminated, and are carried forward to the server and host models.
