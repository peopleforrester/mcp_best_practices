# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) once a tagged release exists.

## [Unreleased]

### Added

- Security track (flagship): policy gateway, guardrails (injection scan and secret/PII redaction),
  Ed25519 signed registry, OAuth confused-deputy demo with RFC 8707 audience binding, original threat
  models, and a composed capstone server that gates a build on registry admission and wraps requests in
  policy and guardrails middleware.
- Fundamentals track: FastMCP (Python) and TypeScript hello-world plus non-trivial servers, a minimal
  client, and conformance tests against MCP `2025-11-25`.
- Tooling track: tool-design examples, an evaluation harness, elicitation and human-in-the-loop,
  structured output.
- Architecture track: multi-server orchestration, stateless vs stateful notes, a registry demo.
- Use-cases track: a production-style server, an MCP and A2A interop demo, an ecosystem map.
- Exam-prep track: a research-backed MCP curriculum and a Railway-deployable FastAPI quiz app with a
  browser frontend, strict CSP and security headers, a request body cap, a per-client rate limiter,
  structured request logging, and env-gated OpenTelemetry.
- Project license (Apache-2.0) and this changelog.

### Changed

- Quiz app rate limiter keys on the trusted right-most `X-Forwarded-For` hop rather than the spoofable
  left-most entry, so an attacker rotating the client-supplied value cannot mint a fresh bucket per
  request. The per-client bucket map is also evicted of stale entries past a size cap.
- Quiz app request body cap is enforced on the request stream, so a chunked upload with no
  Content-Length can no longer bypass it; submission answer keys and values are length-bounded.
- Secret redaction covers the modern OpenAI key prefixes (`sk-proj-`, `sk-svcacct-`, `sk-admin-`) and
  bounds the email host pattern against pathological backtracking.
- Registry demo `server.json` pins the current `2025-12-11` schema, and a test locks it so CI catches
  schema drift; the registry validator now checks that each package and remote has its installable
  fields rather than accepting an empty object.
- Pagination parameters renamed `cursor` to `offset` (a numeric offset, named honestly).
- TypeScript dependencies pinned to exact versions; `exactOptionalPropertyTypes` and
  `noUncheckedIndexedAccess` enabled. `ruff` and `fastapi` bumped to current patches.

### Security

- The composed capstone's injection scan defaults to a logging sink instead of discarding findings, so
  the detector is observable out of the box, not a silent no-op. Nested structured tool output is
  scanned and redacted recursively.
- The Ed25519 registry verifier fails closed on a wrong-type signer key, not just a wrong-length one.
- `get_pod_status` and `find_pods` both map Kubernetes API errors (404/403/other) to labeled tool
  errors instead of leaking a raw exception.
- Frontend builds the DOM with `createElement` and `textContent` only, never `innerHTML`, removing the
  reflected-content sink in the quiz UI.
- Quiz-app pagination bounds were corrected (the earlier off-by-one allowed an out-of-range page).

### Removed

- The canned in-process A2A delegate moved out of the shipped package into the test tier; the package
  exposes only the `AgentDelegate` Protocol seam.
