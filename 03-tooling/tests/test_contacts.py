# ABOUTME: Direct tests for the well-designed contacts_search tool (search, filter, pagination, bounds).
# ABOUTME: Previously only exercised indirectly via the eval harness; this asserts its actual behavior.
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from mcp_tooling.contacts import build_contacts_server


async def test_search_matches_by_name_substring():
    async with Client(build_contacts_server()) as client:
        page = (await client.call_tool("contacts_search", {"query": "ada"})).structured_content
    assert page["total"] >= 1
    assert all("ada" in c["name"].lower() for c in page["contacts"])


async def test_search_filters_by_team():
    async with Client(build_contacts_server()) as client:
        page = (await client.call_tool("contacts_search", {"team": "flight", "limit": 100})).structured_content
    assert page["total"] >= 1
    assert all(c["team"] == "flight" for c in page["contacts"])


async def test_search_paginates_with_offset():
    async with Client(build_contacts_server()) as client:
        first = (await client.call_tool("contacts_search", {"limit": 3, "offset": 0})).structured_content
    assert len(first["contacts"]) == 3
    assert first["next_offset"] == 3


async def test_last_page_has_no_next_offset():
    async with Client(build_contacts_server()) as client:
        page = (await client.call_tool("contacts_search", {"limit": 100, "offset": 0})).structured_content
    assert page["next_offset"] is None


async def test_results_omit_internal_ids():
    async with Client(build_contacts_server()) as client:
        page = (await client.call_tool("contacts_search", {"limit": 1})).structured_content
    assert set(page["contacts"][0]) == {"name", "email", "team"}


async def test_invalid_pagination_is_rejected():
    async with Client(build_contacts_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("contacts_search", {"limit": 0})
        with pytest.raises(ToolError):
            await client.call_tool("contacts_search", {"offset": -1})
