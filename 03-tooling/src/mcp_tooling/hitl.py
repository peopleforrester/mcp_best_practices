# ABOUTME: Elicitation as a human-in-the-loop gate: a consequential tool asks the user before acting.
# ABOUTME: The server pauses mid-call via ctx.elicit; only an explicit accepted "yes" performs the action.
from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from fastmcp import Context, FastMCP
from fastmcp.server.elicitation import (
    AcceptedElicitation,
    CancelledElicitation,
    DeclinedElicitation,
)
from mcp.types import ToolAnnotations


@dataclass
class ConfirmArchive:
    """The elicited confirmation: an explicit boolean, named so the form field is self-describing."""

    confirm: bool


def build_hitl_server() -> FastMCP:
    """Build a server whose consequential tool requires elicited confirmation before acting.

    This is the elicitation pattern from the tooling track: the tool call pauses, the server sends an
    elicitation request through the client (a form asking for a boolean confirmation), and the action
    runs only on an explicit accepted True. A decline, a cancel, or an accepted False all leave state
    untouched and say so, because silence must never be consent for a destructive step. The client must
    advertise the elicitation capability (the in-memory test client does via its handler); production
    hosts render the request as a real user prompt.
    """
    mcp = FastMCP("tooling-hitl")

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    async def archive_report(report_id: str, ctx: Context) -> str:
        """Archive a report by id, after the user confirms via elicitation.

        Destructive-classed on purpose: archiving removes the report from the active list, so the
        tool asks the human first instead of trusting the model's intent.
        """
        # The type: ignore + cast work around an observed upstream typing defect: mypy 2.1.0 resolves
        # fastmcp 3.4.2's elicit() overloads to the response_type=None overload even for a dataclass
        # (verified by minimal reproduction). Runtime behavior is correct and covered by three tests.
        raw = await ctx.elicit(
            f"Archive report {report_id!r}? It will be removed from the active list.",
            response_type=ConfirmArchive,  # type: ignore[arg-type]
        )
        result = cast(
            "AcceptedElicitation[ConfirmArchive] | DeclinedElicitation | CancelledElicitation", raw
        )
        if isinstance(result, AcceptedElicitation) and result.data.confirm is True:
            return f"archived {report_id}"
        return f"archive of {report_id} not confirmed; no action taken"

    return mcp
