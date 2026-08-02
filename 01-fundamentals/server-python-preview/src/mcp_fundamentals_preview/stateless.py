# ABOUTME: A 2026-07-28 stateless-core MCP server on FastMCP 4.0 beta / mcp 2.0 (PREVIEW).
# ABOUTME: No initialize handshake and no session id: cross-call state rides a server-minted handle.
from __future__ import annotations

import uuid
from typing import TypedDict

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

# SEP-2549: the 2026-07-28 spec lets a server attach cache hints (ttlMs / cacheScope) to list/read
# results so a gateway can cache them. FastMCP 4.0 sets this at the server level; the catalog is static,
# so a public TTL is safe and lets a load balancer serve it without hitting the origin every time.
CATALOG_CACHE_TTL_SECONDS = 300

_CATALOG = [
    {"sku": "w1", "name": "Blue Widget"},
    {"sku": "w2", "name": "Red Widget"},
    {"sku": "g1", "name": "Small Gadget"},
]


class CartLine(TypedDict):
    """One line in a cart: a catalog sku and a quantity."""

    sku: str
    qty: int


class CartView(TypedDict):
    """The structured state of a cart, keyed by its handle (not by a protocol session)."""

    cart_id: str
    line_count: int
    total_qty: int


def build_stateless_cart_server() -> FastMCP:
    """Build a stateless-core cart server that demonstrates the 2026-07-28 headline change.

    Under the 2025-11-25 baseline a client opens a session (the `initialize` handshake plus an
    `Mcp-Session-Id`) and the server keeps per-session state for the connection's lifetime. The
    2026-07-28 revision removes that: every request is self-describing (protocol version and client
    identity travel in `_meta`), there is no session, and any state that must cross calls is passed
    explicitly as a server-minted handle. Here `open_cart` mints a `cart_id`; later calls pass it back
    as an ordinary argument. A stateless server like this can sit behind a plain round-robin load
    balancer with no shared session store, which is the point of the change.

    This is PREVIEW code: it runs on the FastMCP 4.0 beta line (which pulls `mcp` 2.0, the 2026-07-28
    SDK). The default examples in this repo stay on stable FastMCP 3.4.x until 4.0 ships stable.
    """
    mcp = FastMCP(
        "fundamentals-stateless-preview",
        cache_ttl=CATALOG_CACHE_TTL_SECONDS,
        cache_scope="public",
    )

    # In-process handle store. As in the architecture track, this stands in for what would be a shared
    # external store (Redis, a database); it is single-process and is not that store. The handle model
    # is what makes swapping in a shared store trivial: any instance can serve any handle.
    carts: dict[str, list[CartLine]] = {}

    def _view(cart_id: str) -> CartView:
        lines = carts[cart_id]
        return {
            "cart_id": cart_id,
            "line_count": len(lines),
            "total_qty": sum(line["qty"] for line in lines),
        }

    @mcp.tool
    def open_cart() -> str:
        """Open a cart and return its handle (cart_id) for later calls. No session is involved."""
        cart_id = uuid.uuid4().hex
        carts[cart_id] = []
        return cart_id

    @mcp.tool
    def add_line(cart_id: str, sku: str, qty: int) -> CartView:
        """Add a line to the cart named by the handle. Raises if the handle is unknown."""
        if cart_id not in carts:
            raise ToolError(f"unknown cart_id {cart_id!r}")
        carts[cart_id].append({"sku": sku, "qty": qty})
        return _view(cart_id)

    @mcp.tool
    def cart_total(cart_id: str) -> CartView:
        """Read the cart named by the handle. Raises if the handle is unknown."""
        if cart_id not in carts:
            raise ToolError(f"unknown cart_id {cart_id!r}")
        return _view(cart_id)

    @mcp.tool
    def list_catalog() -> list[dict[str, str]]:
        """List the static catalog. The server advertises a cache hint so a gateway may cache it."""
        return list(_CATALOG)

    return mcp
