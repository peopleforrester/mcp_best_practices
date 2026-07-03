# ABOUTME: Tests for the token-bucket rate limiter and its enforcement in the policy engine.
# ABOUTME: A clock is injected so refill behavior is deterministic without real time.
import pytest

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


def test_bucket_evicts_stale_principals_past_the_cap():
    # The limiter is the DoS control; it must not itself be a memory-DoS vector. A flood of one-shot
    # principal ids past max_principals triggers a sweep of buckets that have refilled to full (a full
    # bucket is indistinguishable from a fresh principal, so evicting it loses nothing).
    t, now = _clock()
    bucket = TokenBucket(capacity=1, refill_per_second=1.0, now=now, max_principals=2)
    for principal in ("a", "b", "c"):
        assert bucket.allow(principal) is True
    assert len(bucket._state) == 3  # over the cap, but none stale yet (no refill elapsed)

    t["now"] = 10.0  # every bucket refills to full -> all three are stale
    assert bucket.allow("d") is True  # trips the sweep
    assert len(bucket._state) == 1  # a, b, c evicted; only d remains


def test_bucket_rejects_nonsensical_parameters():
    _t, now = _clock()
    with pytest.raises(ValueError):
        TokenBucket(capacity=-1, refill_per_second=1.0, now=now)
    with pytest.raises(ValueError):
        TokenBucket(capacity=1, refill_per_second=-0.5, now=now)


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
