# ABOUTME: Tests for the policy decision engine (allowlist, consent gate, OPA-style rules, defaults).
# ABOUTME: These pin the engine's contract; the FastMCP adapter is tested separately.
from mcp_policy_gateway.policy import (
    Decision,
    Effect,
    PolicyEngine,
    PolicyRequest,
    Rule,
    ToolClass,
)


def make_engine(**kw):
    allowlist = kw.get("allowlist", {("client-a", "server-x"): {"search_docs", "delete_file"}})
    tool_classes = kw.get(
        "tool_classes",
        {"search_docs": ToolClass.READ_ONLY, "delete_file": ToolClass.DESTRUCTIVE},
    )
    rules = kw.get("rules", [])
    return PolicyEngine(allowlist=allowlist, tool_classes=tool_classes, rules=rules)


def req(tool, consents=frozenset(), args=None, client="client-a", server="server-x"):
    return PolicyRequest(
        client_id=client,
        server_id=server,
        tool_name=tool,
        arguments=args or {},
        consents=frozenset(consents),
    )


def test_deny_tool_not_in_allowlist():
    result = make_engine().evaluate(req("exfiltrate_secrets"))
    assert result.decision is Decision.DENY
    assert result.matched_rule == "allowlist"


def test_allow_readonly_tool_without_consent():
    result = make_engine().evaluate(req("search_docs"))
    assert result.decision is Decision.ALLOW


def test_deny_mutating_tool_without_consent():
    result = make_engine().evaluate(req("delete_file"))
    assert result.decision is Decision.DENY
    assert result.matched_rule == "consent"


def test_allow_mutating_tool_with_consent():
    result = make_engine().evaluate(req("delete_file", consents={"delete_file"}))
    assert result.decision is Decision.ALLOW


def test_explicit_deny_rule_overrides_allowlist_and_consent():
    block_prod = Rule(
        name="block-prod-delete",
        effect=Effect.DENY,
        match=lambda r: r.tool_name == "delete_file" and r.arguments.get("path", "").startswith("/prod"),
    )
    engine = make_engine(rules=[block_prod])
    result = engine.evaluate(req("delete_file", consents={"delete_file"}, args={"path": "/prod/db"}))
    assert result.decision is Decision.DENY
    assert result.matched_rule == "block-prod-delete"


def test_unknown_tool_class_requires_consent_secure_default():
    # delete_file is allowlisted but has no declared class -> treated as needing consent
    engine = make_engine(tool_classes={"search_docs": ToolClass.READ_ONLY})
    result = engine.evaluate(req("delete_file"))
    assert result.decision is Decision.DENY
    assert result.matched_rule == "consent"


def test_default_posture_is_deny_for_empty_allowlist():
    engine = PolicyEngine(allowlist={}, tool_classes={})
    result = engine.evaluate(req("anything"))
    assert result.decision is Decision.DENY


def test_allow_rule_satisfies_consent_gate():
    # An operator pre-authorizes a specific mutating tool without per-call consent.
    allow_rule = Rule(name="preauth-delete", effect=Effect.ALLOW, match=lambda r: r.tool_name == "delete_file")
    engine = make_engine(rules=[allow_rule])
    result = engine.evaluate(req("delete_file"))  # no consent supplied
    assert result.decision is Decision.ALLOW
    assert result.matched_rule == "preauth-delete"


def test_deny_rule_wins_over_allow_rule_for_same_request():
    allow_rule = Rule(name="preauth-delete", effect=Effect.ALLOW, match=lambda r: r.tool_name == "delete_file")
    deny_rule = Rule(name="block-prod", effect=Effect.DENY, match=lambda r: r.arguments.get("path") == "/prod")
    engine = make_engine(rules=[allow_rule, deny_rule])
    result = engine.evaluate(req("delete_file", args={"path": "/prod"}))
    assert result.decision is Decision.DENY
    assert result.matched_rule == "block-prod"
