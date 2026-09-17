# ABOUTME: Tests the elicitation human-in-the-loop gate: a tool that asks before acting.
# ABOUTME: The in-memory client supplies the elicitation handler, so accept/decline both test offline.
from typing import Any

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

from mcp_tooling.hitl import build_hitl_server


def _accepting_handler(confirm: bool):
    async def handler(message: str, response_type: Any, params: Any, context: Any) -> Any:
        # The ConfirmArchive schema arrives as a generated object type with one boolean field.
        return {"confirm": confirm}

    return handler


async def _declining_handler(message: str, response_type: Any, params: Any, context: Any) -> Any:
    return ElicitResult(action="decline")


async def test_confirmed_elicitation_performs_the_action():
    server = build_hitl_server()
    async with Client(server, elicitation_handler=_accepting_handler(True)) as client:
        result = await client.call_tool("archive_report", {"report_id": "r-42"})
    assert "archived r-42" in result.data


async def test_explicit_no_does_not_perform_the_action():
    server = build_hitl_server()
    async with Client(server, elicitation_handler=_accepting_handler(False)) as client:
        result = await client.call_tool("archive_report", {"report_id": "r-42"})
    assert "archived r-42" not in result.data
    assert "not confirmed" in result.data


async def test_declined_elicitation_does_not_perform_the_action():
    server = build_hitl_server()
    async with Client(server, elicitation_handler=_declining_handler) as client:
        result = await client.call_tool("archive_report", {"report_id": "r-42"})
    assert "archived r-42" not in result.data
    assert "not confirmed" in result.data


async def test_first_leg_asks_instead_of_acting():
    # Locks the multi-round-trip mechanism itself (SEP-2322), not just the end-to-end behaviour the
    # auto-driving client produces. Driving the session directly with allow_input_required exposes the
    # raw first leg: it must come back as an ask naming the confirm request, having archived nothing.
    server = build_hitl_server()
    async with Client(server) as client:
        result = await client.session.call_tool(
            "archive_report", {"report_id": "r-42"}, allow_input_required=True
        )
    assert result.result_type == "input_required"
    assert "confirm" in (result.input_requests or {})
    # request_state is sealed on the wire and unsealed before the tool reads it, so what the client
    # sees here is an opaque token, never the plaintext the tool minted. That seal is what makes the
    # state tamper-evident across legs.
    assert result.request_state
    assert result.request_state != "r-42"
