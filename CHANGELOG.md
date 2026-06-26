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

- Quiz app rate limiter now keys on the forwarded client rather than the shared proxy address, so one
  visitor cannot consume another visitor's budget behind the platform edge.
- Quiz app request body cap is enforced on the request stream, so a chunked upload with no
  Content-Length can no longer bypass it; submission answer keys and values are length-bounded.
- Secret redaction covers the modern OpenAI key prefixes (`sk-proj-`, `sk-svcacct-`, `sk-admin-`) and
  bounds the email host pattern against pathological backtracking.

### Security

- Frontend builds the DOM with `createElement` and `textContent` only, never `innerHTML`, removing the
  reflected-content sink in the quiz UI.
- Quiz-app pagination bounds were corrected (the earlier off-by-one allowed an out-of-range page).
