# ABOUTME: Conformance-style tests for the hello server over the FastMCP in-memory client.
# ABOUTME: Exercises capability negotiation, a tool, a templated resource, and a prompt.
from fastmcp import Client

from mcp_fundamentals.hello import build_hello_server


async def test_capability_negotiation_lists_the_tool():
    async with Client(build_hello_server()) as client:
        tools = await client.list_tools()
    assert any(t.name == "echo" for t in tools)


async def test_echo_tool_returns_input():
    async with Client(build_hello_server()) as client:
        result = await client.call_tool("echo", {"text": "hello mcp"})
    assert result.data == "hello mcp"


async def test_templated_resource_reads():
    async with Client(build_hello_server()) as client:
        contents = await client.read_resource("greeting://world")
    assert "world" in contents[0].text


async def test_prompt_is_available():
    async with Client(build_hello_server()) as client:
        prompts = await client.list_prompts()
    assert any(p.name == "summarize" for p in prompts)
