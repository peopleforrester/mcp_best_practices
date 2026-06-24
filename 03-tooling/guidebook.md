<!-- ABOUTME: Guidebook for the Tooling track: effective tool design and a deterministic eval harness.
ABOUTME: The harness is the original artifact; it scores a good tool against an anti-pattern offline. -->

# Tooling Guidebook

How to design MCP tools that an agent uses well, and how to measure whether a tool is well-designed.
The measurement is the point: opinions about tool design are cheap, so this track ships a harness that
scores it.

## The matched pair (`contacts.py`)

One domain, two tools:

- `getData(x)` is the anti-pattern: a vague name, a meaningless parameter, a terse description, no
  pagination, and a single opaque text blob of the entire directory including internal ids.
- `contacts_search(query, team, limit, cursor)` is the well-designed tool: a namespaced
  `domain_action` name, a clear description, meaningful parameters, pagination with a `next_cursor`,
  structured human-readable output, and no leaked internal ids.

These embody the guidance from Anthropic's "Writing effective tools for AI agents": build for the
agent, prefer search over list-everything, return meaningful context not raw ids, and manage tokens
with pagination.

## The eval harness (`eval_harness.py`)

`evaluate_server(client)` connects over the in-memory transport, introspects every tool with
`list_tools`, invokes each once, and returns a `Scorecard` per tool across five measured qualities:

| Metric | What it checks |
|---|---|
| namespaced | name is `domain_action` (snake case with a separator) |
| described | description is present and substantive (>= 20 chars) |
| clear_params | no vague parameter names (`x`, `data`, `id`, `value`, ...) |
| paginated | input exposes `limit`/`cursor`/`page`/`offset` |
| concise_response | estimated response tokens fit a budget (a full dump blows it) |

The harness is **deterministic and offline**: no model, no network. That is what makes it CI-safe and
the tests reproducible. The tests assert that `contacts_search` outscores `getData`, that the good
tool passes every metric, and that the anti-pattern fails namespacing, pagination, and conciseness.
An LLM-judged tier (run an agent against each tool and compare task success) is the natural extension;
it is described here but kept out of CI because it needs API calls.

## Annotations (`annotations.py`)

All four tool annotation hints are demonstrated and tested: `readOnlyHint`, `destructiveHint`,
`idempotentHint`, `openWorldHint`, set via `@mcp.tool(annotations=ToolAnnotations(...))` and read back
through `list_tools`. The spec is explicit that annotations are advisory and must be treated as
untrusted unless the server is trusted, which is why the security track puts the real enforcement in
the gateway, not in annotations.

## Structured output, pagination, elicitation

- Structured output: `contacts_search` returns a `TypedDict`, so FastMCP generates an output schema
  and the client receives `structured_content`.
- Pagination: the `cursor` / `next_cursor` pattern in `contacts_search`.
- Elicitation (human-in-the-loop): a server requests structured input mid-call with
  `await ctx.elicit(message, response_type)`, which returns an action of accept, decline, or cancel
  plus the data. It is used in the security track's confirmation flows; the verified API shape is in
  `docs/research/spikes/fastmcp-advanced.md`.

## Code execution with MCP

For servers with very many tools, Anthropic's "Code execution with MCP" presents tools as code loaded
on demand rather than all definitions upfront, with a large reported token reduction (vendor-reported;
see the spike). The eval harness's conciseness metric is the small, local cousin of that idea: keep
each tool's surface and output lean.

## Run it

```bash
cd 03-tooling
uv run pytest -q
uv run ruff check .
```
