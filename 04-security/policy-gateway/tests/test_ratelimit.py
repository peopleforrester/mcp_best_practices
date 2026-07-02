# ABOUTME: Tests for the token-bucket rate limiter and its enforcement in the policy engine.
# ABOUTME: A clock is injected so refill behavior is deterministic without real time.
from mcp_policy_gateway import Decision, PolicyEngine, PolicyRequest, ToolClass
from mcp_policy_gateway.ratelimit import TokenBucket


def _clock():
    t = {"now": 0.0}

    def now() -> float:
        return t["now"]

    return t, now


def test_bucket_allows_up_to_capacity_then_denies():
    _t, now = _clock()
    bucket = TokenBucket(capacity=2, refill_per_second=0.0, now=now)
    assert bucket.allow("client-a") is True
    assert bucket.allow("client-a") is True
    assert bucket.allow("client-a") is False  # burst of 2 exhausted, no refill


def test_bucket_is_per_principal():
    _t, now = _clock()
    bucket = TokenBucket(capacity=1, refill_per_second=0.0, now=now)
    assert bucket.allow("client-a") is True
    assert bucket.allow("client-a") is False
    assert bucket.allow("client-b") is True  # b has its own bucket


def test_bucket_refills_over_time():
    t, now = _clock()
    bucket = TokenBucket(capacity=1, refill_per_second=1.0, now=now)
    assert bucket.allow("client-a") is True
    assert bucket.allow("client-a") is False
    t["now"] = 1.0  # one second later, one token refilled
    assert bucket.allow("client-a") is True


def test_engine_denies_over_limit_with_a_rate_limit_reason():
    _t, now = _clock()
    engine = PolicyEngine(
        allowlist={("c", "s"): {"read_tool"}},
        tool_classes={"read_tool": ToolClass.READ_ONLY},
        rate_limiter=TokenBucket(capacity=1, refill_per_second=0.0, now=now),
    )
    req = PolicyRequest(client_id="c", server_id="s", tool_name="read_tool", arguments={})
    assert engine.evaluate(req).decision is Decision.ALLOW
    second = engine.evaluate(req)
    assert second.decision is Decision.DENY
    assert "rate limit" in second.reason.lower()
    assert second.matched_rule == "rate_limit"
