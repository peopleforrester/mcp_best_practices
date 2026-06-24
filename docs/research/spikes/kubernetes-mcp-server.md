# ABOUTME: Research spike on building a production-style read-only MCP server over the
# ABOUTME: Kubernetes API, verified against the official k8s Python client, FastMCP, and kubernetes.io.

# Kubernetes MCP server spike (2026-06-24)

A use-cases-track build of an MCP server that wraps a CNCF API. The target API
is Kubernetes, exposed through the official `kubernetes` Python client and
served with FastMCP. The design is read-only by default; mutation is treated as
a separate, gated concern.

All version numbers, signatures, and YAML below were checked against official
sources on 2026-06-24. Sources are listed at the end.

---

## 1. The `kubernetes` Python client

### Version pin and Python compatibility

| Fact | Value (verified 2026-06-24) |
|---|---|
| Latest release | `kubernetes==36.0.2` (released 2026-06-01) |
| PyPI package name | `kubernetes` (NOT `kubernetes-client`, which is a stale unrelated 2023 project) |
| Python support | Python >= 3.10, tested on 3.10, 3.11, 3.12, 3.13, 3.14 |
| Cluster compatibility | Client `36.y.z` is a full match for Kubernetes 1.36; `+-` (partial) for 1.35 and below and 1.37 and above |
| Versioning scheme | `vY.Z.P` where `Y.Z` mirror the Kubernetes minor/patch and `P` is the client patch |
| Support window | Three GA major releases (three Kubernetes minors) at a time |

Pin for this spike: `kubernetes==36.0.2`, Python 3.12 (inside the 3.10 to 3.14
band, matches current toolchain). Re-pin to match the target cluster's minor
version. Running a client more than one minor off the cluster gives `+-`
partial compatibility, not a guarantee.

### Loading config: in-cluster vs kubeconfig

Two distinct entry points. The server picks one based on where it runs.

In-cluster (the server is itself a pod, using its mounted ServiceAccount token).
Verbatim from the official example:

```python
from kubernetes import client, config

def main():
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print(f"{i.status.pod_ip}\t{i.metadata.namespace}\t{i.metadata.name}")

if __name__ == '__main__':
    main()
```

`config.load_incluster_config()` authenticates with the pod's ServiceAccount
credentials, mounted automatically by Kubernetes. It does not work outside a
cluster.

Kubeconfig (the server runs on a laptop or CI box against `~/.kube/config`):

```python
from kubernetes import client, config

config.load_kube_config()        # reads ~/.kube/config (or $KUBECONFIG)
v1 = client.CoreV1Api()
ret = v1.list_namespaced_pod(namespace="default")
```

A practical pattern for a server that must run in both places: try in-cluster
first, fall back to kubeconfig. Note this is a fallback for *config discovery*
only, not a behavioral fallback, so it does not violate the no-silent-fallback
rule. It should still fail loudly if neither source is present.

### Read-only example (list pods in a namespace)

`list_namespaced_pod` returns a `V1PodList`; iterate `.items` (each a `V1Pod`):

```python
from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()
pod_list = v1.list_namespaced_pod(namespace="default")
for pod in pod_list.items:
    print(pod.metadata.name, pod.status.phase)
```

Deployments live on `AppsV1Api`, not `CoreV1Api`:

```python
apps = client.AppsV1Api()
deployments = apps.list_namespaced_deployment(namespace="default")
```

### Least privilege: read-only RBAC

The client only does what its credentials permit. Bind the server's
ServiceAccount to a Role (or ClusterRole for cross-namespace) whose verbs are
limited to `get`, `list`, `watch`. Verbatim read-only Role from kubernetes.io:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

Bind it to the server's ServiceAccount:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

To cover deployments too, add a rule with `apiGroups: ["apps"]`,
`resources: ["deployments"]`, same three verbs. RBAC is the *hard* boundary.
Even if a tool's code or annotation lied, the API server rejects any write the
ServiceAccount is not granted. This is the enforcement layer the MCP annotation
hints (section 4) deliberately are not.

---

## 2. Wrapping it as a FastMCP server

### Tool definition

FastMCP turns a decorated function into a tool, using the function name as the
tool id, the docstring as the description, and type annotations for the input
schema. Verbatim basic shape:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="CalculatorServer")

@mcp.tool
def add(a: int, b: int) -> int:
    """Adds two integer numbers together."""
    return a + b
```

### Marking tools read-only via annotations

FastMCP accepts annotations as a `ToolAnnotations` object (preferred for type
support) or a plain dict. Verbatim recommended syntax:

```python
from mcp.types import ToolAnnotations

