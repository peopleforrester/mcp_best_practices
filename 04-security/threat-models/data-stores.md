<!-- ABOUTME: STRIDE threat model for the data stores and downstream resources trust zone of an MCP deployment.
ABOUTME: Maps each threat to an OWASP MCP Top 10 ID and an NSA CSI recommendation with a concrete mitigation. -->

# Threat Model: Data Stores and Downstream Resources

This zone covers the databases, file systems, internal APIs, and third-party services that an MCP server's tools read from and write to on behalf of the agent. The agent never touches these resources directly; it reaches them only by calling server tools, so every threat here is realized through a tool invocation. This is where the real damage happens: data loss from destructive writes, data exfiltration to attacker-controlled endpoints, and silent over-disclosure of records the requesting principal was never entitled to see. The core concern is outbound network behavior and downstream blast radius, because a single over-scoped credential or unfiltered egress path turns a successful prompt injection upstream into permanent loss or leakage here.

## STRIDE

### Spoofing

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| The server presents a single shared service account to a downstream database or API, so all tool calls appear to originate from one identity and the data store cannot tell which user or session acted. | MCP07 Insufficient Authn/Authz | 2 | Mint least-privilege per-action credentials scoped to the requesting principal; propagate the verified caller identity into the downstream connection (per-user DB role, scoped API token) so the data store authenticates the real actor, not a god account. |
| A tool is pointed at an attacker-substituted downstream endpoint (typosquatted host, hijacked DNS, look-alike internal API) and the server trusts it implicitly. | MCP10 Context Injection & Over-Sharing | 3 | Pin downstream resource URLs and access methods in the policy gateway's egress allowlist; route all outbound traffic through the filtering proxy so unpinned hosts are refused before a connection opens. |

### Tampering

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A write-capable tool is driven (by injected instructions or scope creep) to corrupt or overwrite records the workflow never intended to mutate. | MCP02 Privilege Escalation via Scope Creep | 4 | Gate every write/destructive tool behind human-in-the-loop confirmation via elicitation; validate parameters against schema in the gateway and reject ambiguous or user-sourced fields before the write reaches the data store. |
| Untrusted content ingested from a downstream source (a record field, a fetched document) is written back into a trusted store unsanitized, persisting a payload that later drives indirect injection. | MCP03 Tool Poisoning | 7 | Treat every downstream read as untrusted input to the next stage; run it through guardrails (content sanitization, injection-pattern detection) before it is persisted or fed back to the model. |

### Repudiation

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A destructive or exfiltrating tool call lands on a downstream system with no record tying the action to a principal, parameters, and result, so the event cannot be reconstructed or attributed. | MCP08 Lack of Audit & Telemetry | 8 | Emit SIEM-ready JSON audit logs from the policy gateway for every tool invocation: caller identity, tool name, parameters, downstream target, and a result hash, correlated by trace context across the call. |

### Information disclosure

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A read tool returns far more than the request needed (full table dumps, adjacent tenants' rows, fields the principal has no entitlement to), over-sharing sensitive context into the model's window. | MCP10 Context Injection & Over-Sharing | 4 | Scope queries server-side with row- and column-level filters tied to the caller; run results through guardrails with PII redaction before they leave the server; design search-focused tools that return narrow result sets rather than list-all tools. |
| The exfiltration leg of the lethal trifecta: private data read from a downstream store is shipped to an attacker-controlled external endpoint by a tool with outbound network access. | MCP10 Context Injection & Over-Sharing | 3 | Cut the exfiltration channel with network egress control: a filtering outbound proxy or DLP that only permits pinned downstream hosts (NSA rec 3), enforced by the policy gateway's egress allowlist so data cannot leave to an unapproved destination. |
| A downstream credential, connection string, or API key is exposed through a tool error message, log line, or returned field. | MCP01 Token Mismanagement & Secret Exposure | 8 | Hold downstream secrets in the server's secret store, never in tool inputs or outputs; scrub secrets from errors and logs in the gateway; verify the audit pipeline never persists raw credential material. |

### Denial of service

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| An unbounded or repeated tool call exhausts a downstream resource (connection pool saturation, expensive unfiltered queries, third-party API rate-limit lockout), denying service to other consumers of that store. | MCP02 Privilege Escalation via Scope Creep | 4 | Enforce per-tool and per-principal rate limits and query/result bounds (pagination, row caps, timeouts) at the gateway; validate parameters so unbounded scans are rejected before they reach the data store. |

### Elevation of privilege

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A tool runs against a downstream system with a credential broader than the action requires (write grant where read suffices, admin role on a shared key), so any compromise of that tool inherits the full credential's blast radius. | MCP02 Privilege Escalation via Scope Creep | 2 | Issue least-privilege per-action credentials: read-only roles for read tools, narrowly scoped write grants for write tools, separate downstream identities per tool so a single compromised tool cannot pivot across the data store's full surface. |
| A foreign or passed-through token is reused to reach a downstream system it was never audience-scoped for (confused deputy), letting a low-privilege caller act with a higher-privilege downstream identity. | MCP07 Insufficient Authn/Authz | 2 | Forbid token passthrough; the server exchanges the validated, audience-bound caller token (RFC 8707) for a downstream credential scoped to that principal, demonstrated in the OAuth confused-deputy demo, never forwarding the inbound token to the data store. |

## Data-store-specific notes

- **Exfiltration leg of the lethal trifecta.** This zone is where the trifecta (private data + untrusted content + an exfiltration channel) is consummated. Upstream defenses reduce the odds of injection, but the data store is the sink: if a tool can both read private data and reach an arbitrary external host, one successful injection is a leak. Removing either capability from any single tool breaks the trifecta. The egress allowlist is the cheapest place to break it.
- **Network egress control (NSA rec 3).** Default-deny outbound. Route all server-initiated downstream traffic through a filtering proxy or DLP with downstream resource URLs and access methods pinned tightly. An unpinned destination is refused, so data has nowhere to be exfiltrated to even when a tool is hijacked. The policy gateway owns the egress allowlist and logs every allow/deny.
- **Least-privilege per-action credentials.** Each tool gets a downstream identity scoped to exactly what that action needs: read tools get read-only roles, write tools get narrow write grants, and no tool shares a high-privilege key. This bounds the blast radius of any single compromised tool and supports per-principal attribution at the data store.
- **Data over-sharing / context oversharing (MCP10).** A read tool that returns more than the request needs leaks data into the model context and, by extension, into anything downstream of the model. Scope queries server-side to the caller's entitlements, redact PII in guardrails before results leave the server, and prefer narrow search tools over list-all tools.
- **Write and destructive operations need human-in-the-loop confirmation.** Any tool that mutates or deletes downstream data should require explicit user confirmation through elicitation, with the target and parameters shown to the user before the action commits. Pair this with the `destructiveHint` annotation, but treat the annotation as advisory: the gateway, not the hint, enforces the confirmation gate.

**Residual risk.** Even with egress allowlisting, least-privilege credentials, write confirmation, and PII redaction in place, an authorized read tool operating within its scope can still return more than a given workflow strictly required, and a downstream system trusted in the allowlist can itself be compromised; both leave a leakage path that controls in this zone narrow but do not fully close.
