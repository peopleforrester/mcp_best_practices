<!-- ABOUTME: Guidebook for the Use Cases & Ecosystem track: a real k8s server, an A2A bridge, a map.
ABOUTME: Each code section is tested offline; the ecosystem map is labeled verified vs self-reported. -->

# Use Cases & Ecosystem Guidebook

Two buildable use cases and one honest map.

## A production-style server over Kubernetes (`k8s.py`)

The kind of MCP server an organization actually runs: read-only access to a real CNCF API. `find_pods`
is search-focused (namespace plus an optional label selector) and `get_pod_status` reads one pod. Both
return trimmed, human-readable views (name, namespace, phase, node), not raw `V1Pod` dumps, and both
carry `readOnlyHint`.

The design choice that makes it testable and safe: the `CoreV1Api` is injected. In deployment,
`default_core_v1_api()` loads in-cluster or kubeconfig credentials behind a least-privilege read-only
Role (verbs get/list/watch). In tests, a `FakeCoreV1Api` returns real `V1PodList`/`V1Pod` model objects
(recorded data, not a behavioral mock), so the suite runs with no cluster. RBAC is the real boundary;
a mutating tool would gate behind the security track's gateway and consent rather than ship here.

## MCP plus A2A (`a2a_bridge.py`)

The composition the ecosystem converged on: MCP connects an agent to tools, A2A connects agents to each
other. The bridge is the smallest honest version: `ask_specialist` is an MCP tool that delegates to an
`AgentDelegate`. The delegate is a Protocol; `LocalSpecialist` is the in-process stand-in used in tests.
In production the concrete delegate is an A2A client (resolve the agent card at
`/.well-known/agent-card.json`, send a message, read the task result via the `a2a-sdk`). The seam is the
point; the transport is documented in `docs/research/spikes/a2a-integration.md`.

## The ecosystem map (`ecosystem-map.md`)

A snapshot that labels every adoption claim as verified or self-reported, because the honest version is
more credible than the marketing one. The governance and protocol facts are durable; the download
counts are directional. The independent census (12.9% high-trust of 17,468 servers) is the useful
counterweight to the vendor numbers.

## Run it

```bash
cd 05-use-cases-ecosystem
uv run pytest -q
uv run ruff check .
```
