# ABOUTME: A per-principal token-bucket rate limiter for the policy gateway (DoS / flood control).
# ABOUTME: The clock is injected so refill is deterministic and the limiter is unit-testable offline.
from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    """A token bucket per principal: a burst of `capacity`, refilling at `refill_per_second`.

    Each `allow()` call spends one token if one is available and returns True; otherwise it returns
    False without spending. Tokens accrue continuously from the injected clock, so a client may burst up
    to `capacity` then is limited to the steady refill rate. State is in-memory per process, which is
    correct for a single-instance demo; a real multi-instance gateway would key a shared store.

    Memory is bounded: once the principal map grows past `max_principals`, buckets that have refilled
    to full are swept (a full bucket is indistinguishable from a fresh principal, so evicting it loses
    nothing). Without this, an attacker-controlled principal space would turn the DoS control into a
    memory-DoS vector. `allow()` contains no awaits, so it is atomic under a single asyncio event loop
    (FastMCP's execution model); it is not synchronized for multi-threaded callers.

    Args:
        capacity: Maximum tokens (the burst size). Also the initial balance for a new principal.
            Must be non-negative; 0 means always deny.
        refill_per_second: Tokens added per second, up to `capacity` (the sustained rate).
            Must be non-negative; 0 means no refill (a hard burst budget).
        now: Monotonic clock returning seconds; injected for deterministic tests.
        max_principals: Sweep threshold for the per-principal state map.
    """

    capacity: int
    refill_per_second: float
    now: Callable[[], float] = time.monotonic
    max_principals: int = 10_000
    _state: dict[str, tuple[float, float]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.capacity < 0:
            raise ValueError(f"capacity must be non-negative, got {self.capacity}")
        if self.refill_per_second < 0:
            raise ValueError(f"refill_per_second must be non-negative, got {self.refill_per_second}")
        if self.max_principals < 1:
            raise ValueError(f"max_principals must be at least 1, got {self.max_principals}")

    def _evict_stale(self, t: float) -> None:
        """Drop principals whose bucket has refilled to full; they are equivalent to fresh entries."""
        full = float(self.capacity)
        stale = [
            principal
            for principal, (tokens, last) in self._state.items()
            if tokens + (t - last) * self.refill_per_second >= full
        ]
        for principal in stale:
            del self._state[principal]

    def allow(self, principal: str) -> bool:
        """Spend one token for `principal`; return True if allowed, False if the bucket is empty."""
        t = self.now()
        if len(self._state) > self.max_principals:
            self._evict_stale(t)
        tokens, last = self._state.get(principal, (float(self.capacity), t))
        tokens = min(float(self.capacity), tokens + (t - last) * self.refill_per_second)
        if tokens < 1.0:
            self._state[principal] = (tokens, t)
            return False
        self._state[principal] = (tokens - 1.0, t)
        return True
