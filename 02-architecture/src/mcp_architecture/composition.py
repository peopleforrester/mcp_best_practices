# ABOUTME: Server composition: a host server mounts sub-servers under namespaces (FastMCP mount()).
# ABOUTME: The composite exposes the union of the sub-servers' tools, callable through one endpoint.
from __future__ import annotations

from fastmcp import FastMCP

from mcp_architecture.handles import build_basket_server


def build_math_server() -> FastMCP:
    """A tiny second server, used to show composition with the basket server."""
    mcp = FastMCP("math")

    @mcp.tool
    def add(a: int, b: int) -> int:
        """Add two integers."""
        return a + b

    return mcp


def build_composite_server() -> FastMCP:
    """Mount the basket and math servers under namespaces into one composite host server.

    mount() is a live link: calls to namespaced tools are routed to the mounted server. This is how a
    host aggregates multiple servers behind a single connection.
    """
    composite = FastMCP("architecture-composite")
    composite.mount(build_basket_server(), namespace="basket")
    composite.mount(build_math_server(), namespace="math")
    return composite
