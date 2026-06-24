# ABOUTME: Tests for the SIEM-ready audit record, including the no-raw-arguments guarantee.
# ABOUTME: Arguments are fingerprinted (sha256), never logged in plaintext (MCP01 mitigation).
import json

from mcp_policy_gateway.audit import audit_record
from mcp_policy_gateway.policy import PolicyEngine, PolicyRequest, ToolClass

REQUIRED_FIELDS = [
    "timestamp",
    "correlation_id",
    "client_id",
    "server_id",
    "tool",
    "tool_class",
    "decision",
    "reason",
    "matched_rule",
    "arguments_sha256",
]


def _engine():
    return PolicyEngine(allowlist={("c", "s"): {"t"}}, tool_classes={"t": ToolClass.READ_ONLY})


def test_audit_record_has_required_fields_and_is_json_serializable():
    request = PolicyRequest(
        client_id="c", server_id="s", tool_name="t", arguments={"q": "hello"}, consents=frozenset()
    )
    result = _engine().evaluate(request)
    record = audit_record(request, result, correlation_id="abc-123", timestamp="2026-06-24T00:00:00Z")
    json.dumps(record)  # raises if not serializable
    for field in REQUIRED_FIELDS:
        assert field in record, f"missing audit field: {field}"
    assert record["decision"] == "ALLOW"
    assert record["client_id"] == "c"


def test_audit_record_does_not_leak_raw_arguments():
    secret = "super-secret-token-value-9f2c"
    request = PolicyRequest(
        client_id="c", server_id="s", tool_name="t", arguments={"token": secret}, consents=frozenset()
    )
    result = _engine().evaluate(request)
    record = audit_record(request, result, correlation_id="x", timestamp="2026-06-24T00:00:00Z")
    blob = json.dumps(record)
    assert secret not in blob
    assert len(record["arguments_sha256"]) == 64
