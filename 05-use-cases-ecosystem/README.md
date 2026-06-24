<!-- ABOUTME: Use Cases & Ecosystem track: a read-only k8s MCP server, an MCP-to-agent bridge, a map.
ABOUTME: See guidebook.md for the narrative; this is the package quick reference. -->

# Use Cases & Ecosystem

- `k8s.py` : a read-only Kubernetes MCP server (`find_pods`, `get_pod_status`) over an injected
  `CoreV1Api`. Tested offline with real `V1Pod` models; production uses least-privilege RBAC.
- `a2a_bridge.py` : `ask_specialist`, an MCP tool that delegates to a specialist agent over an
  injected `AgentDelegate` seam (an A2A client in production).
- `ecosystem-map.md` : an MCP ecosystem snapshot labeling each claim verified vs self-reported.

5 tests, ruff clean. See `guidebook.md`.

```bash
uv run pytest -q
uv run ruff check .
```
