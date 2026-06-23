<!-- ABOUTME: STRIDE threat model for the MCP server trust zone (tools/resources/prompts, OAuth 2.1 resource server).
ABOUTME: Maps each threat to an OWASP MCP Top 10 ID and an NSA CSI recommendation with a security-track mitigation. -->

# Threat Model: MCP Server

The MCP server is the trust zone that exposes tools, resources, and prompts to clients and executes
tool logic against backing systems (databases, internal APIs, shell, filesystems). For remote
deployments it is an OAuth 2.1 Resource Server that must validate audience-bound access tokens per
RFC 8707. This model treats the server as a distinct trust zone (NSA CSI rec 2): everything inbound
from a client or the model is untrusted, and everything the server emits is untrusted input to the
next stage. It is written against the stable `2025-11-25` spec, with `2026-07-28` RC deltas flagged
inline as preview.

## STRIDE

### Spoofing

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A client presents a token that was issued for a different audience (or a self-minted/forged token) and the server accepts it, allowing an attacker to impersonate a legitimately authorized caller. | MCP07 Insufficient Authn/Authz | 2 | Validate the JWT signature, `iss`, `exp`, and `aud` on every request; reject any token whose `aud` is not this server's canonical URI (RFC 8707). Demonstrated in the `oauth-confused-deputy/` correct-flow path; enforced at the edge by the policy gateway before any tool dispatch. |
| A rogue process registers itself as a trusted server (shadow server) on a discovery surface and clients connect to it believing it is the real one. | MCP09 Shadow MCP Servers | 3 | Pre-connection validation against a `signed-registry/` entry: cosign-verified image digest and a `.well-known/mcp/server-card.json` whose identity matches the registry record before the client is allowed to connect. |

### Tampering

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A poisoned server image or a tampered dependency is deployed, altering tool behavior or tool descriptions after the supply chain (rug-pull / dependency tampering). | MCP04 Supply Chain & Dependency Tampering | 1 | cosign/sigstore keyless signing (Fulcio + Rekor) with SBOM and SLSA provenance attestations; admission verification via the `signed-registry/` so only signed digests run. Pin and audit dependencies; choose maintained projects. |
| Tool-call arguments or results are modified in transit, or a tool description carries hidden instructions the model then executes (tool poisoning). | MCP03 Tool Poisoning | 6 | TLS for transport integrity plus signed-and-timestamped MCP messages with replay protection (the protocol does not guarantee integrity beyond TLS); treat tool annotations as untrusted unless the server is trusted. `guardrails/` scans tool descriptions and results for injected directives. |

### Repudiation

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A tool invocation against a backing system (data write, command execution) occurs with no durable record, so an actor can deny having triggered it and incident reconstruction is impossible. | MCP08 Lack of Audit & Telemetry | 8 | SIEM-ready structured JSON audit log emitted by the policy gateway for every `tools/call`: caller identity (token subject), tool name, parameters, and a result hash. RC preview: W3C Trace Context (`traceparent`/`tracestate` in `_meta`, SEP-414) correlates the record end to end via OpenTelemetry. |

### Information disclosure

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Long-lived secrets, API keys, or downstream credentials are logged, embedded in tool descriptions, or returned in tool output, leaking from the server. | MCP01 Token Mismanagement & Secret Exposure | 8 | Short-lived per-action tokens, never static long-lived credentials; `guardrails/` output filtering with PII/secret redaction (Presidio) before results leave the server; audit logs record result hashes, not raw secret values. |
| A resource or tool returns more context than the caller's scope warrants (over-sharing), exposing data from another tenant or trust boundary. | MCP10 Context Injection & Over-Sharing | 4 | Scope reads at the resource layer to the caller's authorized URIs; the policy gateway applies per-client allow/deny; prefer local servers for private data and a filtering outbound proxy/DLP for egress (NSA rec 3 reinforces this). |

### Denial of service

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A malicious or buggy client floods `tools/call`, or a single tool argument drives an unbounded operation against a backing system, exhausting server or downstream capacity. | MCP05 Command Injection & Execution | 5 | Schema-enforced parameter bounds (NSA rec 4) plus per-client rate limiting and concurrency caps at the policy gateway; execute tool logic in a resource-capped sandbox (seccomp/AppArmor/SELinux, cgroup limits) so a single call cannot starve the host. |

