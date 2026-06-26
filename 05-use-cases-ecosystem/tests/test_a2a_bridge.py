# ABOUTME: Tests the MCP-to-agent delegation bridge: an MCP tool delegates to a specialist agent.
# ABOUTME: The delegate is injected; in production it is an A2A client to a remote agent.
from fastmcp import Client

from mcp_usecases.a2a_bridge import build_delegating_server


class StubSpecialist:
    """An in-process delegate standing in for a remote A2A agent. Lives in the test tier only, so the
    shipped package exposes the AgentDelegate seam without a canned implementation (the real delegate
    is an a2a-sdk client, documented in the spike)."""

    def __init__(self, name: str):
        self.name = name

    def ask(self, question: str) -> str:
        return f"[{self.name}] answer to: {question}"


async def test_tool_delegates_to_the_agent():
    server = build_delegating_server(StubSpecialist("k8s-expert"))
    async with Client(server) as client:
        result = await client.call_tool("ask_specialist", {"question": "why is my pod pending?"})
    assert "k8s-expert" in result.data
    assert "pending" in result.data
