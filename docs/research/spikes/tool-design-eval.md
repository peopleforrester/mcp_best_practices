<!-- ABOUTME: Research spike on designing MCP tools for AI agents and building a tool eval harness.
ABOUTME: Sourced from Anthropic engineering posts and modelcontextprotocol.io; flags vendor-reported figures. -->

---
created: 2026-06-24
topic: mcp
status: fresh
---

# Tool Design and Eval Harnesses for MCP

Spike date: 2026-06-24. Verified against Anthropic's two engineering posts and
the MCP specification. Figures attributed to Anthropic and Cloudflare are
vendor-reported benchmarks on their own workloads, not independently
reproduced here. They are flagged inline.

## Primary sources

- Anthropic, "Writing effective tools for AI agents":
  https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic, "Code execution with MCP: building more efficient agents"
  (published 2025-11-04):
  https://www.anthropic.com/engineering/code-execution-with-mcp
- MCP specification, Tools (2025-06-18 revision):
  https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- Cloudflare, "Code Mode: give agents an entire API in 1,000 tokens":
  https://blog.cloudflare.com/code-mode-mcp/

---

## 1. Principles from "Writing effective tools for AI agents"

A tool is a contract between a deterministic system and a non-deterministic
agent. Anthropic frames the design goal as increasing the surface area over
which an agent can be effective, not mirroring a developer-facing API. The
agent may hallucinate, misread the spec, or take a path you did not plan for,
so the tool has to tolerate that.

### Build for agents, not developers

Do not reflexively wrap each existing API endpoint as one tool. A developer
SDK optimizes for completeness and composability; an agent optimizes for
getting to the answer inside a finite context window. Design the tool around
the workflow the agent is trying to complete.

### High-leverage tools over thin API wrappers

Consolidate the discrete calls a workflow needs into one tool that returns
what the agent actually wants. Anthropic's own examples:

| Thin wrappers (avoid) | Consolidated tool (prefer) |
|---|---|
| `list_users`, `list_events`, `create_event` | `schedule_event` (finds availability and books in one call) |
| `read_logs` | `search_logs` (returns only the relevant lines with context) |
| `get_customer_by_id`, `list_transactions`, `list_notes` | `get_customer_context` (compiles the relevant info at once) |

The reasoning: an agent with limited context cannot brute-force through full
result sets. It needs targeted retrieval, like skipping to the relevant page
rather than reading a book sequentially.

### Namespacing: domain_action prefixes

When an agent has dozens of servers and hundreds of tools, group related
tools under a consistent prefix so boundaries are obvious: `asana_search`,
`asana_projects_search`, `jira_search`. Anthropic notes the choice between
prefix- and suffix-based namespacing has non-trivial effects on eval
performance, so test both rather than assuming.

### Return human-readable context, not raw IDs

Prioritize contextual relevance over flexibility. Avoid low-level technical
identifiers in responses (`uuid`, `256px_image_url`, `mime_type`); expose
user-meaningful fields (`name`, `image_url`, `file_type`). Anthropic's claim:
"Resolving arbitrary alphanumeric UUIDs to more semantically meaningful and
interpretable language ... significantly improves Claude's precision in
retrieval tasks by reducing hallucinations."

When the agent genuinely needs raw IDs for a downstream call, expose a
`response_format` enum (e.g. `CONCISE` vs `DETAILED`) so it can opt in. In
Anthropic's Slack example the concise format consumed roughly one third of the
tokens of the detailed format (vendor-reported).

### Token management: pagination, truncation, filtering

Build in pagination, range selection, filtering, and truncation with sensible
defaults and limits. Claude Code caps tool responses at 25,000 tokens by
default. When you truncate, steer the agent with an instruction in the
response rather than silently cutting, for example: "You've reached the
response limit. Use filters to narrow results or paginate through results."
Error responses should be actionable input guidance, not opaque codes. Nudge
the agent toward many small targeted searches over one broad query.

### Unambiguous parameter names and descriptions

Write the tool description as you would brief a new hire: spell out
specialized query formats, terminology, and how resources relate. Name
parameters so intent is unmistakable; prefer `user_id` over `user`. Anthropic
reports that even small refinements to tool descriptions yield large
improvements, citing Claude Sonnet's SWE-bench gains after description edits.

### Search over list-everything

Replace broad-retrieval tools with targeted queries. A `list_contacts` tool
burns context returning every entry; `search_contacts` is both more
agent-ergonomic and more human-intuitive.

### Concrete good-vs-bad example pair

Bad (thin wrapper, raw IDs, list-everything):

```json
{
  "name": "list_contacts",
  "description": "Returns all contacts.",
  "input_schema": { "type": "object", "properties": {} }
}
```

Response: a full dump where each entry is `{"id":"u_8f3a...","u":"…"}`. The
agent must page through everything, then resolve opaque IDs on its own.

Good (consolidated, searchable, human-readable, paginated, self-describing
on truncation):

```json
{
  "name": "contacts_search",
  "description": "Search the address book by name, email, or company. Returns the best matches with display names and emails. Use the query to narrow results; this tool does not return the full directory.",
  "input_schema": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Name, email, or company substring to match." },
      "limit": { "type": "integer", "default": 10, "maximum": 50, "description": "Max results to return." },
      "response_format": { "type": "string", "enum": ["CONCISE", "DETAILED"], "default": "CONCISE", "description": "DETAILED adds raw contact_id for downstream calls." }
    },
    "required": ["query"]
  }
}
```

Response (CONCISE): `[{"name":"Sarah Chen","email":"sarah@acme.co","company":"Acme"}]`.
On overflow it appends: "Showing 10 of 240 matches. Narrow the query or raise
limit (max 50)."

