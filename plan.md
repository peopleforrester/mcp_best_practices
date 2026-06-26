# Remediation Plan (senior review 2026-06-26)

Phased TDD remediation of the `/review-senior` findings. Order by risk: High, then
teaching-fidelity Mediums, then contract-locking Lows. One concern per commit; full gate
(ruff + mypy + pytest) green before each commit. Push to staging per batch, PR to main at end.

## Phases

| # | Finding | Change | Test that catches it |
|---|---------|--------|----------------------|
| 1 | H3 | Redaction matches `sk-proj-`/`sk-svcacct-`/`sk-admin-` keys; bound the email host regex | `sk-proj-...` redacted |
| 2 | H1 | Rate-limit identity from left-most `X-Forwarded-For` (Railway edge), labeled demo-grade | distinct XFF clients get distinct buckets |
| 3 | H2 | Streaming body-size cap (not Content-Length only) + `Field(max_length)` on answer keys/values | chunked oversize rejected; long value 422 |
| 4 | H4 | Add `LICENSE` (Apache-2.0) and `CHANGELOG.md` | n/a (governance files) |
| 5 | M5 | Capstone guardrails recurse dicts/lists, redact + scan every reachable string | nested secret redacted |
| 6 | M6 | Honest pagination: `cursor`/`next_cursor` -> `offset`/`next_offset`; note MCP cursors are opaque | offset pagination tests |
| 7 | M8 | k8s `find_pods` maps `ApiException` to `ToolError` like its sibling | 403 from list -> ToolError |
| 8 | M10 | Enforce the type bar: mypy `disallow_untyped_defs`, `tsc --noEmit` in Taskfile check, tsconfig `noUncheckedIndexedAccess` | mypy/tsc gate |
| 9 | M11 | `report_progress` reports genuinely incremental progress (or is removed) | progress is incremental |
| 10 | M7 + low | Soften `arguments_fingerprint` docstring; fix `server.json` `$schema` to baseline | n/a (doc/data) |
| 11 | low | Lock contracts: OpenAPI hides answer/rationale; detector-bypass test; rate-limit `hits` eviction | new tests |

## Deferred (with reason)

- **M9 (eval namespacing metric):** `"_" in name` is a weak proxy for MCP namespacing, but the eval is
  only ever applied to the contacts demo pair, where the verdict is correct. Theoretical; not worth the churn.
- **Low A2A async:** making the delegate Protocol/tool `async` is a reasonable production note but churns
  the teaching seam; the synchronous demo is clearly labeled. Defer.
- **Low pagination DRY:** a shared `pagination.py` cannot be shared across the independent per-package
  projects without introducing a cross-package dependency, which the design deliberately avoids. Defer.
