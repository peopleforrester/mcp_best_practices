<!-- ABOUTME: Demonstrates RFC 8707 audience binding defeating the confused-deputy attack in MCP auth.
ABOUTME: Shows why token passthrough is forbidden and token exchange is the correct downstream flow. -->

# OAuth Confused-Deputy Demo

A runnable, tested model of the MCP authorization rule that matters most for proxies and gateways:
access tokens are audience-bound (RFC 8707 Resource Indicators), and a server must never pass a
client's token through to a different downstream server. This is the confused-deputy defense the
auth-server threat model (`../threat-models/auth-server.md`) calls for.

## What it shows

- **`authz.py`** : an `AuthorizationServer` that issues Ed25519-signed access tokens carrying an
  `aud` (audience) claim bound to a single resource server.
- **`resource_server.py`** : a `ResourceServer` that accepts a token only if the signature verifies,
  the issuer matches, it is not expired, and its `aud` equals this server's canonical URI. The
  audience check is the line of defense: a token minted for server A is rejected at server B.
- **`flows.py`** :
  - `attempt_passthrough(...)` performs the forbidden anti-pattern (forward A's token to B) so a test
    can show B rejecting it on audience mismatch. A real gateway must never do this.
  - `exchange_token_for_audience(...)` is the correct flow: mint a fresh token whose audience is the
    downstream server, which the downstream then accepts.

## The tests are the lesson

`tests/test_confused_deputy.py` proves, with real Ed25519 signatures (no mocks):

1. A token validates at its own audience.
2. The same token is rejected at a different audience. **This is the confused-deputy defense.**
3. Expired and tampered tokens are rejected.
4. Passthrough to a downstream server fails (audience mismatch).
5. Token exchange (a new audience-bound token) is accepted downstream.

## Mapping

OWASP MCP02 (privilege escalation via scope creep) and MCP07 (insufficient authn/authz); the MCP
authorization spec's forbidden token passthrough; RFC 8707 audience binding. The `2026-07-28` RC adds
issuer-validation hardening (RFC 9207, SEP-2468); see `docs/spec-currency.md`.

## Develop

```bash
cd 04-security/oauth-confused-deputy
uv run pytest -q
uv run ruff check .
```
