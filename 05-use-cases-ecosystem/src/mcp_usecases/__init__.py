# ABOUTME: Public API for the use-cases track: a read-only k8s server and an MCP-to-agent bridge.
# ABOUTME: Both are dependency-injected so they test offline with no cluster and no network.
from mcp_usecases.a2a_bridge import AgentDelegate, LocalSpecialist, build_delegating_server
from mcp_usecases.k8s import PodView, build_k8s_server

__all__ = [
    "AgentDelegate",
    "LocalSpecialist",
    "PodView",
    "build_delegating_server",
    "build_k8s_server",
]
