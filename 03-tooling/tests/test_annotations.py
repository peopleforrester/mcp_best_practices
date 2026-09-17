# ABOUTME: Verifies all four tool annotation hints are declared and surfaced via list_tools.
# ABOUTME: A client reads these to decide consent prompts; they are advisory, not enforcement.
from fastmcp import Client

from mcp_tooling.annotations import build_annotations_server


async def test_all_four_annotation_hints_are_surfaced():
    async with Client(build_annotations_server()) as client:
        tools = {t.name: t for t in await client.list_tools()}
    assert tools["read_status"].annotations.read_only_hint is True
    assert tools["delete_record"].annotations.destructive_hint is True
    assert tools["set_flag"].annotations.idempotent_hint is True
    assert tools["web_search"].annotations.open_world_hint is True
