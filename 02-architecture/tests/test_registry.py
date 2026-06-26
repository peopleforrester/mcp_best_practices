# ABOUTME: Tests the registry-entry validator against the shipped server.json and bad inputs.
# ABOUTME: Keeps the published server.json well-formed in CI without contacting the live registry.
import json
from pathlib import Path

from mcp_architecture.registry import validate_server_json

_SERVER_JSON = Path(__file__).resolve().parents[1] / "registry-demo" / "server.json"


# The current registry server.schema.json revision, verified live against the CDN on 2026-06-27 and
# documented in docs/research/spikes/architecture-registry.md. Locking it here so CI catches drift if
# the shipped artifact falls behind the published schema again.
_EXPECTED_SCHEMA = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"


def test_shipped_server_json_is_valid():
    data = json.loads(_SERVER_JSON.read_text())
    assert validate_server_json(data) == []


def test_shipped_server_json_pins_the_current_schema():
    data = json.loads(_SERVER_JSON.read_text())
    assert data["$schema"] == _EXPECTED_SCHEMA


def test_missing_name_is_reported():
    errors = validate_server_json({"description": "x", "version": "1.0.0", "packages": [{}]})
    assert any("name" in e for e in errors)


def test_missing_install_target_is_reported():
    errors = validate_server_json({"name": "io.example/x", "description": "x", "version": "1.0.0"})
    assert any("packages" in e or "remotes" in e for e in errors)
