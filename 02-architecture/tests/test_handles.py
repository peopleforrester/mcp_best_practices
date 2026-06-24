# ABOUTME: Tests the stateless handle pattern: state travels via a server-minted basket_id argument.
# ABOUTME: This is the 2026-07-28 RC direction (no protocol session); state keyed by the handle.
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_architecture.handles import build_basket_server


async def test_create_then_add_then_get_via_handle():
    async with Client(build_basket_server()) as client:
        basket_id = (await client.call_tool("create_basket", {})).data
        added = (await client.call_tool("add_item", {"basket_id": basket_id, "item": "apple"}))
        assert added.structured_content["count"] == 1
        got = (await client.call_tool("get_basket", {"basket_id": basket_id})).structured_content
    assert got["items"] == ["apple"]


async def test_two_baskets_are_independent():
    async with Client(build_basket_server()) as client:
        a = (await client.call_tool("create_basket", {})).data
        b = (await client.call_tool("create_basket", {})).data
        await client.call_tool("add_item", {"basket_id": a, "item": "x"})
        state_b = (await client.call_tool("get_basket", {"basket_id": b})).structured_content
    assert a != b
    assert state_b["count"] == 0


async def test_unknown_handle_raises():
    async with Client(build_basket_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_basket", {"basket_id": "nope"})
