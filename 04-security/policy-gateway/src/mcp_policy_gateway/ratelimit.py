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

    Args:
        capacity: Maximum tokens (the burst size). Also the initial balance for a new principal.
        refill_per_second: Tokens added per second, up to `capacity` (the sustained rate).
        now: Monotonic clock returning seconds; injected for deterministic tests.
    """

    capacity: int
    refill_per_second: float
    now: Callable[[], float] = time.monotonic
    _state: dict[str, tuple[float, float]] = field(default_factory=dict, init=False)

    def allow(self, principal: str) -> bool:
        """Spend one token for `principal`; return True if allowed, False if the bucket is empty."""
        t = self.now()
        tokens, last = self._state.get(principal, (float(self.capacity), t))
        tokens = min(float(self.capacity), tokens + (t - last) * self.refill_per_second)
        if tokens < 1.0:
            self._state[principal] = (tokens, t)
            return False
        self._state[principal] = (tokens - 1.0, t)
        return True
