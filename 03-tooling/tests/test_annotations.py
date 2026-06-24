# ABOUTME: Verifies all four tool annotation hints are declared and surfaced via list_tools.
# ABOUTME: A client reads these to decide consent prompts; they are advisory, not enforcement.
from fastmcp import Client

from mcp_tooling.annotations import build_annotations_server


async def test_all_four_annotation_hints_are_surfaced():
    async with Client(build_annotations_server()) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["read_status"].annotations.readOnlyHint is True
    assert tools["delete_record"].annotations.destructiveHint is True
    assert tools["set_flag"].annotations.idempotentHint is True
    assert tools["web_search"].annotations.openWorldHint is True
