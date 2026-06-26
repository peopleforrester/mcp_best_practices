# ABOUTME: The MCP-to-agent boundary: an MCP tool delegates a question to a specialist agent.
# ABOUTME: The delegate is a Protocol; in production it is an A2A client to a remote agent.
from __future__ import annotations

from typing import Protocol

from fastmcp import FastMCP


class AgentDelegate(Protocol):
    """A specialist agent this server can hand work to.

    The seam between MCP (agent-to-tool) and A2A (agent-to-agent): an MCP tool consults another
    agent. In production the concrete delegate is an A2A client (resolve the agent card, send a
    message, read the task result via the a2a-sdk); here it is injected so the bridge tests offline.
    """

    def ask(self, question: str) -> str:
        """Send a question to the agent and return its answer."""
        ...


def build_delegating_server(delegate: AgentDelegate) -> FastMCP:
    """Build an MCP server whose tool delegates to a specialist agent over the AgentDelegate seam."""
    mcp = FastMCP("usecases-a2a-bridge")

    @mcp.tool
    def ask_specialist(question: str) -> str:
        """Ask a specialist agent a question and return its answer.

        This is the MCP plus A2A composition: an MCP tool that consults another agent. The real
        a2a-sdk wiring (AgentCard, ClientFactory, message send) is documented in the spike.
        """
        return delegate.ask(question)

    return mcp
