# ABOUTME: Tests the 2026-07-28 stateless-core preview server on FastMCP 4.0 beta / mcp 2.0.
# ABOUTME: State crosses calls via a server-minted handle, not a protocol session (the headline change).
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_fundamentals_preview import build_stateless_cart_server


async def test_handle_carries_state_across_stateless_calls():
    server = build_stateless_cart_server()
    async with Client(server) as client:
        cart_id = (await client.call_tool("open_cart", {})).data
        assert isinstance(cart_id, str) and cart_id
        await client.call_tool("add_line", {"cart_id": cart_id, "sku": "w1", "qty": 2})
        view = (await client.call_tool("cart_total", {"cart_id": cart_id})).structured_content
    assert view["cart_id"] == cart_id
    assert view["line_count"] == 1
    assert view["total_qty"] == 2


async def test_two_carts_are_isolated_by_handle():
    server = build_stateless_cart_server()
    async with Client(server) as client:
        a = (await client.call_tool("open_cart", {})).data
        b = (await client.call_tool("open_cart", {})).data
        await client.call_tool("add_line", {"cart_id": a, "sku": "w1", "qty": 5})
        view_b = (await client.call_tool("cart_total", {"cart_id": b})).structured_content
    assert a != b
    assert view_b["line_count"] == 0  # b was never touched


async def test_unknown_handle_is_a_tool_error():
    server = build_stateless_cart_server()
    async with Client(server) as client:
        with pytest.raises(ToolError):
            await client.call_tool("cart_total", {"cart_id": "does-not-exist"})


async def test_catalog_list_is_served():
    # SEP-2549: the server is constructed with a public cache TTL so a gateway may cache this static
    # list (visible in build_stateless_cart_server). Here we assert the list is served correctly.
    server = build_stateless_cart_server()
    async with Client(server) as client:
        catalog = (await client.call_tool("list_catalog", {})).data
    assert len(catalog) >= 1
    assert all({"sku", "name"} <= set(item) for item in catalog)
