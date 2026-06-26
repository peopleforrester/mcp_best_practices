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


async def test_search_reports_incremental_progress():
    # report_progress must advance as the scan proceeds, not fire once with a single ratio. Collect the
    # notifications and assert there is more than one, they do not go backwards, and they end at total.
    seen: list[tuple[float, float | None]] = []

    async def on_progress(progress: float, total: float | None, message: str | None) -> None:
        seen.append((progress, total))

    async with Client(build_catalog_server(), progress_handler=on_progress) as client:
        await client.call_tool("search_items", {"query": ""})

    assert len(seen) > 1
    progresses = [p for p, _ in seen]
    assert progresses == sorted(progresses)
    assert seen[-1][0] == seen[-1][1]


async def test_search_paginates_with_offset():
    async with Client(build_catalog_server()) as client:
        first = (await client.call_tool("search_items", {"query": "", "limit": 3, "offset": 0})).structured_content
    assert len(first["items"]) == 3
    assert first["next_offset"] == 3


async def test_search_last_page_has_no_next_offset():
    async with Client(build_catalog_server()) as client:
        page = (await client.call_tool("search_items", {"query": "", "limit": 100, "offset": 0})).structured_content
    assert page["next_offset"] is None


async def test_get_item_returns_typed_view():
    async with Client(build_catalog_server()) as client:
        result = await client.call_tool("get_item", {"item_id": "w1"})
    assert result.structured_content["id"] == "w1"
    assert isinstance(result.structured_content["price_cents"], int)


async def test_get_unknown_item_raises_tool_error():
    async with Client(build_catalog_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_item", {"item_id": "does-not-exist"})


async def test_invalid_pagination_is_rejected():
    # limit=0 would advance the offset by 0 forever; offset<0 is nonsensical. Both must fail loudly.
    async with Client(build_catalog_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("search_items", {"limit": 0})
        with pytest.raises(ToolError):
            await client.call_tool("search_items", {"offset": -1})
