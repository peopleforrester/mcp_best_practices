<!-- ABOUTME: The policy-enforcing MCP gateway: a testable policy core plus a FastMCP transport adapter.
ABOUTME: This is the spine of the security track; guardrails and the signed registry plug into it. -->

# MCP Policy Gateway

A policy-enforcing gateway that sits between an MCP client and one or more upstream MCP servers. It
decides, per tool call, whether to allow or deny, and emits a SIEM-ready audit record for every
decision. It is the control point the threat models in `../threat-models/` call for.

## Design

The gateway separates the policy decision (original, framework-independent, fully unit-tested) from
the transport (a thin FastMCP adapter). This keeps the security logic provable and portable.

- **`policy.py` (the core).** `PolicyEngine.evaluate(request)` returns an allow/deny decision with a
  reason. Evaluation is secure default-deny, in order:
  1. **Rate limit** (`ratelimit.py`): deny a client over its per-client token-bucket budget, before
     any other work, so floods of any shape are throttled at the gateway (a DoS mitigation, MCP05).
  2. **Allowlist**: deny any tool not allowlisted for the `(client_id, server_id)` pair (mitigates
     shadow servers and tool-name shadowing, OWASP MCP09; with definition pinning, rug-pulls, MCP03).
  3. **Explicit deny rules** (OPA-style predicates): a deny wins over any later allow.
  4. **Explicit allow rules**: a matching allow rule grants the call and satisfies the consent gate
     (operator pre-authorization; scope allow predicates tightly).
  5. **Consent gate**: deny a non-read-only tool the client has not consented to (mitigates
     over-broad consent and scope creep, MCP02). Undeclared tools default to needing consent.
  6. Default allow only for an allowlisted, consented tool.
- **`audit.py`.** `audit_record(...)` builds a structured record (NSA CSI recommendation 8). Arguments
  are fingerprinted with sha256, never logged in plaintext, so secrets passed as arguments do not
  leak (OWASP MCP01). Rate-limited requests still produce one audit record each (log-every-invocation
  by design), so a flood is shifted from tool execution to the audit sink, not silenced.
- **Scope.** The middleware gates `tools/call` only. Resources and prompts registered on a gated
  server are not policy-checked or redacted by this control; a deployment exposing those primitives
  needs the corresponding hooks.
- **`adapter.py` (FastMCP middleware).** `PolicyMiddleware` subclasses `fastmcp.server.middleware.Middleware`
  and implements `on_call_tool`: it builds a `PolicyRequest` from the call, evaluates the engine,
  writes one audit record, and either denies with a `fastmcp.exceptions.ToolError` or forwards to the
  upstream via `call_next`. Verified end-to-end against FastMCP 3.x with the in-memory `Client`
  (async in-memory-client tests). The security logic stays in the framework-independent core; this class is only the
  transport seam. Register with `mcp.add_middleware(PolicyMiddleware(engine, ...))`.

### Verified FastMCP 3.x API (2026-06-24)

```python
from fastmcp import FastMCP, Client          # in-memory Client(mcp) for tests
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import ToolError      # raise to deny a tool call

class M(Middleware):
    async def on_call_tool(self, context: MiddlewareContext, call_next):
        name = context.message.name           # tool name
        args = context.message.arguments       # dict of arguments
        return await call_next(context)        # forward, or raise ToolError to deny

mcp.add_middleware(M())
# client: result = await client.call_tool("echo", {...}); result.data == ...
```

Deployment as a proxy in front of upstream servers (composing multiple upstreams, stdio vs Streamable
HTTP) uses FastMCP's proxy API and is documented as the next integration step; the security control
itself is the middleware above and is fully tested.

## Develop

```bash
cd 04-security/policy-gateway
uv run pytest -q     # run the test suite
uv run ruff check .  # lint
```

Built against the stable `2025-11-25` spec. The `2026-07-28` RC moves session state into explicit
tool-argument handles and adds `Mcp-Method`/`Mcp-Name` routing headers, both of which suit a gateway;
that path will be added as labeled preview.
