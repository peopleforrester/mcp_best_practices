# Plan: adopt MCP 2026-07-28 (now final) as the current spec + a labeled stateless-core preview

The `2026-07-28` MCP revision went **final** on 2026-07-28 (verified live against blog.modelcontextprotocol.io
and the SEP set the repo already documented). It replaces `2025-11-25`. The repo currently calls it a
"Release Candidate" everywhere; that is now factually wrong.

## Verified SDK reality (2026-07-28 / PyPI + npm + uv resolution)
- Official Python `mcp` SDK: **2.0.0** final (a compat `1.29.0` shipped the same day).
- **FastMCP** (every Python server here uses it): stable **3.4.5 -> mcp 1.29** (2025-11-25 line);
  **4.0.0b1 -> mcp 2.0** is the 2026-07-28 line but is **beta**.
- TS `@modelcontextprotocol/sdk`: 1.30.0.

## Decision (Michael, framing flip + labeled preview)
The current spec is now 2026-07-28. The working code stays on **stable FastMCP 3.4.x** because the only
FastMCP that supports 2026-07-28 is 4.0-beta, and the repo's rule is "never ship preview as the default."
Add ONE clearly-labeled preview server on fastmcp 4.0-beta / mcp 2.0 to demonstrate the stateless core.
So the posture inverts: 2026-07-28 used to be the future preview; now it is the present, and the SDK
support (FastMCP 4.0 / mcp 2.0) is what is in preview.

## Phases
1. **P1 spec-currency.md** rewritten: 2026-07-28 = current final; 2025-11-25 = prior stable; the
   examples run on FastMCP 3.4.x (through 2025-11-25 semantics); FastMCP 4.0 / mcp 2.0 is the beta
   2026-07-28 line demonstrated in the preview; refresh trigger becomes "FastMCP 4.0 stable".
2. **P2 front door**: README, docs/index.md, CLAUDE.md, AGENTS.md, PROJECT_STATE.md, MEMORY.md,
   mkdocs description. Flip stable/RC wording; add the honest SDK-support note and the preview pointer.
3. **P3 threat models + guidebooks + decks**: the six threat models' inline "under the RC" / "the RC"
   notes become "2026-07-28 (final)"; guidebook and deck spec-boundary lines updated.
4. **P4 spikes + reminder cron**: supersede/reframe `mcp-rc-2026-07-28-readiness.md` (the RC is now
   final), note the currency in version-currency spike framing, and repoint the
   spec-currency-reminder workflow from "RC goes final" to "FastMCP 4.0 reaches stable".
5. **P5 preview server** (`01-fundamentals/server-python-preview/`, or `preview/stateless-core/`):
   fastmcp 4.0-beta / mcp 2.0, demonstrating the stateless request form + server/discover + a
   handle-based tool. VERIFY the fastmcp 4.0 API first (adopting-new-tech). Own pyproject allowing
   prereleases; README marks it PREVIEW. Tests. EXCLUDE from the lockdrift CI check (intentional SDK
   divergence) and confirm the CI python matrix still passes with a beta dep installed.
6. **P6 exam bank + curriculum**: questions flagged "RC, not final" are now wrong. Update the affected
   items, stems, and rationales to 2026-07-28-final facts; re-verify keys; curriculum README RC notes.
7. **P7 verify + wrap**: full gate, state/decisions/changelog, push staging, CI green (watch lockdrift
   and the new preview job), PR to main, verify deploys, journal.

## Guardrails
- No numerical regression and no fabricated support: the default code stays on the SDK line that
  actually implements what it claims; the preview is labeled and isolated.
- Recency: every version claim carries its 2026-07-28 verification and source.
