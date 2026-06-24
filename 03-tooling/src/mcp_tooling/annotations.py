# ABOUTME: Demonstrates all four MCP tool annotation hints on representative tools.
# ABOUTME: Annotations are advisory and untrusted unless the server is trusted (per the spec).
from __future__ import annotations

from fastmcp import FastMCP
from mcp.types import ToolAnnotations


def build_annotations_server() -> FastMCP:
    """Build a server with one tool per annotation hint, for teaching and for the test suite."""
    mcp = FastMCP("tooling-annotations")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def read_status() -> str:
        """Read-only: returns a status string and changes nothing."""
        return "ok"

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    def delete_record(record_id: str) -> str:
        """Destructive: a client should require confirmation before calling this (demo only)."""
        return f"would delete {record_id}"

    @mcp.tool(annotations=ToolAnnotations(idempotentHint=True))
    def set_flag(name: str, value: bool) -> str:
        """Idempotent: calling with the same arguments twice has the same effect."""
        return f"{name}={value}"

    @mcp.tool(annotations=ToolAnnotations(openWorldHint=True))
    def web_search(query: str) -> str:
        """Open-world: interacts with external entities outside a closed dataset (demo only)."""
        return f"searching {query}"

    return mcp
