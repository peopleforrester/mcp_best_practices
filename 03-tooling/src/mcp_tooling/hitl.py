# ABOUTME: Human-in-the-loop gate built on multi-round-trip requests: a tool asks before it acts.
# ABOUTME: 2026-07-28 removed server-initiated elicitation, so the tool returns InputRequiredResult.
from __future__ import annotations

from fastmcp import Context, FastMCP
from fastmcp.tools import InputRequiredToolResult
from mcp.types import (
    ElicitRequest,
    ElicitRequestFormParams,
    InputRequiredResult,
    ToolAnnotations,
)

# The key naming this ask. It appears in the InputRequiredResult the tool mints and again in the
# client's responses, which is how a tool that asks several things at once tells the answers apart.
_CONFIRM = "confirm"

# MCP elicitation schemas are deliberately flat: an object of primitives, so any host can render a
# form for it without executing server-supplied layout.
_CONFIRM_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "confirm": {
            "type": "boolean",
            "description": "True to archive the report; false to leave it untouched.",
        }
    },
    "required": ["confirm"],
}


def build_hitl_server() -> FastMCP:
    """Build a server whose consequential tool requires human confirmation before acting.

    Under the `2025-11-25` baseline this was elicitation: the server paused mid-call and pushed a
    request down to the client. The `2026-07-28` stateless core removes that, because a stateless
    request cannot hold a connection open waiting for an answer (SEP-2260). The replacement is the
    multi-round-trip request (SEP-2322), and the control flow inverts:

    1. **Ask.** The first call arrives with no answers, so the tool returns an `InputRequiredResult`
       naming what it needs. That ask is the call's legitimate result, not a pause and not an error.
    2. **Answer.** The client renders the form, collects the human's decision, and retries the same
       call carrying `inputResponses` plus the opaque `requestState` the tool minted.
    3. **Act.** The retry arrives with answers present, so the tool reads them and proceeds.

    The safety property is unchanged and is the point of the pattern: only an explicit accepted
    `true` archives anything. A decline, a cancel, an accepted `false`, or a malformed answer all
    leave state untouched and say so, because silence must never be consent for a destructive step.
    """
    mcp = FastMCP("tooling-hitl")

    # The annotation is the *success* type. `InputRequiredToolResult` is a protocol-level control
    # result rather than part of this tool's output schema, and FastMCP passes it through untouched;
    # declaring a union here instead would suppress structured output on the answering leg.
    @mcp.tool(annotations=ToolAnnotations(destructive_hint=True, idempotent_hint=True))
    async def archive_report(report_id: str, ctx: Context) -> str:
        """Archive a report by id, after the human confirms.

        Destructive-classed on purpose: archiving removes the report from the active list, so the
        tool asks a person first rather than trusting the model's intent.
        """
        if ctx.input_responses is None:
            # First leg: nothing has been asked yet, so ask. `request_state` is sealed on the wire
            # and unsealed before the tool runs, so it is a tamper-evident way to carry what this
            # round decided into the next one.
            # mypy flags this against the `-> str` annotation. That annotation is deliberate (see
            # above): the ask is a protocol control result, not this tool's declared output type, and
            # FastMCP passes it through. Declaring a union instead would suppress structured output.
            return InputRequiredToolResult(  # type: ignore[return-value]
                InputRequiredResult(
                    input_requests={
                        _CONFIRM: ElicitRequest(
                            params=ElicitRequestFormParams(
                                mode="form",
                                message=(
                                    f"Archive report {report_id!r}? "
                                    "It will be removed from the active list."
                                ),
                                requested_schema=_CONFIRM_SCHEMA,
                            )
                        )
                    },
                    request_state=report_id,
                )
            )

        # Later leg: the client answered. Fail closed on anything that is not an explicit yes, and
        # on a state mismatch, which would mean this answer belongs to a different ask.
        answer = ctx.input_responses.get(_CONFIRM)
        confirmed = (
            answer is not None
            and getattr(answer, "action", None) == "accept"
            and (getattr(answer, "content", None) or {}).get("confirm") is True
            and ctx.request_state == report_id
        )
        if confirmed:
            return f"archived {report_id}"
        return f"archive of {report_id} not confirmed; no action taken"

    return mcp