---

## 2. "Code execution with MCP" (2025-11-04)

The problem: as connected tools grow, loading every tool definition upfront
and passing intermediate results back through the context window slows the
agent and inflates cost.

The pattern: present MCP servers as a filesystem of code the agent reads on
demand. The agent lists `./servers/` to find servers (such as `google-drive`
and `salesforce`), then reads only the specific tool files it needs (such as
`getDocument.ts`, `updateRecord.ts`) to learn the interface. It then writes a
small program that calls those tools, processes data in the execution
environment, and returns only the final concise result. This is progressive
disclosure: the model loads tool definitions when it needs them, via
filesystem navigation or a `search_tools` function, instead of all at once.

Two further benefits:

- Context-efficient results. Large datasets (a 10,000-row spreadsheet) are
  filtered inside the execution environment. Intermediate results stay there
  by default; the agent sees only what you explicitly log or return.
- Privacy. Sensitive fields can flow tool-to-tool (Sheets to Salesforce)
  without entering the model context; PII can be tokenized before exposure.

Reported figures (vendor-reported, Anthropic's own Google-Drive-to-Salesforce
workflow): "This reduces the token usage from 150,000 tokens to 2,000 tokens,
a time and cost saving of 98.7%."

Cloudflare's "Code Mode" is the same idea applied to a whole API. It exposes
just two tools, `search()` and `execute()`, backed by a type-aware SDK, and
the model writes TypeScript that runs in a V8 isolate. Cloudflare reports this
serves the entire Cloudflare API over MCP in roughly 1,000 tokens, versus an
estimated 1.17 million tokens for an equivalent definition-loading MCP server,
a 99.9% input-token reduction (vendor-reported). The footprint stays fixed
regardless of endpoint count.

Caveat on both numbers: they are best-case figures on workloads the vendors
chose, measuring tool-definition and intermediate-data tokens. They are
directionally credible and consistent with each other, but treat the exact
percentages as marketing-grade, not benchmark-grade. The mechanism (don't
serialize every schema and every intermediate row through the context) is the
durable takeaway.

---

## 3. Building a tool eval harness

Anthropic's guidance: build evaluations to measure tool performance, then use
the transcripts to refactor the tools. Concatenate eval transcripts and paste
them into Claude Code to spot where the agent got confused and propose tool
edits. Hold out a test set so you do not overfit the tools to the eval.

### Define tasks

- Ground tasks in real workflows, not toy sandboxes.
- Make tasks require several tool calls, sometimes dozens.
- Pair each prompt with a verifiable outcome (exact match, or a judged answer).
- Avoid verifiers so strict they reject correct alternative phrasings.

Strong task: "Customer ID 9182 was charged three times. Find the relevant log
entries and determine whether other customers were affected." Weak task:
"Search payment logs for `purchase_complete` and `customer_id=9182`" (it
pre-specifies the tool call and tests nothing about agent reasoning).

### Run the agent

Drive a simple agentic loop: alternate model API calls and tool calls in a
while-loop until the agent stops. Capture per-task metrics: success/accuracy,
wall-clock runtime, tool-call count, token consumption, and error rate.

### What an LLM-judge gets you vs a deterministic judge

An LLM judge scores open-ended answers ("did the retention offer cite the
right risk factors") that exact-match cannot. It costs API calls, adds
variance, and is itself a thing to validate. Use it for the final
answer-quality verdict only.

### What is measurable deterministically (no API calls, CI-safe)

Most of the harness can run in CI with zero model calls by asserting against
the tool layer directly. These are the testable invariants:

| Check | How to measure deterministically |
|---|---|
| Schema clarity | Parse `input_schema`. Assert every property has a `description`; assert `required` is set; assert no bare ambiguous names (`user`, `id`, `data`). Lint param names against a `*_id` convention. |
| Response token cost | Tokenize a recorded tool response (e.g. `tiktoken` or a fixed tokenizer). Assert it stays under a budget. Diff CONCISE vs DETAILED to confirm CONCISE is materially smaller. |
| Truncation behavior | Call the tool with input that overflows the limit. Assert the response is truncated AND carries a steering instruction string (regex for "narrow", "paginate", "limit"). |
| Error-message quality | Call with bad input. Assert the error names the offending field and states the expected format, not a bare code. Assert exit is non-zero / structured. |
| Namespacing consistency | Assert every tool name matches `^<domain>_<action>` and prefixes are consistent across the server. |
| Human-readable fields | Assert responses do not leak `uuid`/`mime_type`-style fields in CONCISE mode (allowlist the fields that may appear). |
| Pagination correctness | Assert page 2 differs from page 1 and that a cursor/offset round-trips. |

These deterministic checks are the half of the harness that belongs in CI and
guards against regressions on every commit. The LLM-judged success-rate run is
a separate, slower, networked tier you run deliberately, not on every push.

### Comparing a well-designed tool vs an anti-pattern tool

Wire both implementations behind the same task set. The deterministic tier
already shows the anti-pattern tool failing schema, token-budget, and
error-quality assertions. The networked tier then quantifies the gap: run the
same tasks against `contacts_search` (good) and `list_contacts` (bad) and
compare success rate and mean token cost per task. The expected and
demonstrable result is that the consolidated, searchable, human-readable tool
completes more tasks at lower token cost. That delta is the artifact worth
publishing.

---

## Open questions for a follow-up spike

- The code-execution pattern needs a sandbox (V8 isolate, container). What is
  the minimal safe local sandbox for a portfolio demo, and how do its security
  properties compare to Cloudflare's Worker Loader.
- Whether a deterministic harness can approximate "agent confusion" without an
  LLM, e.g. by counting redundant tool calls on a fixed scripted policy.
