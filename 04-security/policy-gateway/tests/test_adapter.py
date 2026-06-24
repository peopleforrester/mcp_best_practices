# ABOUTME: End-to-end tests for the FastMCP policy middleware using the in-memory client.
# ABOUTME: Verifies a denied tool is blocked with a clean error and an allowed tool passes through.
import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError

from mcp_policy_gateway.adapter import PolicyMiddleware
from mcp_policy_gateway.policy import PolicyEngine, ToolClass


def _engine():
    return PolicyEngine(
        allowlist={("client-a", "server-x"): {"echo", "delete_thing"}},
        tool_classes={"echo": ToolClass.READ_ONLY, "delete_thing": ToolClass.DESTRUCTIVE},
    )


def _server(consents=frozenset()):
    mcp = FastMCP("test-server")

    @mcp.tool
    def echo(text: str) -> str:
        return text

    @mcp.tool
    def delete_thing(path: str) -> str:
        return f"deleted {path}"

    audit: list[dict] = []
    mcp.add_middleware(
        PolicyMiddleware(
            _engine(),
            client_id="client-a",
            server_id="server-x",
            consents_for=lambda _client_id: frozenset(consents),
            audit_sink=audit.append,
        )
    )
    return mcp, audit


async def test_allows_readonly_tool_and_audits_allow():
    mcp, audit = _server()
    async with Client(mcp) as client:
        result = await client.call_tool("echo", {"text": "hello"})
    assert result.data == "hello"
    assert audit and audit[-1]["decision"] == "ALLOW"
    assert audit[-1]["tool"] == "echo"


async def test_denies_destructive_without_consent_and_audits_deny():
    mcp, audit = _server(consents=frozenset())
    async with Client(mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("delete_thing", {"path": "/data"})
    assert audit[-1]["decision"] == "DENY"
    assert audit[-1]["matched_rule"] == "consent"


async def test_allows_destructive_with_consent():
    mcp, audit = _server(consents=frozenset({"delete_thing"}))
    async with Client(mcp) as client:
        result = await client.call_tool("delete_thing", {"path": "/data"})
    assert result.data == "deleted /data"
    assert audit[-1]["decision"] == "ALLOW"


async def test_audit_never_contains_raw_arguments():
    mcp, audit = _server()
    secret = "tok-sk-do-not-log-7733"
    async with Client(mcp) as client:
        await client.call_tool("echo", {"text": secret})
    import json

    assert secret not in json.dumps(audit[-1])
