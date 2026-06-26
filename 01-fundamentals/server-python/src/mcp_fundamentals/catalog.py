# ABOUTME: A non-trivial FastMCP server: a typed catalog with a paginated, search-focused tool.
# ABOUTME: Shows structured output (TypedDict), pagination via offset, and progress reporting.
from __future__ import annotations

from typing import Annotated, TypedDict

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

# Pagination bounds: limit must be at least 1 (limit 0 would advance the offset by 0 forever) and the
# offset must be non-negative. Declared on the parameters so the schema advertises them and invalid
# input is rejected rather than silently producing a broken or non-terminating page.
# This is a numeric offset, named honestly. MCP's wire pagination uses an opaque string cursor; a demo
# over an in-memory list uses a plain offset, so it is called "offset" rather than dressed up as one.
Limit = Annotated[int, Field(ge=1, le=100)]
Offset = Annotated[int, Field(ge=0)]


class ItemView(TypedDict):
    """The structured shape returned for a single catalog item."""

    id: str
    name: str
    category: str
    price_cents: int


class SearchPage(TypedDict):
    """A page of search results plus pagination metadata."""

    items: list[ItemView]
    total: int
    next_offset: int | None


_CATALOG: list[ItemView] = [
    {"id": "w1", "name": "Blue Widget", "category": "widgets", "price_cents": 1200},
    {"id": "w2", "name": "Red Widget", "category": "widgets", "price_cents": 1300},
    {"id": "w3", "name": "Green Widget", "category": "widgets", "price_cents": 1100},
    {"id": "g1", "name": "Small Gadget", "category": "gadgets", "price_cents": 4200},
    {"id": "g2", "name": "Large Gadget", "category": "gadgets", "price_cents": 6900},
    {"id": "g3", "name": "Travel Gadget", "category": "gadgets", "price_cents": 5400},
    {"id": "d1", "name": "USB Dongle", "category": "dongles", "price_cents": 900},
    {"id": "d2", "name": "HDMI Dongle", "category": "dongles", "price_cents": 1500},
]


def build_catalog_server() -> FastMCP:
    """Build the catalog server: a paginated search tool and a typed get-item tool."""
    mcp = FastMCP("fundamentals-catalog")

    @mcp.tool
    async def search_items(
        query: str = "",
        category: str | None = None,
        limit: Limit = 5,
        offset: Offset = 0,
        ctx: Context | None = None,
    ) -> SearchPage:
        """Search the catalog by name substring and optional category.

        Returns a page of matches with a next_offset for pagination (None on the last page).
        Search-focused rather than list-everything, per effective-tool design.
        """
        matches = [
            item
            for item in _CATALOG
            if query.lower() in item["name"].lower()
            and (category is None or item["category"] == category)
        ]
        if ctx is not None:
            await ctx.report_progress(progress=len(matches), total=len(_CATALOG))
        page = matches[offset : offset + limit]
        next_offset = offset + limit if offset + limit < len(matches) else None
        return {"items": page, "total": len(matches), "next_offset": next_offset}

    @mcp.tool
    def get_item(item_id: str) -> ItemView:
        """Get one catalog item by id. Raises a ToolError if the id is unknown."""
        for item in _CATALOG:
            if item["id"] == item_id:
                return item
        raise ToolError(f"no catalog item with id {item_id!r}")

    return mcp
