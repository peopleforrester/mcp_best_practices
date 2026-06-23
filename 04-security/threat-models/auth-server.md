<!-- ABOUTME: STRIDE threat model for the OAuth 2.1 authorization server trust zone in an MCP deployment (June 2026).
ABOUTME: Maps each threat to an OWASP MCP Top 10 ID and an NSA CSI recommendation with a concrete mitigation. -->

# Threat Model: OAuth 2.1 Authorization Server

The authorization server (AS) is the trust zone that interacts with the resource owner and issues and validates the access tokens an MCP client presents to a remote MCP server. In this deployment the MCP server is an OAuth 2.1 resource server (since spec revision `2025-06-18`); RFC 8707 Resource Indicators bind every token to a single MCP server audience via the canonical-URI `resource` parameter; and token passthrough is forbidden, so a server accepts only tokens minted for itself and never transits a foreign token. The AS holds the consent state, the client registry, the signing keys, and the refresh-token store, which makes it the highest-value target for confused-deputy, audience-confusion, and consent-phishing attacks.

This model is written against the stable `2025-11-25` spec. Where the `2026-07-28` release candidate (RC, final July 28, 2026) changes the authorization attack surface, that is flagged inline as preview.

## STRIDE

### Spoofing

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Authorization-server mix-up: a client is induced to send an authorization code (and later a token request) to an attacker-controlled AS impersonating the legitimate one, so the code is redeemed by the attacker. | MCP07 | 2 | Validate the `iss` parameter on the authorization response against the issuer recorded from validated AS metadata, using exact string comparison with no normalization (RFC 9207). Reject when `iss` is absent and the AS advertised `authorization_response_iss_parameter_supported=true`. (RC preview, SEP-2468 hardens this.) |
| A consent-phishing client registers via Dynamic Client Registration with a name or logo cloned from a trusted client, so the user approves it believing it is the real one. | MCP07 | 2 | Prefer Client ID Metadata Documents (HTTPS-URL client IDs) over open Dynamic Client Registration; treat the DCR path as deprecated and rate-limit it. Bind the displayed client identity to verified metadata, not self-asserted registration fields. |
| A client presents a token at the AS introspection or token endpoint that was issued for a different MCP server audience. | MCP07, MCP01 | 2 | Issue audience-bound tokens (RFC 8707 `aud`/`resource`) and validate audience on introspection; the resource server independently rejects any token whose audience is not its own canonical URI. |

### Tampering

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| An attacker alters the `resource` parameter or scope set on an authorization or token request so the AS mints a token for a wider audience or with broader scope than the user intended. | MCP02, MCP07 | 4 | Validate `resource` against an allowlist of registered canonical MCP server URIs and reject unrecognized targets with `invalid_target`; bind the granted scope to the consent record, not to the raw request. Schema-validate every authorization and token request (rec 4). |
| Token-claim tampering: a forged or modified JWT (altered `aud`, `scope`, or `exp`) is presented as a valid access token. | MCP01, MCP07 | 6 | Sign tokens with a strong asymmetric key and rotate via JWKS; resource servers verify the signature and `aud` per OAuth 2.1 Section 5.2 before honoring any claim. Apply message integrity and expiration end to end (rec 6). |

### Repudiation

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| A token is issued but the AS keeps no durable record of which client, which user-consent decision, which scopes, and which `resource` audience it was bound to, so a disputed grant cannot be attributed later. | MCP08 | 8 | Emit a structured, tamper-evident audit record per issuance (client id, subject, granted scopes, audience, grant type, jti, timestamp) to SIEM. Correlate to the downstream tool call via W3C Trace Context in `_meta` (RC, SEP-414). |
| A refresh-token rotation or revocation event is not logged, so theft-and-replay of a refresh token cannot be reconstructed during incident response. | MCP08, MCP01 | 8 | Log every refresh rotation, reuse-detection trip, and revocation with the prior and new `jti`; feed reuse alerts to SIEM (rec 8) so a replayed rotated token is both rejected and recorded. |

### Information disclosure

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Token and secret exposure: access tokens, refresh tokens, client secrets, or signing keys are written to logs, error responses, query strings, or plaintext config. | MCP01 | 8 | Never place tokens in the URI query string (spec MUST NOT); reference signing keys and client secrets from a secrets store, never config files; redact token-shaped values before logging (guardrails). See the OAuth/confused-deputy demo for the correct secret-handling flow. |
| Refresh-token theft from client storage or transit grants long-lived offline access to the bound MCP server audience. | MCP01 | 8 | Require refresh tokens to be kept confidential in transit and storage (OAuth 2.1 Section 4.3); enforce sender-constrained or rotating refresh tokens with reuse detection so a stolen token is single-use and trips revocation on replay. (RC preview, SEP-2207 refresh-token guidance.) |
| AS or Protected Resource Metadata over-discloses internal scopes, endpoints, or client lists to an anonymous discovery request. | MCP07, MCP10 | 3 | Expose only the minimal `scopes_supported` needed for basic functionality (scope minimization); serve discovery documents through the filtering egress proxy with pinned resource URLs (rec 3) so metadata cannot leak to unapproved destinations. |

### Denial of service

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Open Dynamic Client Registration is flooded with bogus client registrations, exhausting the registry or seeding consent-phishing entries. | MCP07, MCP09 | 4, 10 | Rate-limit and authenticate the DCR endpoint; prefer Client ID Metadata Documents so no server-side registration record is created. Scan for and prune unauthorized client registrations (rec 10). |
| The token and introspection endpoints are flooded to deny token issuance and validation to legitimate clients. | MCP07 | 4 | Rate-limit per client and per source at the policy gateway in front of the AS; cache JWKS at resource servers so token validation does not depend on a live AS round trip per call. |

### Elevation of privilege

