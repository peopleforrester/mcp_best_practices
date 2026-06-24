# ABOUTME: Tests the MCP-to-agent delegation bridge: an MCP tool delegates to a specialist agent.
# ABOUTME: The delegate is injected; in production it is an A2A client to a remote agent.
from fastmcp import Client

from mcp_usecases.a2a_bridge import LocalSpecialist, build_delegating_server


async def test_tool_delegates_to_the_agent():
    server = build_delegating_server(LocalSpecialist("k8s-expert"))
    async with Client(server) as client:
        result = await client.call_tool("ask_specialist", {"question": "why is my pod pending?"})
    assert "k8s-expert" in result.data
    assert "pending" in result.data
