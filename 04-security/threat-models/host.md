<!-- ABOUTME: STRIDE threat model for the host application trust zone in an MCP deployment (June 2026).
ABOUTME: Maps each threat to an OWASP MCP Top 10 ID and an NSA CSI recommendation with a concrete mitigation. -->

# Threat Model: Host Application

The host is the application that runs the agent loop and embeds one MCP client per connected server: Claude Desktop, Claude Code, an IDE extension such as VS Code or Cursor, ChatGPT, or a custom agent runtime. It is the trust anchor for the deployment. The host holds the user's session and credentials, decides which servers to launch and which tools to expose to the model, mediates every consent prompt, and assembles the prompt context (system prompt, user input, tool definitions, tool results) that the LLM acts on. Its trust boundaries are three: with the human user (whose intent it must faithfully represent), with the LLM (whose output it treats as a request for action, not as ground truth), and with each embedded client and the server behind it (which it must treat as untrusted until verified, per NSA CSI rec 2). Tool results that cross the client boundary back into the prompt are the highest-risk inbound channel.

This model is written against the stable `2025-11-25` spec. Where the `2026-07-28` release candidate (RC, final July 28, 2026) shifts host responsibilities, that is flagged inline as preview.

## STRIDE

### Spoofing

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A malicious or shadow server is registered into the host (config edit, copied tutorial, typosquatted registry entry) and impersonates a trusted server. | MCP09 | 2, 10 | Admit servers only through the signed registry: verify a cosign/sigstore signature and pinned identity before the host launches a client. Scan the host environment for unauthorized servers (rec 10 tooling). |
| LLM output spoofs the user's intent, emitting a tool call the user never asked for. | MCP06 | 2, 7 | Treat model output as an action proposal, not authorization. Require explicit per-action user consent for non-read tools via host UI; log the proposing identity (policy gateway audit). |
| A server presents tool metadata claiming a trusted publisher it does not hold. | MCP03, MCP09 | 6, 2 | Bind tool provenance to verified signer identity in the signed registry; do not trust self-asserted publisher fields or `annotations` from an unverified server. |

### Tampering

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Tool-definition rug-pull: a server changes a tool's description or schema after the user approved it, so a previously benign tool now carries injected instructions or a wider parameter surface. | MCP03 | 6, 7 | Pin and hash approved tool definitions at consent time. Re-prompt the user when the hash changes; the policy gateway diffs `tools/list` against the approved snapshot and blocks drifted tools. |
| Tool results are tampered in transit or by the server to inject content into the next prompt stage. | MCP03, MCP10 | 6, 7 | Sign and verify MCP messages with expiration and replay protection (rec 6); treat every tool result as untrusted input to the next stage (rec 7) and pass it through output guardrails before it re-enters context. |
| The assembled prompt context (system prompt, tool catalog) is mutated by a compromised local component. | MCP06 | 5, 8 | Sandbox server processes under least privilege (seccomp/AppArmor) so a server cannot reach host config; log context-assembly inputs with result hashes to SIEM (rec 8). |

### Repudiation

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A destructive tool call runs but the host keeps no record of who proposed it, which user approved it, or what arguments were sent, so the action cannot be attributed after the fact. | MCP08 | 8 | Emit a structured, tamper-evident audit record per invocation (proposing model turn, user-consent decision, server identity, parameters, result hash) to SIEM via the policy gateway. |
| Consent decisions are not durably logged, so a disputed "the agent did X without asking" claim cannot be resolved. | MCP08 | 8 | Persist every consent grant and its scope with a timestamp and correlation id; W3C Trace Context in `_meta` (RC, SEP-414) lets the host correlate a UI consent to the downstream tool call. |

### Information disclosure

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Secrets in host configuration or logs: API keys, OAuth tokens, and server credentials stored in plaintext config files or written verbatim into debug logs and crash dumps. | MCP01 | 8 | Keep credentials out of host config files; reference a secrets store and inject at launch. Redact tokens and tool arguments matching credential patterns before logging (guardrails); never log full tokens. |
| Over-sharing: the host concatenates private data from one server into context that is then visible to a tool call on a different, less-trusted server. | MCP10 | 2, 3 | Enforce per-server data-flow boundaries in the policy gateway; route outbound calls through a filtering proxy / DLP with pinned resource URLs (rec 3) so private context cannot leave to an unapproved destination. |
| The host is tricked into exfiltration: injected content in a tool result instructs the agent to read sensitive data and send it through a write-capable or network tool (the lethal trifecta closing at the host). | MCP10, MCP06 | 3, 7 | Break the trifecta at the egress channel: outbound filtering proxy with allowlisted destinations (rec 3), output guardrails that strip injected exfiltration instructions, and human confirmation on any tool that can transmit externally. |

