<!-- ABOUTME: Capstone guidebook for the security track: how the threat models and four controls compose.
ABOUTME: Reads top to bottom as the teaching narrative; each section links to runnable, tested code. -->

# Security Track Guidebook

The flagship track. It starts from a threat model of an MCP deployment and builds the controls that
the model demands, as original, tested code. The order is deliberate: understand the attack surface
first, then build the control points that close it.

Built against the stable MCP `2025-11-25` spec; `2026-07-28` RC deltas are noted as preview. See
`docs/spec-currency.md`.

## 1. The trust-zone model

Following the NSA guidance to treat agents, plugins, models, and users as separate trust zones
(CSI recommendation 2), an MCP deployment decomposes into six zones, each with its own STRIDE model
in `threat-models/`:

| Zone | File | The core risk |
|---|---|---|
| Host application | `threat-models/host.md` | Lethal trifecta converges here; multi-server aggregation |
| MCP client | `threat-models/client.md` | Trusting untrusted annotations; transport rebinding |
| LLM / inference boundary | `threat-models/llm.md` | Indirect prompt injection; tool poisoning |
| MCP server | `threat-models/server.md` | Command injection; token passthrough |
| Data stores / downstream | `threat-models/data-stores.md` | Exfiltration sink; over-sharing |
| OAuth authorization server | `threat-models/auth-server.md` | Confused deputy; audience confusion |

Every threat in those files is mapped to an OWASP MCP Top 10 category and an NSA CSI recommendation.
The cross-component summary is at the bottom of `threat-models/README.md`.

## 2. The four controls and how they compose

The threat models point at four control points. Each is a separate, tested package.

1. **Policy gateway** (`policy-gateway/`). The structural control: a secure default-deny engine over
   an allowlist, OPA-style deny rules, and a consent gate, plus a SIEM-ready audit record per
   decision. Wired into FastMCP as `PolicyMiddleware.on_call_tool`, so it sits in the request path of
   every tool call. Closes shadow servers (MCP09), rug-pulls (MCP03), scope creep (MCP02), and the
   audit gap (MCP08).
2. **Guardrails** (`guardrails/`). The content control: detect indirect-prompt-injection patterns in
   untrusted text, and redact secrets and PII before anything is logged or re-shared. The gateway
   calls these on arguments and results. Closes injection paths (MCP03, MCP06, MCP10) and secret
   exposure (MCP01).
3. **Signed registry** (`signed-registry/`). The supply-chain control: admit a server only when a
   trusted signer produced a valid signature over its entry (real Ed25519; a cosign/sigstore backend
   is the container path). Closes supply-chain tampering (MCP04) and shadow servers (MCP09).
4. **OAuth confused-deputy demo** (`oauth-confused-deputy/`). The authorization control: RFC 8707
   audience-bound tokens, so a token minted for one server is rejected at another, and token exchange
   instead of the forbidden passthrough. Closes the confused deputy (MCP02, MCP07).

Composed, the picture is: the signed registry decides which servers may exist; the gateway decides
which tool calls may run and records them; guardrails sanitize the content crossing the boundary; and
audience-bound tokens keep credentials from being replayed across servers. No single control is
sufficient, which is why the model builds all four.

5. **Composed capstone** (`capstone/`). The four controls above are also wired into a single running
   server so the composition is tested code, not just this paragraph. `build_capstone_server` gates the
   build on registry admission, runs `PolicyMiddleware` outermost (deny and audit before the tool
   runs) and `GuardrailsMiddleware` innermost (redact the result on the way out). Its tests prove,
   end to end, that an unadmitted server refuses to start, a destructive call without consent is
   denied and audited, and a secret in a result is redacted before return.

## 3. What stays honest

- The injection detectors are heuristics, not a complete defense. The real control is least-privilege
  tool design plus the gateway, not pattern matching. The guardrails README says so.
- The signed registry's unit tests use real Ed25519, not mocks; the cosign backend is an integration
  concern, documented and not yet wired.
- The gateway adapter is verified end to end against real FastMCP via the in-memory client, not a
  stubbed protocol.

## 4. Run it

```bash
# from each package directory
cd 04-security/policy-gateway      && uv run pytest -q
cd 04-security/guardrails          && uv run pytest -q
cd 04-security/signed-registry     && uv run pytest -q
cd 04-security/oauth-confused-deputy && uv run pytest -q
```

Each package has its own README with the design detail and the OWASP/NSA mapping.

## 5. Where the RC changes the picture

The `2026-07-28` RC moves session state into explicit tool-argument handles and adds `Mcp-Method` /
`Mcp-Name` routing headers, both of which suit a gateway (it can route and apply policy without
inspecting the body). It also hardens authorization (issuer validation per RFC 9207). These are
preview; the controls here are built on the stable baseline and will gain RC paths as labeled preview.