### Elevation of privilege

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Crafted tool parameters break out of the intended operation into the underlying shell, path, or query (command/argument injection, path traversal), running attacker code with the server's privileges. | MCP05 Command Injection & Execution | 5 | Strict JSON Schema validation and allowlisting of parameter values (no string interpolation into shells); execute in a least-privilege sandbox (seccomp/AppArmor/SELinux) with no ambient credentials. The Anthropic Git MCP path-traversal/arg-injection class is the worked example in `guardrails/`. |
| Granted scopes accumulate across step-up or consent flows until a low-trust client holds broad privilege it was never meant to have (scope creep). | MCP02 Privilege Escalation via Scope Creep | 2 | Least-privilege, per-action/per-tool tokens; the policy gateway enforces a per-client consent registry and refuses scope accumulation. RC preview: scope-accumulation hardening on step-up (SEP-2350) and credential-to-AS binding (SEP-2352). |
| The server is handed a client's foreign-issued token and forwards it to a downstream system, acting as a confused deputy that exercises the downstream's trust in the server. | MCP01 Token Mismanagement & Secret Exposure | 2 | Token passthrough is forbidden: the server accepts only tokens issued for itself and obtains downstream access via token exchange, never by relaying the inbound token. Demonstrated end to end in `oauth-confused-deputy/`. |

## Server-specific notes

**Command and shell injection via tool parameters.** This is the dominant real-world MCP server bug.
Per Unit 42 (cited by Practical DevSecOps), over 30 CVEs were filed against MCP servers, clients, and
tooling between January and February 2026, of which about 43% were shell injections. Anthropic's own
Git MCP server had a path-traversal/argument-injection class disclosed in January 2026: tool
parameters that were concatenated into git invocations could escape the intended repository scope.
The structural fix is to never interpolate caller-supplied strings into a shell or a path, to pass
arguments as a validated argv array, and to validate every parameter against its JSON Schema before
the tool body runs (NSA rec 4). The `guardrails/` artifact carries this worked example.

**Token passthrough is forbidden, and why.** A server must validate that a token was issued for it
(audience match) and must not accept or transit tokens issued for another party. Forwarding a client
token downstream turns the server into a confused deputy: the downstream system trusts the server, so
a relayed token lets a caller reach resources its own grant never covered. RFC 8707 Resource
Indicators bind a token's audience to the canonical server URI (the client sends `resource` on both
the authorization and token requests), which defeats the token-ambiguity attack where a token minted
for a low-privilege server is replayed at a high-privilege one. The correct downstream pattern is
token exchange with a fresh, audience-scoped token, demonstrated in `oauth-confused-deputy/`.

**Sandboxing tool execution (NSA rec 5).** Tool logic touches shells, filesystems, and network
egress, so it runs under least privilege in an OS sandbox: seccomp to restrict syscalls, AppArmor or
SELinux to confine file and capability access, and cgroup resource limits to bound CPU, memory, and
process count. The sandbox holds no ambient credentials; downstream access is granted per action.

**Parameter validation against schemas (NSA rec 4).** Every tool input is validated against its
declared JSON Schema before execution, and ambiguous or user-sourced parameter forwarding is blocked.
The RC moves tool input/output schemas to full JSON Schema 2020-12 with `oneOf`/`anyOf`/`allOf`/`$ref`
(SEP-2106), which tightens what can be expressed and validated; the guardrails validator targets that
schema dialect.

**Supply chain and provenance.** Server container images are signed with cosign/sigstore (keyless
OIDC via Fulcio, recorded in the Rekor transparency log) and carry SBOM plus SLSA attestations.
Admission verification (sigstore policy-controller or Kyverno) admits only signed digests. MCP Server
Cards (`/.well-known/mcp/server-card.json`, SEP-1649 / SEP-2127, DRAFT) give clients a pre-connection
identity and capability record to validate against the `signed-registry/` before connecting.

**RC stateless-core impact on server design (preview).** The `2026-07-28` RC removes the
`initialize`/`initialized` handshake (SEP-2575) and the `Mcp-Session-Id` header / protocol-level
session (SEP-2567). Cross-call state no longer lives in a server-held session: it moves to explicit
server-minted handles (for example `basket_id`) passed back as ordinary tool arguments. For this
threat model that shifts surface area. Every handle now arrives as an untrusted tool parameter, so it
must be validated and authorized on each call exactly like any other argument (treating a handle as an
implicitly trusted session key would be the new privilege-escalation foot-gun). Protocol version,
client info, and capabilities travel in per-request `_meta`, and the required `Mcp-Method`/`Mcp-Name`
routing headers (SEP-2243) let the policy gateway authorize and rate-limit without parsing the body.
This is RC, not final; verify against the GA spec when it ships.

## Residual risk

After these controls, residual risk concentrates in indirect prompt injection arriving through
otherwise-valid tool results (the model is steered by data the server faithfully returned) and in
zero-day vulnerabilities in a signed, audited, sandboxed dependency; both are reduced by treating all
tool output as untrusted input to the next stage (NSA rec 7) and by CVE tracking and patching (NSA rec
9), but neither is eliminated.
