# ABOUTME: A read-only, production-style MCP server over the Kubernetes API (search + read pods).
# ABOUTME: The CoreV1Api is injected, so it tests offline; production loads least-privilege config.
from __future__ import annotations

from typing import Any, TypedDict

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from kubernetes.client.exceptions import ApiException
from mcp.types import ToolAnnotations


class PodView(TypedDict):
    """A trimmed, human-readable view of a pod (not the raw V1Pod dump)."""

    name: str
    namespace: str
    phase: str
    node: str


class PodPage(TypedDict):
    """A set of pod views plus a count."""

    pods: list[PodView]
    count: int


def _view(pod: Any) -> PodView:
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": (pod.status.phase if pod.status else "") or "Unknown",
        "node": (pod.spec.node_name if pod.spec else "") or "",
    }


def default_core_v1_api() -> Any:
    """Build a CoreV1Api from in-cluster or local kubeconfig (used in deployment, not in tests).

    Imported lazily so this module loads without a cluster present. Production should grant only a
    read-only Role (verbs get/list/watch); the server exposes no mutating tools.
    """
    from kubernetes import client, config

    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.CoreV1Api()


def build_k8s_server(api: Any) -> FastMCP:
    """Build a read-only Kubernetes MCP server over an injected CoreV1Api-like object."""
    mcp = FastMCP("usecases-kubernetes")

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
    def find_pods(namespace: str, label_selector: str = "") -> PodPage:
        """Search pods in a namespace, optionally filtered by a label selector (e.g. app=web).

        Returns trimmed pod views (name, namespace, phase, node), not raw API objects. Read-only.
        """
        result = api.list_namespaced_pod(namespace, label_selector=label_selector)
        views = [_view(pod) for pod in result.items]
        return {"pods": views, "count": len(views)}

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True))
    def get_pod_status(namespace: str, name: str) -> PodView:
        """Get the status of one pod by name. Raises a ToolError if no such pod exists. Read-only.

        Reads the single named pod (a GET on that resource) rather than listing the namespace, which
        is cheaper and keeps the least-privilege story tight (get on one pod, not list over the namespace).
        """
        try:
            pod = api.read_namespaced_pod(name=name, namespace=namespace)
        except ApiException as exc:
            if exc.status == 404:
                raise ToolError(f"no pod named {name!r} in namespace {namespace!r}") from exc
            raise
        return _view(pod)

    return mcp
