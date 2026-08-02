<!-- ABOUTME: PREVIEW package: a 2026-07-28 stateless-core MCP server on FastMCP 4.0 beta / mcp 2.0.
ABOUTME: Deliberately isolated so the repo's default examples never depend on a pre-release SDK. -->

# Fundamentals: stateless-core preview (2026-07-28)

> **Preview.** This package runs on the **FastMCP 4.0 beta** line (which pulls `mcp` 2.0, the
> `2026-07-28` SDK). It is not a default example. The repo's stable examples stay on FastMCP 3.4.x
> until FastMCP 4.0 ships stable. See [`docs/spec-currency.md`](../../docs/spec-currency.md).

The `2026-07-28` revision (final on 2026-07-28) makes the protocol core **stateless**. This package
demonstrates the headline change against the current SDK, next to the stable, session-based
`server-python/` server so the difference is concrete rather than described.

## What it shows

- **No session, state via a handle.** Under `2025-11-25` a client opens a session (`initialize`
  handshake + `Mcp-Session-Id`) and the server keeps per-connection state. `2026-07-28` removes that:
  every request is self-describing (protocol version and client identity travel in `_meta`), there is
  no session, and cross-call state is passed explicitly. Here `open_cart` mints a `cart_id`; `add_line`
  and `cart_total` take it back as an ordinary argument. Such a server sits behind a plain round-robin
  load balancer with no shared session store, which is the point of the change (SEP-2567 / SEP-2575).
- **Cache hints on a list result.** The server is built with `cache_ttl` + `cache_scope="public"`, so
  the static `list_catalog` result carries the `2026-07-28` cache hint (`ttlMs` / `cacheScope`, SEP-2549)
  and a gateway may cache it.

The same in-process handle-store caveat as the architecture track applies: it stands in for a shared
external store and is not one; the handle model is what makes swapping one in trivial.

## Run

```bash
uv run pytest -q
uv run ruff check .
```
