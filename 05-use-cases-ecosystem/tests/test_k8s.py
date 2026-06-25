# ABOUTME: Tests the read-only Kubernetes MCP server with an injected fake CoreV1Api.
# ABOUTME: The fake returns real V1PodList/V1Pod models (recorded data), so no cluster is needed.
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError
from kubernetes.client import V1ObjectMeta, V1Pod, V1PodList, V1PodSpec, V1PodStatus

from mcp_usecases.k8s import build_k8s_server


def _pod(name: str, phase: str, node: str, labels: dict | None = None) -> V1Pod:
    return V1Pod(
        metadata=V1ObjectMeta(name=name, namespace="default", labels=labels or {}),
        spec=V1PodSpec(node_name=node, containers=[]),
        status=V1PodStatus(phase=phase),
    )


class FakeCoreV1Api:
    """A stand-in for kubernetes.client.CoreV1Api that returns recorded pod models."""

    def __init__(self, pods: list[V1Pod]):
        self._pods = pods

    def list_namespaced_pod(self, namespace: str, label_selector: str = "", **_kw) -> V1PodList:
        # Note: this fake parses only a single key=value selector; the real client handles the full
        # selector grammar (comma terms, !=, set-based). Sufficient for these read-only tests.
        pods = self._pods
        if label_selector:
            key, value = label_selector.split("=", 1)
            pods = [p for p in pods if (p.metadata.labels or {}).get(key) == value]
        return V1PodList(items=pods)

    def read_namespaced_pod(self, name: str, namespace: str, **_kw) -> V1Pod:
        for pod in self._pods:
            if pod.metadata.name == name:
                return pod
        from kubernetes.client.exceptions import ApiException

        raise ApiException(status=404, reason="Not Found")


def _server() -> object:
    api = FakeCoreV1Api(
        [
            _pod("web-1", "Running", "node-a", {"app": "web"}),
            _pod("web-2", "Running", "node-b", {"app": "web"}),
            _pod("db-1", "Pending", "node-a", {"app": "db"}),
        ]
    )
    return build_k8s_server(api)


async def test_find_pods_returns_trimmed_views():
    async with Client(_server()) as client:
        result = await client.call_tool("find_pods", {"namespace": "default"})
    page = result.structured_content
    assert page["count"] == 3
    assert {p["name"] for p in page["pods"]} == {"web-1", "web-2", "db-1"}
    assert all({"name", "namespace", "phase", "node"} == set(p) for p in page["pods"])


async def test_find_pods_filters_by_label_selector():
    async with Client(_server()) as client:
        result = await client.call_tool("find_pods", {"namespace": "default", "label_selector": "app=db"})
    page = result.structured_content
    assert page["count"] == 1
    assert page["pods"][0]["name"] == "db-1"


async def test_get_pod_status_returns_one_pod():
    async with Client(_server()) as client:
        result = await client.call_tool("get_pod_status", {"namespace": "default", "name": "db-1"})
    assert result.structured_content["phase"] == "Pending"


async def test_get_unknown_pod_raises():
    async with Client(_server()) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_pod_status", {"namespace": "default", "name": "ghost"})
