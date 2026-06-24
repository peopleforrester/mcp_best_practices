# ABOUTME: The simplest useful FastMCP server: one tool, one templated resource, one prompt.
# ABOUTME: Builder returns a FastMCP instance so tests can drive it with the in-memory client.
from __future__ import annotations

from fastmcp import FastMCP


def build_hello_server() -> FastMCP:
    """Build the hello server: an echo tool, a templated greeting resource, and a prompt."""
    mcp = FastMCP("fundamentals-hello")

    @mcp.tool
    def echo(text: str) -> str:
        """Return the given text unchanged. The smallest possible tool."""
        return text

    @mcp.resource("greeting://{name}")
    def greeting(name: str) -> str:
        """A templated resource: a greeting for the given name."""
        return f"Hello, {name}!"

    @mcp.prompt
    def summarize(topic: str) -> str:
        """A reusable prompt template asking for a short summary of a topic."""
        return f"Summarize the key points about {topic} in three bullets."

    return mcp
