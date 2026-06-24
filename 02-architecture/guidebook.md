<!-- ABOUTME: Guidebook for the Architecture track: handle pattern, composition, and the registry.
ABOUTME: Each section points at runnable, tested code; the registry server.json is CI-validated. -->

# Architecture Guidebook

How MCP servers are put together at the system level: where state lives, how servers compose, and how
a server is published for discovery. Built on the stable `2025-11-25` spec, with the `2026-07-28` RC
direction shown for state.

## Stateful session vs stateless handle (`handles.py`)

The central 2026 architecture question is where cross-call state lives.

- Under `2025-11-25`, a Streamable HTTP server can hold a session: it mints an `Mcp-Session-Id` on
  initialize, the client echoes it, and the server keeps per-session state. That requires sticky
  routing or a shared session store.
- The `2026-07-28` RC removes the protocol session. State moves into a server-minted handle passed as
  an ordinary tool argument. `create_basket` returns a `basket_id`; `add_item(basket_id, item)` and
  `get_basket(basket_id)` take it back. Any instance with access to the store can serve any call, so
  the server runs behind a plain round-robin load balancer.

`build_basket_server()` implements the handle form. The in-process dict stands in for the shared store;
the teaching point is the contract (handle-in-arguments), not the storage. The tests show two baskets
staying independent and an unknown handle raising.

## Server composition (`composition.py`)

`build_composite_server()` mounts two sub-servers under namespaces with `FastMCP.mount(server,
namespace=...)`. `mount` is a live link: a call to a namespaced tool is routed to the mounted server.
This is how one host aggregates several servers behind a single connection. `import_server(server,
prefix=...)` is the static alternative (a one-time copy). The test asserts the composite exposes tools
from both sub-servers and that a composed tool is callable.

## Registry and discovery (`registry-demo/`, `registry.py`)

The official MCP Registry is preview (API frozen at v0.1, service not yet GA). A server publishes a
`server.json`; `registry-demo/server.json` is an entry for the policy gateway. `validate_server_json`
checks the load-bearing fields offline (namespaced name, description, version, at least one install
target), so CI keeps the entry well-formed without contacting the live registry. The test validates
the shipped file and rejects entries missing a name or an install target.

`registry-demo/.well-known/mcp/server-card.json` is an illustrative pre-connection server card. The
server-card SEP (1649 / 2127) is still draft and the well-known path varies across sources, so treat
the card here as a shape to discuss, not a ratified contract. See
`docs/research/spikes/architecture-registry.md`.

## Run it

```bash
cd 02-architecture
uv run pytest -q
uv run ruff check .
```