@mcp.tool(
    annotations=ToolAnnotations(
        title="Calculate Sum",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=False,
    )
)
def calculate_sum(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b
```

For a Kubernetes read tool, `readOnlyHint=True`, `idempotentHint=True`
(re-listing pods returns the same shape), and `openWorldHint=True` (it talks to
an external cluster whose contents change outside our control).

### Applied: a search tool and a read tool

Good tool design here means: a clear namespace prefix, narrow typed inputs,
human-readable structured output (a `dict` or Pydantic model, not a raw
`V1Pod.to_dict()` dump), and read-only annotations.

```python
from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from kubernetes import client, config

mcp = FastMCP(name="k8s-readonly")

def _core_api() -> client.CoreV1Api:
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()
    return client.CoreV1Api()

@mcp.tool(
    name="k8s_find_pods",
    annotations=ToolAnnotations(
        title="Find pods by label",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def k8s_find_pods(namespace: str, label_selector: str) -> list[dict]:
    """Find pods in a namespace matching a label selector
    (e.g. 'app=nginx'). Returns a compact summary per pod."""
    api = _core_api()
    pods = api.list_namespaced_pod(
        namespace=namespace, label_selector=label_selector
    )
    return [
        {
            "name": p.metadata.name,
            "namespace": p.metadata.namespace,
            "phase": p.status.phase,
            "node": p.spec.node_name,
        }
        for p in pods.items
    ]

@mcp.tool(
    name="k8s_get_pod_status",
    annotations=ToolAnnotations(
        title="Get pod status",
        readOnlyHint=True,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
def k8s_get_pod_status(namespace: str, name: str) -> dict:
    """Get the human-readable status of a single pod:
    phase, ready containers, restart counts, and conditions."""
    api = _core_api()
    pod = api.read_namespaced_pod(name=name, namespace=namespace)
    statuses = pod.status.container_statuses or []
    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": pod.status.phase,
        "containers": [
            {
                "name": cs.name,
                "ready": cs.ready,
                "restart_count": cs.restart_count,
            }
            for cs in statuses
        ],
        "conditions": [
            {"type": c.type, "status": c.status}
            for c in (pod.status.conditions or [])
        ],
    }
```

When a tool returns a `dict`, dataclass, or Pydantic model, FastMCP
automatically produces structured content alongside the human-readable text, so
clients get deserializable JSON without an explicit output schema. The point of
hand-building the dict is to avoid dumping the full `V1Pod` (hundreds of fields,
managed-field noise, base64 blobs) into the model's context. Return what a human
operator would actually want to read.

Design notes that hold up under review:

- Namespace every tool name (`k8s_*`) so it never collides with another server.
- Take `namespace` as an explicit required argument. Do not silently default to
  `default` or to "all namespaces", which would broaden blast radius and read
  data the caller did not ask for.
- One tool, one job. `find_pods` (search by selector) and `get_pod_status`
  (fetch one) are separate, matching the MCP "search + fetch" pairing.

---

## 3. Unit testing without a real cluster

### The cleanest seam: inject the API object

The structural problem with the examples above is the module-level `_core_api()`
call. For testability, the API client should be a dependency the tool receives,
not something it constructs. Refactor the logic out of the decorated function
into a plain function that takes the API object:

```python
# logic.py  -- no decorator, no global, fully testable
from kubernetes import client

def find_pods(api: client.CoreV1Api, namespace: str, label_selector: str) -> list[dict]:
    pods = api.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
    return [
        {"name": p.metadata.name, "phase": p.status.phase}
        for p in pods.items
    ]
```

The MCP tool becomes a thin wrapper that wires in the real client; the logic is
tested directly. The injection seam is the `api` parameter.

### Use recorded real model objects, not behavioral mocks

The key discipline: the test should feed in a real `V1PodList` built from the
client's own model classes (`V1Pod`, `V1ObjectMeta`, `V1PodStatus`), so the test
exercises the same attribute structure the live API returns. This is a
recorded/constructed *response*, not a mock that fakes API *behavior*.

```python
# test_logic.py
from kubernetes import client
from logic import find_pods

class FakeCoreV1Api:
    """A fake that returns recorded real model objects.
    No behavior is invented: list_namespaced_pod returns a genuine
    V1PodList, exactly the type the real client returns."""
    def __init__(self, pod_list: client.V1PodList):
        self._pod_list = pod_list

    def list_namespaced_pod(self, namespace, label_selector=None):
        return self._pod_list

def test_find_pods_returns_name_and_phase():
    recorded = client.V1PodList(items=[
        client.V1Pod(
            metadata=client.V1ObjectMeta(name="nginx-abc", namespace="default"),
            status=client.V1PodStatus(phase="Running"),
        ),
    ])
    api = FakeCoreV1Api(recorded)

    result = find_pods(api, namespace="default", label_selector="app=nginx")

    assert result == [{"name": "nginx-abc", "phase": "Running"}]
```

Why this over `unittest.mock.Mock`: a bare `Mock` will answer to any attribute
access and any method, so a test passes even when the code reads a field the
real `V1Pod` does not have, or when the API method signature changes. Building
the response from `client.V1Pod` / `client.V1PodList` means a typo like
`p.status.phasee` or a renamed field fails the test, because the real model
class does not carry that attribute. The fake fakes *transport* (no HTTP, no
cluster); it does not fake the *data contract*.

`MagicMock` / `patch` are acceptable only to stand in for the transport-level
client when you also assert against real model objects as return values. Treat
a test that asserts on `Mock(...)` return values as a smell: it proves the test
double, not the code.

This needs no extra dependency. For integration tests against a live cluster,
`kubetest` (a pytest plugin) manages a real cluster, but that is a separate
tier, not a unit test.

---

## 4. Safety: read-only by default, and how a write would gate

### Why read-only by default

Two independent layers, and they are not the same thing:

1. **RBAC (the hard boundary, section 1).** The ServiceAccount is granted only
   `get/list/watch`. Any write the code attempts is rejected by the API server.
   This holds regardless of what the tool code or its annotations claim.
2. **MCP annotations (the soft signal).** `readOnlyHint=True` tells the client
   the tool does not modify state, so a trusted-server client may auto-approve
   it without a confirmation prompt.

The MCP spec is explicit that annotations are hints, not enforcement. Verbatim
from the MCP blog:

> "Every property is a **hint**. The spec is explicit about this: annotations
> are not guaranteed to faithfully describe tool behavior, and clients **must**
> treat them as untrusted unless they come from a trusted server."

> "An untrusted server can lie. A server can claim `readOnlyHint: true` and
> delete your files anyway."

> "They aren't enforcement. If you need a guarantee that a tool can't exfiltrate
> data, that's a job for network controls or sandboxing, not a boolean hint."

So the read-only guarantee comes from RBAC, not the annotation. The annotation
just smooths the UX for tools that are genuinely safe. Build the server so the
two agree: read-only tools, read-only ServiceAccount.

### How a mutating tool would gate behind consent

If a write tool (say `k8s_scale_deployment`) were ever added, three things move
together:

1. **Annotation.** Drop `readOnlyHint`, set `destructiveHint=True` (and
   `idempotentHint` honestly: scale-to-N is idempotent, delete is not). Per the
   spec the default for `destructiveHint` is already `true`, so an unannotated
   tool is assumed destructive.
2. **Client consent.** Clients use the hints to decide when to prompt. From the
   sources: a `readOnlyHint: true` tool from a trusted server may be
   auto-approved, while `destructiveHint: true` "gets a confirmation step" and
   the client "shows a dialog listing what's about to be deleted before anything
   happens." ChatGPT requires all three of `readOnlyHint`, `destructiveHint`,
   `openWorldHint` and uses them to trigger confirmation; Claude requires at
   least `readOnlyHint` or `destructiveHint` and uses them to decide auto-call
   vs ask.
3. **RBAC + gateway.** The write tool needs a *separate*, more-privileged
   ServiceAccount (e.g. `patch` on `deployments/scale`). That elevation is the
   real gate. The pattern that fits this repo's posture: the read-only server
   runs with the read-only ServiceAccount, and any mutation is brokered through
   a distinct, audited path (the gateway) that holds the write credential and
   can require human approval, rather than handing write RBAC to the same
   surface the model talks to directly. The annotation tells the client to
   prompt; the gateway + RBAC make "no" actually mean no.

The honest framing: annotations drive the *prompt*, RBAC and the gateway drive
the *permission*. A demo that relies on the hint alone is teaching the
anti-pattern the spec warns against.

---

## 5. Version pin summary

| Component | Pin | Notes |
|---|---|---|
| `kubernetes` | `==36.0.2` | Latest as of 2026-06-01. Match to cluster minor (`36.x` = k8s 1.36). |
| Python | `>=3.10,<3.15` | Client tests 3.10 to 3.14. Use 3.12 for the build. |
| `fastmcp` | latest | Specific FastMCP version not pinned in this spike; verify the installed version against gofastmcp.com before shipping. |
| `mcp` (types) | provides `ToolAnnotations` | `from mcp.types import ToolAnnotations`. |

---

## Not confirmed / caveats

- **FastMCP version number.** gofastmcp.com documents the API surface but I did
  not capture a current FastMCP release number in this pass. Pin it explicitly
  from PyPI before building; the `@mcp.tool` and `ToolAnnotations` API shown here
  is current per the docs.
- **`config.load_incluster_config` exception type.** The try/except fallback
  uses `config.ConfigException`. The example files show the two loaders
  separately; the combined fallback pattern is idiomatic but the exact exception
  class should be verified against the installed client's source before relying
  on it for control flow.
- **Gateway specifics.** The "gateway" referenced in section 4 is this repo's
  own concept. The MCP-side consent mechanics (annotation-driven prompts) are
  confirmed from official sources; how the local gateway brokers the
  more-privileged write credential is a design decision for this project, not a
  quoted standard.

---

## Sources

- Kubernetes Python client repo and compatibility matrix: https://github.com/kubernetes-client/python
- Client on PyPI (version, Python support): https://pypi.org/project/kubernetes/
- In-cluster config example (verbatim): https://github.com/kubernetes-client/python/blob/master/examples/in_cluster_config.py
- V1Pod model source: https://github.com/kubernetes-client/python/blob/master/kubernetes/client/models/v1_pod.py
- Fake-client-for-unit-testing discussion: https://github.com/kubernetes-client/python/issues/524
- FastMCP tools (definition, annotations, structured output): https://gofastmcp.com/servers/tools
- Kubernetes RBAC (read-only Role + RoleBinding YAML): https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- MCP tool annotations as risk vocabulary (hints not enforcement, consent): https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/
