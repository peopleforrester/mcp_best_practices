# ABOUTME: Tests proving RFC 8707 audience binding rejects a token replayed at the wrong server.
# ABOUTME: Also proves token passthrough fails downstream and token exchange is the correct flow.
import pytest

from mcp_oauth_demo.authz import AuthorizationServer
from mcp_oauth_demo.flows import (
    TokenPassthroughForbidden,
    attempt_passthrough,
    exchange_token_for_audience,
    gateway_forward,
)
from mcp_oauth_demo.resource_server import ResourceServer

SERVER_A = "https://mcp.example.com/server-a"
SERVER_B = "https://mcp.example.com/server-b"
NOW = 1_000


def _setup():
    auth = AuthorizationServer(issuer="https://auth.example.com")
    rs_a = ResourceServer(resource_uri=SERVER_A, issuer_public_key=auth.public_key, issuer=auth.issuer)
    rs_b = ResourceServer(resource_uri=SERVER_B, issuer_public_key=auth.public_key, issuer=auth.issuer)
    return auth, rs_a, rs_b


def test_token_validates_at_its_own_audience():
    auth, rs_a, _ = _setup()
    token = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW + 100)
    assert rs_a.validate(token, now=NOW).accepted is True


def test_token_rejected_at_a_different_audience_confused_deputy_defense():
    auth, _, rs_b = _setup()
    token = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW + 100)
    result = rs_b.validate(token, now=NOW)
    assert result.accepted is False
    assert "audience" in result.reason


def test_expired_token_rejected():
    auth, rs_a, _ = _setup()
    token = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW - 1)
    result = rs_a.validate(token, now=NOW)
    assert result.accepted is False
    assert "expired" in result.reason


def test_tampered_token_rejected():
    auth, rs_a, _ = _setup()
    token = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW + 100)
    forged = token.with_claim("scope", "admin")  # mutate a claim without re-signing
    result = rs_a.validate(forged, now=NOW)
    assert result.accepted is False
    assert "signature" in result.reason


def test_passthrough_to_downstream_fails():
    # The confused-deputy anti-pattern: server A forwards the client's A-audience token to server B.
    auth, rs_a, rs_b = _setup()
    token_for_a = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW + 100)
    result = attempt_passthrough(token_for_a, downstream=rs_b, now=NOW)
    assert result.accepted is False
    assert "audience" in result.reason


def test_token_exchange_is_the_correct_flow():
    # The correct flow: obtain a fresh token whose audience is the downstream server.
    auth, _, rs_b = _setup()
    token_for_b = exchange_token_for_audience(
        auth, subject="user-1", audience=SERVER_B, scope="read", expires_at=NOW + 100
    )
    assert rs_b.validate(token_for_b, now=NOW).accepted is True


def test_conforming_gateway_refuses_passthrough_structurally():
    # The prohibition is a rule, not a side effect: a conforming gateway never forwards the token.
    auth, _, _ = _setup()
    token_for_a = auth.issue(subject="user-1", audience=SERVER_A, scope="read", expires_at=NOW + 100)
    with pytest.raises(TokenPassthroughForbidden):
        gateway_forward(token_for_a, downstream_uri=SERVER_B)


def test_list_valued_audience_is_honored():
    # RFC 8707 permits an array audience; a server listed in it accepts the token.
    auth, rs_a, _ = _setup()
    token = auth.issue(
        subject="user-1", audience=[SERVER_A, "https://mcp.example.com/server-c"], scope="read",
        expires_at=NOW + 100,
    )
    assert rs_a.validate(token, now=NOW).accepted is True
