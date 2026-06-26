# ABOUTME: Tests for the deterministic tool-design eval harness over the good/anti-pattern pair.
# ABOUTME: The well-designed tool must outscore the anti-pattern tool on the measured metrics.
from fastmcp import Client, FastMCP

from mcp_tooling.contacts import build_contacts_server
from mcp_tooling.eval_harness import evaluate_server


async def test_good_tool_outscores_bad_tool():
    async with Client(build_contacts_server()) as client:
        scores = await evaluate_server(client)
    assert scores["contacts_search"].score > scores["getData"].score


async def test_good_tool_passes_the_key_metrics():
    async with Client(build_contacts_server()) as client:
        scores = await evaluate_server(client)
    good = scores["contacts_search"]
    assert good.namespaced
    assert good.described
    assert good.clear_params
    assert good.paginated
    assert good.concise_response


async def test_bad_tool_fails_design_metrics():
    async with Client(build_contacts_server()) as client:
        scores = await evaluate_server(client)
    bad = scores["getData"]
    assert not bad.namespaced
    assert not bad.paginated
    assert not bad.concise_response


async def test_evaluate_server_handles_a_required_param_tool_without_crashing():
    # A tool with a required parameter cannot be invoked with {}; the harness must still score it on the
    # static design metrics rather than crashing on the response-size probe.
    mcp = FastMCP("required-param-demo")

    @mcp.tool
    def widget_lookup(widget_id: str) -> str:
        """Return a widget by its required id; a well-designed tool that cannot be called with {}."""
        return f"widget {widget_id}"

    async with Client(mcp) as client:
        scores = await evaluate_server(client)
    assert "widget_lookup" in scores
    assert scores["widget_lookup"].namespaced
    assert scores["widget_lookup"].described


async def test_scorecard_is_deterministic():
    async with Client(build_contacts_server()) as client:
        first = await evaluate_server(client)
    async with Client(build_contacts_server()) as client:
        second = await evaluate_server(client)
    # Compare the whole frozen Scorecard, not just .score: two cards can share a total while
    # differing on which metrics passed, and that would still be non-determinism.
    assert first["contacts_search"] == second["contacts_search"]
    assert first["getData"] == second["getData"]
