# ABOUTME: Framework-independent policy decision engine for an MCP gateway.
# ABOUTME: Evaluates allowlist, explicit deny rules, and a consent gate with a secure default-deny posture.
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum


class Decision(Enum):
    """Outcome of evaluating a request against policy."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class Effect(Enum):
    """Whether a rule, when matched, allows or denies the request."""

    ALLOW = "ALLOW"
    DENY = "DENY"


class ToolClass(Enum):
    """Safety classification that governs whether a tool needs prior consent.

    READ_ONLY tools may run without consent. MUTATING and DESTRUCTIVE tools require
    a recorded consent for the calling client. An undeclared tool defaults to MUTATING.
    """

    READ_ONLY = "read_only"
    MUTATING = "mutating"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class PolicyRequest:
    """A single tool invocation to be evaluated.

    Args:
        client_id: Identity of the calling MCP client.
        server_id: Identity of the upstream MCP server the tool belongs to.
        tool_name: Name of the tool being invoked.
        arguments: Tool arguments. Never logged in plaintext; see audit.arguments_fingerprint.
        consents: Tool names the client has an active consent grant for, in this context.
    """

    client_id: str
    server_id: str
    tool_name: str
    arguments: dict
    consents: frozenset[str] = frozenset()


@dataclass(frozen=True)
class PolicyResult:
    """The decision plus the reason and the rule that produced it (for audit attribution)."""

    decision: Decision
    reason: str
    matched_rule: str | None
    tool_class: ToolClass


@dataclass
class Rule:
    """An OPA-style rule: a named predicate with an allow or deny effect.

    The predicate is an ordinary Python callable so rules stay testable and explicit.
    Deny rules are evaluated before the consent gate and short-circuit on first match.
    """

    name: str
    effect: Effect
    match: Callable[[PolicyRequest], bool]


@dataclass
class PolicyEngine:
    """Evaluates tool invocations against allowlist, rules, and a consent gate.

    Evaluation order (secure default-deny):
        1. Allowlist: deny any tool not allowlisted for the (client, server) pair.
        2. Explicit deny rules: deny wins (evaluated before any allow).
        3. Explicit allow rules: a matching allow rule grants the call and satisfies the consent
           gate (an operator pre-authorizing a specific tool or argument pattern).
        4. Consent gate: deny a non-read-only tool the client has not consented to.
        5. Default allow for an allowlisted, read-only-or-consented tool.
    """

    allowlist: dict[tuple[str, str], set[str]]
    tool_classes: dict[str, ToolClass]
    rules: list[Rule] = field(default_factory=list)

    def evaluate(self, request: PolicyRequest) -> PolicyResult:
        """Return the policy decision for a single request."""
        tool_class = self.tool_classes.get(request.tool_name, ToolClass.MUTATING)

        allowed = self.allowlist.get((request.client_id, request.server_id), set())
        if request.tool_name not in allowed:
            return PolicyResult(
                Decision.DENY,
                "tool is not allowlisted for this client and server",
                "allowlist",
                tool_class,
            )

        for rule in self.rules:
            if rule.effect is Effect.DENY and rule.match(request):
                return PolicyResult(Decision.DENY, f"denied by rule {rule.name}", rule.name, tool_class)

        # A matching allow rule grants the call and satisfies the consent gate below.
        for rule in self.rules:
            if rule.effect is Effect.ALLOW and rule.match(request):
                return PolicyResult(Decision.ALLOW, f"allowed by rule {rule.name}", rule.name, tool_class)

        if tool_class is not ToolClass.READ_ONLY and request.tool_name not in request.consents:
            return PolicyResult(
                Decision.DENY,
                "consent required for a non-read-only tool",
                "consent",
                tool_class,
            )

        return PolicyResult(Decision.ALLOW, "allowlisted and consented", "allowlist", tool_class)
