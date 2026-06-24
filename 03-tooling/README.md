<!-- ABOUTME: Tooling track: a good-vs-anti-pattern tool pair and a deterministic eval harness.
ABOUTME: See guidebook.md for the narrative; this is the package quick reference. -->

# Tooling

- `contacts.py` : `getData` (anti-pattern) vs `contacts_search` (well-designed) on one domain.
- `eval_harness.py` : `evaluate_server(client)` returns a `Scorecard` per tool across five measured
  qualities (namespacing, description, parameter clarity, pagination, response conciseness).
  Deterministic and offline; no LLM or network.
- `annotations.py` : all four tool annotation hints, surfaced via `list_tools`.

The tests prove the well-designed tool outscores the anti-pattern. See `guidebook.md` for the full
discussion, including the LLM-judged extension and the code-execution-with-MCP idea.

```bash
uv run pytest -q
uv run ruff check .
```
