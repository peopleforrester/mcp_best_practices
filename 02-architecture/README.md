<!-- ABOUTME: Architecture track: stateless handle pattern, server composition, registry/server-card.
ABOUTME: See guidebook.md for the narrative; this is the package quick reference. -->

# Architecture

- `handles.py` : the stateless handle pattern (`create_basket` mints a `basket_id`; `add_item` /
  `get_basket` take it as an argument). The RC direction: state via handles, not a protocol session.
- `composition.py` : `build_composite_server()` mounts the basket and math servers under namespaces
  via `FastMCP.mount(...)`; the composite exposes both toolsets.
- `registry.py` + `registry-demo/` : an offline validator for a registry `server.json`, plus a sample
  entry and an illustrative `.well-known/mcp/server-card.json` (the card SEP is draft).

8 tests, ruff clean. See `guidebook.md` for the stateful-vs-stateless discussion.

```bash
uv run pytest -q
uv run ruff check .
```
