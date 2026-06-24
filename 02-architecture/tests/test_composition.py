# ABOUTME: Tests server composition: one host server mounts two sub-servers under namespaces.
# ABOUTME: The aggregated server exposes tools from both, callable through the composite.
from fastmcp import Client

from mcp_architecture.composition import build_composite_server


async def test_composite_aggregates_tools_from_both_servers():
    async with Client(build_composite_server()) as client:
        names = [tool.name for tool in await client.list_tools()]
    assert any(name.endswith("add") for name in names)
    assert any("create_basket" in name for name in names)


async def test_a_composed_tool_is_callable():
    async with Client(build_composite_server()) as client:
        names = [tool.name for tool in await client.list_tools()]
        add_name = next(name for name in names if name.endswith("add"))
        result = await client.call_tool(add_name, {"a": 2, "b": 3})
    assert result.data == 5
