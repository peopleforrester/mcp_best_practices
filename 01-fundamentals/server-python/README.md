<!-- ABOUTME: Fundamentals Python package: a FastMCP hello server and a typed, paginated catalog server.
ABOUTME: Driven in tests by the FastMCP in-memory client; see the track guidebook for the narrative. -->

# Fundamentals (Python, FastMCP)

Two servers that teach the MCP primitives:

- `hello.py` : `build_hello_server()` with an `echo` tool, a templated `greeting://{name}` resource,
  and a `summarize` prompt.
- `catalog.py` : `build_catalog_server()` with a paginated, search-focused `search_items` tool
  (cursor + next_cursor, progress reporting, typed `SearchPage`) and a typed `get_item` tool that
  raises `ToolError` on an unknown id.

Tests use the in-memory `Client`, so they assert the protocol surface (capability negotiation, list,
call, read) end to end. Structured output is asserted via `result.structured_content` (the dict form);
`result.data` hydrates into a model object.

```bash
uv run pytest -q
uv run ruff check .
```
