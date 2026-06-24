# ABOUTME: Tests for the typed, paginated catalog server (search, pagination, typed get, errors).
# ABOUTME: Demonstrates search-focused tool design and structured output over the in-memory client.
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_fundamentals.catalog import build_catalog_server


async def test_search_returns_only_matches():
    async with Client(build_catalog_server()) as client:
        result = await client.call_tool("search_items", {"query": "widget"})
    assert result.structured_content["total"] >= 1
    assert all("widget" in item["name"].lower() for item in result.structured_content["items"])


async def test_search_paginates_with_cursor():
    async with Client(build_catalog_server()) as client:
        first = (await client.call_tool("search_items", {"query": "", "limit": 3, "cursor": 0})).structured_content
    assert len(first["items"]) == 3
    assert first["next_cursor"] == 3


async def test_search_last_page_has_no_next_cursor():
    async with Client(build_catalog_server()) as client:
        page = (await client.call_tool("search_items", {"query": "", "limit": 100, "cursor": 0})).structured_content
    assert page["next_cursor"] is None


async def test_get_item_returns_typed_view():
    async with Client(build_catalog_server()) as client:
        result = await client.call_tool("get_item", {"item_id": "w1"})
    assert result.structured_content["id"] == "w1"
    assert isinstance(result.structured_content["price_cents"], int)


async def test_get_unknown_item_raises_tool_error():
    async with Client(build_catalog_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_item", {"item_id": "does-not-exist"})
