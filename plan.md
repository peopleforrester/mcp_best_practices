# Plan: September 2026 currency sweep (FastMCP 4.0 migration)

Triggered by a full-repo currency review on 2026-09-17 and by issue #50, which the repo's own
spec-currency reminder workflow filed on 2026-09-07 when its watched condition fired.

## Verified state (2026-09-17, primary sources)

- **MCP spec: `2026-07-28` is still current.** No newer revision published (blog.modelcontextprotocol.io).
  The repo's spec framing was already correct and did not need to change.
- **FastMCP 4.0.0 went stable on 2026-08-31**, now **4.0.4** (PyPI, 2026-09-16). `mcp` is **2.2.0**.
  This is the condition the repo documented as its trigger to migrate off 3.4.x.
- 5 open Dependabot alerts (2 high), all npm transitives in the TypeScript package.
- 4 open code-scanning alerts, all `note` severity.
- 5 open Dependabot version PRs targeting `main` directly.

## Decision: migrate, because the documented condition is met

The repo's standing rule is that a pre-release SDK is never the default path, which is why the code sat
on 3.4.x while the spec had moved. 4.0 is stable, so that reason is gone. Measured before committing to
it: six of seven packages pass their suites unchanged on 4.0.4, so the migration is a version bump plus
two real API changes, not a rewrite.

## Phases

1. **Migrate all packages to FastMCP 4.0 / mcp 2.x.** Re-pin, re-lock, verify.
2. **Rewrite the HITL gate for multi-round-trip requests.** `2026-07-28` removed server-initiated
   elicitation (SEP-2260); `ctx.elicit` now fails on a compliant connection. Replace with
   `InputRequiredResult` (SEP-2322). Keep the existing behaviour tests as the contract and add one
   that locks the new mechanism.
3. **Adapt to the `mcp` 2.x snake_case rename.** `ToolAnnotations(readOnlyHint=)` becomes
   `read_only_hint`, `Tool.inputSchema` becomes `input_schema`. Wire format unchanged.
4. **Retire the preview package's label.** It existed only because 4.0 was beta. Rename
   `server-python-preview` to `server-python-stateless` and drop the preview framing; the code is a
   good stateless-core example on its own merits. Remove the lockdrift exclusion it needed.
5. **Refresh the docs** that describe the old posture: spec-currency (rewritten), README, docs index,
   agent guidance, guidebooks, threat-model README, MEMORY, PROJECT_STATE.
6. **Repoint the reminder workflow.** Its trigger fired; point it at the next major line.
7. **Clear the security alerts and version drift**, then the code-scanning notes.
8. **Ship**: staging, CI green, promote, close #50 and the superseded Dependabot PRs.

## Guardrails

- No version claim without a live registry check, dated.
- The default path stays on stable. If a future spec outruns the framework again, label one package
  and say so in the docs rather than moving the default onto a pre-release.
