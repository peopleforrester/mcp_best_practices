# ABOUTME: Tests for secret/PII redaction over tool inputs and results (MCP01, MCP10 mitigation).
# ABOUTME: The raw secret must never survive in the redacted output.
from mcp_guardrails.redaction import redact


def test_redacts_email():
    result = redact("Contact me at jane.doe@example.com please.")
    assert "jane.doe@example.com" not in result.text
    assert any(r.kind == "email" for r in result.redactions)


def test_redacts_openai_style_api_key():
    secret = "sk-abcdef0123456789abcdef0123456789"
    result = redact(f"the key is {secret} keep it safe")
    assert secret not in result.text
    assert any(r.kind == "api_key" for r in result.redactions)


def test_redacts_github_and_aws_tokens():
    text = "ghp_0123456789abcdef0123456789abcdef0123 and AKIAIOSFODNN7EXAMPLE"
    result = redact(text)
    assert "ghp_0123456789abcdef0123456789abcdef0123" not in result.text
    assert "AKIAIOSFODNN7EXAMPLE" not in result.text
    kinds = {r.kind for r in result.redactions}
    assert "github_token" in kinds
    assert "aws_access_key" in kinds


def test_redacts_modern_openai_key_prefixes():
    # sk-proj-/sk-svcacct-/sk-admin- are today's dominant formats; the hyphen must not end the match.
    for secret in (
        "sk-proj-abcdef0123456789ABCDEF0123",
        "sk-svcacct-abcdef0123456789ABCD",
        "sk-admin-abcdef0123456789ABCDEF",
    ):
        result = redact(f"the key is {secret} keep it safe")
        assert secret not in result.text, secret
        assert any(r.kind == "api_key" for r in result.redactions)


def test_redacts_github_pat_jwt_and_pem():
    text = (
        "github_pat_" + "A" * 70 + " "
        "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.sig-part "
        "-----BEGIN RSA PRIVATE KEY-----"
    )
    result = redact(text)
    kinds = {r.kind for r in result.redactions}
    assert {"github_pat", "jwt", "pem_private_key"} <= kinds


def test_reports_one_redaction_per_occurrence():
    result = redact("mail a@x.com and b@y.com")
    email_hits = [r for r in result.redactions if r.kind == "email"]
    assert len(email_hits) == 2
    assert "a@x.com" not in result.text and "b@y.com" not in result.text


def test_clean_text_is_unchanged():
    text = "Paris is the capital of France."
    result = redact(text)
    assert result.text == text
    assert result.redactions == []
