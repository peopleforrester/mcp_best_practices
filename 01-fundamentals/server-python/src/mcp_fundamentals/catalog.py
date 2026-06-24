# ABOUTME: A non-trivial FastMCP server: a typed catalog with a paginated, search-focused tool.
# ABOUTME: Shows structured output (TypedDict), pagination via cursor, and progress reporting.
from __future__ import annotations

from typing import TypedDict

from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError


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
    next_cursor: int | None


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
        limit: int = 5,
        cursor: int = 0,
        ctx: Context | None = None,
    ) -> SearchPage:
        """Search the catalog by name substring and optional category.

        Returns a page of matches with a next_cursor for pagination (None on the last page).
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
        page = matches[cursor : cursor + limit]
        next_cursor = cursor + limit if cursor + limit < len(matches) else None
        return {"items": page, "total": len(matches), "next_cursor": next_cursor}

    @mcp.tool
    def get_item(item_id: str) -> ItemView:
        """Get one catalog item by id. Raises a ToolError if the id is unknown."""
        for item in _CATALOG:
            if item["id"] == item_id:
                return item
        raise ToolError(f"no catalog item with id {item_id!r}")

    return mcp