| Threat | OWASP MCP Top 10 | NSA CSI rec | Mitigation |
|---|---|---|---|
| Confused deputy via a proxy MCP server: the proxy holds a static, pre-registered client ID at a third-party AS; an attacker, exploiting the AS's consent cookie from a prior legitimate approval, sends the user a crafted authorization link with a malicious `redirect_uri`, and the AS skips the consent screen and redirects the code to the attacker. | MCP07, MCP02 | 2 | Do not let a proxy reuse one static client ID across users; the AS MUST obtain explicit user consent for each dynamically registered client before redirecting, even when a consent cookie exists for the static proxy client. Demonstrated in the OAuth/confused-deputy demo. |
| Token passthrough: a server forwards a client-supplied token to a downstream MCP server or API, letting the downstream act with privileges the upstream token was never audience-scoped for. | MCP02, MCP07 | 2 | Forbidden by spec: a server MUST only accept tokens issued for itself and MUST NOT accept or transit any other token; clients MUST NOT send a server any token not issued by that server's AS. Mint a fresh audience-bound token (token exchange), never pass through. |
| Audience confusion: a token issued for a low-privilege MCP server is replayed against a high-privilege server that fails to validate audience. | MCP07, MCP02 | 2, 4 | RFC 8707 audience binding plus mandatory resource-server validation: the AS audience-restricts the token to the `resource` URI, and the server MUST validate the token was issued specifically for it before honoring it; the policy gateway re-checks audience per call. |
| Scope creep through step-up: repeated `insufficient_scope` step-up authorizations accumulate broad scope on a single token beyond the user's per-operation intent. | MCP02 | 2 | Challenge with only the scopes the current operation needs (least privilege); keep scope accumulation a client-side union of prior and challenged scopes so the AS stays stateless and the user re-consents on expansion. (RC preview, SEP-2350 scope accumulation on step-up.) |

## Authz-specific notes

**The confused-deputy attack against MCP proxy servers.** The classic shape, called out on the official MCP authorization and security-best-practices pages, is an MCP proxy that fronts a third-party authorization server using a single static client ID for all of its users. Because that client is pre-registered (or registered once via Dynamic Client Registration), the third-party AS sets a consent cookie the first time any user approves the proxy. An attacker then sends a victim a malicious authorization link whose `redirect_uri` points at attacker-controlled infrastructure. The AS sees the consent cookie for the already-approved static client, skips the consent screen, and redirects the authorization code to the attacker, who exchanges it for a token bearing the user's authority. The fix is that the AS must require explicit, per-client user consent before redirecting, and the proxy must not collapse many users behind one static client identity. The OAuth/confused-deputy demo in this security track reproduces the anti-pattern and the corrected flow.

**Why token passthrough is forbidden.** The spec is normative: a client MUST NOT send a server any token other than one issued by that server's authorization server; a server MUST only accept tokens valid for its own resources; and a server MUST NOT accept or transit any other token. Passthrough breaks audience validation (the receiving service can no longer trust that a token was meant for it), erases least privilege (the token carries whatever scope the original holder had), and severs attribution (the downstream sees the original client, not the proxy). The correct pattern when a server needs to call a downstream is to mint a fresh, audience-bound token for that downstream (token exchange), never to relay the inbound one.

**RFC 8707 Resource Indicators make tokens audience-bound.** The client MUST include the `resource` parameter on both the authorization request and the token request, MUST set it to the canonical URI of the MCP server it intends to call (for example `https://mcp.example.com/mcp`, scheme present, no fragment), and MUST send it whether or not the AS advertises support. The AS audience-restricts the issued token to that resource (RFC 8707 Section 2), typically via the JWT `aud` claim, so a token legitimately presented to one server cannot be redirected to another. The resource server then MUST validate that the token was issued specifically for it as the intended audience before honoring it. This is the direct defeat for audience confusion: a token for a low-privilege server is rejected at a high-privilege one.

**PKCE.** OAuth 2.1 requires PKCE on the authorization-code flow for all clients, public and confidential. The client generates a `code_verifier` and sends its `code_challenge` on the authorization request, then the verifier on the token request. This binds the redeemed code to the client instance that started the flow, defeating authorization-code interception and injection even if the code leaks through a logged redirect or a malicious `redirect_uri`.

**RC authorization hardening SEPs (label: preview).** The `2026-07-28` RC tightens several of the controls above. Treat all of these as in-flight until GA:

- **`iss` validation per RFC 9207 (SEP-2468):** the client validates the authorization-response issuer against the recorded issuer, hardening the AS mix-up / spoofing defense above.
- **Credential-to-issuer binding (SEP-2352):** binds issued credentials to the issuer that minted them, narrowing cross-issuer replay.
- **`.well-known` discovery clarification (SEP-2351):** clarifies the protected-resource and AS metadata discovery suffix so clients resolve the correct AS deterministically.
- **Refresh-token guidance (SEP-2207):** codifies confidential handling, rotation, and reuse-detection expectations for refresh tokens.
- **Scope accumulation on step-up (SEP-2350):** defines scope accumulation as a client-side union across step-up challenges, keeping the AS stateless and bounding privilege growth.

## Residual risk

The AS cannot guarantee that a correctly issued, audience-bound token is used only as the user intended once it reaches a server: a server that skips audience validation, a client that mishandles a refresh token, or a proxy that reuses a static client ID can each defeat the binding the AS provides. Those failure points sit in the server and client zones, not the AS, so the controls must be enforced there too: mandatory resource-server audience validation, no token passthrough, per-client consent, and per-call audience re-checks at the policy gateway. The AS's job is to mint tokens that are tightly scoped and tightly bound, and to refuse to issue when consent, issuer, or resource identity cannot be verified, not to assume downstream zones will honor that binding on their own.
