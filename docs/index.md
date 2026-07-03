<!-- ABOUTME: Landing page for the MkDocs site; orients a reader to the portfolio and its tracks.
ABOUTME: Mirrors the README banner; the build plan and spec-currency guide carry the detail. -->

# MCP Best Practices

A security-first portfolio demonstrating Model Context Protocol expertise through original working
code, threat models, and teaching material.

!!! info "Spec baseline"
    Built against MCP **`2025-11-25`** (latest stable). Forward-compatible notes for the
    **`2026-07-28`** Release Candidate; RC-only code is labeled preview. See
    [Spec Currency](spec-currency.md).

**Live demo:** the exam-prep quiz app runs at
[mcp-exam-quiz-production.up.railway.app](https://mcp-exam-quiz-production.up.railway.app).

## Tracks

The portfolio is built in this order, security first:

1. **Security (flagship)** : policy gateway (allowlist, consent, rules, rate limit, audit),
   guardrails, Ed25519-signed registry, threat models, OAuth demo, composed capstone.
2. **Fundamentals** : FastMCP and TypeScript servers, a minimal client, conformance-style tests.
3. **Tooling** : tool design, an eval harness, an elicitation human-in-the-loop confirmation demo,
   structured output.
4. **Architecture** : multi-server orchestration, stateless vs stateful, a self-hosted registry.
5. **Use cases and ecosystem** : a production-style server, an MCP plus A2A seam demo, an ecosystem map.
6. **Exam prep** : a researched curriculum and the live Railway quiz app.

## Start here

- [Build Plan](BUILD_PLAN.md) : the approved, sequenced plan and the locked stack.
- [Spec Currency](spec-currency.md) : the `2025-11-25` to `2026-07-28` RC migration guide.
- [Founding Report](research/mcp-sme-portfolio-research-2026-06.md) : the research this is built on.
- [Exam Curriculum](research/exam-curriculum-2026-06-23.md) : the ordered body of knowledge and blueprint.