### Denial of service

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A server floods the host with oversized tool results, huge `tools/list` payloads, or rapid list-changed notifications, exhausting context window, memory, or the user's token budget. | MCP05 | 4, 5 | Cap result size and tool-catalog size at the client boundary; rate-limit notifications; sandbox and resource-bound server processes (rec 5). Validate payloads against schema before ingest (rec 4). |
| The agent loop is driven into a runaway tool-call cycle by injected content, consuming cost and blocking the user. | MCP06 | 4, 8 | Enforce per-session call budgets and loop-depth limits in the host; alert on anomalous call rates from audit telemetry (rec 8). |

### Elevation of privilege

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Over-broad consent granted once and reused: the user approves a tool or scope in one context and the host silently reuses that grant for later, unrelated calls. | MCP02 | 2, 4 | Scope consent to the action and context, not the session; expire grants and re-prompt on scope expansion. The policy gateway evaluates each call against the recorded grant rather than a blanket session approval. |
| Indirect prompt injection reaching the agent via tool results escalates the model's effective authority, making it invoke higher-privilege tools on the attacker's behalf. | MCP06, MCP03 | 7, 2 | Treat all tool/model output as untrusted input to the next stage (rec 7); run input guardrails for indirect-injection patterns before results re-enter context; keep destructive tools behind per-action consent so injection alone cannot trigger them. |
| Confused-deputy: the host (acting as a deputy with the user's authority) is induced to use its credentials on a resource the user did not intend, or to forward a token to the wrong audience. | MCP07, MCP01 | 2 | Audience-bind tokens with RFC 8707 Resource Indicators so a token for one server cannot be replayed at another; never pass tokens through (forbidden by spec). See the OAuth/confused-deputy demo for the anti-pattern and the correct flow. |

## Host-specific notes

**The lethal trifecta at the host.** The host is where the three ingredients converge: it holds private data (user files, session secrets, prior context), it ingests untrusted content (tool results, fetched pages, server-supplied resources), and it controls exfiltration channels (any network- or write-capable tool). All three are inside one process boundary, so the host cannot assume any single component is hostile and the others safe. The defensible move is to assume injected instructions will arrive in tool results and to gate the exfiltration channel: allowlisted egress proxy, output guardrails, and human confirmation on transmit-capable tools. Removing any one leg of the trifecta defeats the attack.

**Multi-server aggregation risk.** A host typically runs several clients at once and merges their tool catalogs into one namespace the model sees. This is where cross-server contamination lives: data read from a trusted server can be handed to a tool on a less-trusted server in the same turn, tool-name collisions can shadow a trusted tool, and one compromised server raises blast radius across the aggregate (Unit 42 reported a 78.3% attack success rate with five connected servers, a single compromise). Namespace tools per server, enforce per-server data-flow policy in the gateway, and keep one client and one consent scope per server.

**RC stateless core shift (label: preview).** The `2026-07-28` RC removes the `initialize`/`initialized` handshake (SEP-2575) and the `Mcp-Session-Id` / protocol-level session (SEP-2567); protocol version, client info, and capabilities now travel in `_meta` on each request, with `server/discover` for capability advertisement. For the host this moves identity and capability verification from a one-time handshake to a per-request concern: the host (or its gateway) must validate provenance and capability claims on every call rather than trusting a session established once. W3C Trace Context in `_meta` (SEP-414) helps the host correlate consent to invocation across stateless calls for audit. Re-verify these specifics at GA; the RC is not final.

## Residual risk

The host cannot, alone, guarantee that a verified server behaves correctly once admitted, prove a tool result is free of injected content, or enforce that a downstream resource API honors the least-privilege token it was given. Those controls must be pushed outward: message integrity, audience-bound tokens, and behavioral provenance to the auth server and the server; egress filtering, per-call policy evaluation, and tamper-evident audit to the policy gateway. The host's job is to refuse to act without those controls in place, not to substitute for them.
