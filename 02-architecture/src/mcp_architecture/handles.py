# ABOUTME: The stateless handle pattern: cross-call state via a server-minted handle as a tool arg.
# ABOUTME: Mirrors the 2026-07-28 RC direction (no protocol session); the basket_id is the handle.
from __future__ import annotations

from typing import TypedDict

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError


class BasketState(TypedDict):
    """The structured state of a basket, returned by add_item and get_basket."""

    basket_id: str
    items: list[str]
    count: int


def build_basket_server() -> FastMCP:
    """Build a basket server where state is keyed by a handle passed as an ordinary tool argument.

    There is no protocol session: create_basket mints a handle, and later calls pass it back as a
    normal argument. Any server instance with access to the same store could serve any call, which is
    what makes the pattern horizontally scalable. The in-process dict here stands in for that store.
    """
    mcp = FastMCP("architecture-basket")
    baskets: dict[str, list[str]] = {}
    counter = {"n": 0}

    def _state(basket_id: str) -> BasketState:
        items = baskets[basket_id]
        return {"basket_id": basket_id, "items": list(items), "count": len(items)}

    @mcp.tool
    def create_basket() -> str:
        """Create a basket and return its handle (basket_id) for use in later calls."""
        counter["n"] += 1
        basket_id = f"basket-{counter['n']}"
        baskets[basket_id] = []
        return basket_id

    @mcp.tool
    def add_item(basket_id: str, item: str) -> BasketState:
        """Add an item to the basket named by the handle. Raises if the handle is unknown."""
        if basket_id not in baskets:
            raise ToolError(f"unknown basket_id {basket_id!r}")
        baskets[basket_id].append(item)
        return _state(basket_id)

    @mcp.tool
    def get_basket(basket_id: str) -> BasketState:
        """Read the basket named by the handle. Raises if the handle is unknown."""
        if basket_id not in baskets:
            raise ToolError(f"unknown basket_id {basket_id!r}")
        return _state(basket_id)

    return mcp
