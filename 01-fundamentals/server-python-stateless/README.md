<!-- ABOUTME: The 2026-07-28 stateless core as a worked example: handle pattern plus cache hints.
ABOUTME: Sits beside the session-shaped hello server so the two shapes read against each other. -->

# Fundamentals: the stateless core (2026-07-28)

The `2026-07-28` revision makes the protocol core **stateless**. This package shows what that means in
code, next to the session-shaped `server-python/` hello server, so the difference is concrete rather
than described. Both run on stable FastMCP 4.0 (`mcp` 2.x); see
[`docs/spec-currency.md`](../../docs/spec-currency.md).

## What it shows

- **No session, state via a handle.** Under `2025-11-25` a client opened a session (`initialize`
  handshake plus `Mcp-Session-Id`) and the server kept per-connection state. `2026-07-28` removes
  both: every request is self-describing (protocol version and client identity travel in `_meta`),
  and cross-call state is passed explicitly. Here `open_cart` mints a `cart_id`; `add_line` and
  `cart_total` take it back as an ordinary argument. Such a server sits behind a plain round-robin
  load balancer with no shared session store, which is the point of the change (SEP-2567 / SEP-2575).
- **Cache hints on a list result.** The server is built with `cache_ttl` + `cache_scope="public"`, so
  the static `list_catalog` result carries the `2026-07-28` cache hint (`ttlMs` / `cacheScope`,
  SEP-2549) and a gateway may cache it.

The same in-process handle-store caveat as the architecture track applies: it stands in for a shared
external store and is not one. The handle model is what makes swapping one in trivial.

## Run

```bash
uv run pytest -q
uv run ruff check .
```
