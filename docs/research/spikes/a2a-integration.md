<!-- ABOUTME: Research spike on the A2A (Agent-to-Agent) protocol and how it composes with MCP. -->
<!-- ABOUTME: Verified against a2a-protocol.org, github.com/a2aproject, modelcontextprotocol.io as of 2026-06-24. -->

# A2A + MCP Integration Spike

Date: 2026-06-24
Status: fresh

A2A reached v1.0 on 2026-03-12, is governed by the Linux Foundation (Agent2Agent
Protocol Project, hosted since June 2025), and is the agent-to-agent counterpart to
MCP's agent-to-tool focus. This spike records what is confirmable from official
sources for a use-cases demo.

## 1. What A2A is, and how it differs from MCP

A2A standardizes how independent, often opaque, AI agents discover one another,
delegate tasks, and exchange data as peers. MCP standardizes how a single agent or
model connects to tools, APIs, and external resources. The official A2A docs state
the split plainly: "The distinction between A2A and MCP depends on what an agent
interacts with." Tools and resources are stateless primitives with defined inputs
and outputs (MCP); agents are autonomous systems that reason, plan, hold state, and
hold multi-turn dialogue (A2A).

The consensus "MCP + A2A" stack is complementary, not competing. From the official
A2A-and-MCP topic page: "An agentic application might primarily use A2A to communicate
with other agents. Each individual agent internally uses MCP to interact with its
specific tools and resources." A2A is the horizontal layer between agents; MCP is the
vertical layer from one agent down to its tools.

Sources:
- A2A and MCP (official): https://a2a-protocol.org/latest/topics/a2a-and-mcp/
- MCP spec: https://modelcontextprotocol.io
- LF launch press: https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents

## 2. Core A2A concepts

From the official specification (https://a2a-protocol.org/latest/specification/):

- Agent Card: "A JSON metadata document published by an A2A Server, describing its
  identity, capabilities, skills, service endpoint, and authentication requirements."
  Fields include `name`, `description`, `version`, `url`, `capabilities`,
  `defaultInputModes`/`defaultOutputModes`, and a list of `skills` (AgentSkill).
  v1.0 added Signed Agent Cards.
- Task: "The fundamental unit of work managed by A2A, identified by a unique ID.
  Tasks are stateful and progress through a defined lifecycle." Fields: `id`,
  `contextId`, `status`, `artifacts`, `history`, `metadata`.
- Message: "One unit of communication between client and server." Required: `messageId`,
  `role` (`user`/`agent`), `parts`. A `Part` carries text, bytes/file, or structured
  JSON data.
- Core RPC methods: Send Message (returns a Task or a Message), Send Streaming Message,
  Get Task.

### Agent Card discovery path

The canonical well-known path in v1.0 is `/.well-known/agent-card.json`. This is
confirmed by the SDK client, which "will search for an AgentCard at
`/.well-known/agent-card.json` when given an agent URL." Older 0.x material and some
tutorials reference `/.well-known/agent.json`; treat that as legacy.

FLAG: The exact spec section text (14.3 Well-Known URI Registration) was truncated in
the fetched pages, so the path is confirmed from official SDK behavior rather than a
verbatim spec sentence. The two agree.

### Python SDK package and minimal snippets

Package: `a2a-sdk` (`pip install a2a-sdk` or `uv add a2a-sdk`). Requires Python >= 3.10.
Import roots: `a2a.types`, `a2a.server.apps`, `a2a.server.request_handlers`,
`a2a.server.tasks`, `a2a.client`.

Expose (serve) an agent. Class names below are confirmed from the official SDK docs;
the agent-logic body is illustrative:

```python
from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

skill = AgentSkill(
    id="summarize",
    name="Summarize",
    description="Summarize a block of text.",
    tags=["text"],
)
card = AgentCard(
    name="Summarizer",
    description="Summarizes text.",
    version="1.0.0",
    url="http://localhost:9999/",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[skill],
)

handler = DefaultRequestHandler(
    agent_executor=MyExecutor(),   # your AgentExecutor subclass holds the core logic
    task_store=InMemoryTaskStore(),
)
app = A2AStarletteApplication(agent_card=card, http_handler=handler)
# serve app.build() with uvicorn; card is published at /.well-known/agent-card.json
```

Call an agent (client). Construction confirmed from the SDK client API docs:

```python
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig

async with httpx.AsyncClient() as http:
    card = await A2ACardResolver(http, "http://localhost:9999").get_agent_card()
    client = ClientFactory(ClientConfig(httpx_client=http)).create(card)
    async for event in client.send_message(my_send_message_request):
        ...   # Task / Message / streaming events
```

Sources:
- Python SDK repo: https://github.com/a2aproject/a2a-python
- PyPI: https://pypi.org/project/a2a-sdk/
- Client API docs: https://a2a-protocol.org/dev/sdk/python/api/a2a.client.html
- Specification: https://a2a-protocol.org/latest/specification/

## 3. Minimal MCP + A2A integration pattern

The clean demo pattern is an MCP server whose tool delegates to a remote agent over
A2A. The host (a Claude Code session, say) calls an MCP tool `delegate_summary`; the
MCP server is, internally, an A2A client that resolves a remote agent's card and sends
it a message.

```python
# MCP server side (FastMCP), acting as an A2A client inside one tool
from mcp.server.fastmcp import FastMCP
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig

mcp = FastMCP("bridge")

@mcp.tool()
async def delegate_summary(text: str, agent_url: str) -> str:
    async with httpx.AsyncClient() as http:
        card = await A2ACardResolver(http, agent_url).get_agent_card()
        client = ClientFactory(ClientConfig(httpx_client=http)).create(card)
        # build a Message with a text Part = text, send, collect the agent reply
        ...
        return reply_text
```

The mirror pattern also holds: an A2A agent whose `AgentExecutor` internally calls MCP
tools (a diagnostic scanner, a database). The official auto-repair-shop example in the
A2A-and-MCP topic page describes exactly this: shop agents coordinate over A2A while
each uses MCP for its own scanners and manuals.

### What can be unit-tested without a network

- Agent Card construction and serialization: build an `AgentCard`, assert fields and
  JSON shape. No I/O.
- Skill routing inside an `AgentExecutor`: feed it a constructed `Message`/`Part`,
  assert the produced `Task`/`Message`. No I/O.
- The MCP tool's request-building logic: factor the "text to A2A Message" mapping into
  a pure function and assert it.
- The card-resolution + send path: inject a stubbed `httpx.AsyncClient` (or a
  `MockTransport`) so `A2ACardResolver` reads a fixed `agent-card.json` and the send
  returns a canned Task. `httpx` ships an ASGI/transport mock that keeps this in-process.

What genuinely needs a network (integration tier, not unit): a real `uvicorn`-served
A2AStarletteApplication and a real socket between the MCP server and the A2A agent.
Per the project's NO-EXCEPTIONS testing rule, no mock-mode shortcuts in shipped code;
the stubs above are test doubles in the test tier only.

## 4. Current versions and pins

| Component | Pin | Source |
|---|---|---|
| A2A protocol spec | v1.0 (released 2026-03-12) | LF / a2a-protocol.org |
| `a2a-sdk` (Python) | `1.1.0` (released 2026-05-29) | PyPI |
| `a2a-sdk` protocol compliance | implements spec `1.0`, compat mode for `0.3` | PyPI / repo |
| Python floor | `>=3.10` | PyPI |
| SDK extras | all, db-cli, encryption, fastapi, grpc, http-server, mysql, postgresql, signing, sql, sqlite, telemetry | PyPI |

Suggested pin for the demo: `a2a-sdk>=1.1,<2` with the `http-server` (or `fastapi`)
extra for the server side. Other official SDKs exist for JavaScript, Java, Go, and .NET.

## Flags / not fully confirmable from official sources

- The verbatim spec sentence for the `/.well-known/agent-card.json` path was not
  captured (section 14.3 truncated in fetch). Path is confirmed from official SDK
  client behavior instead; the two are consistent.
- SDK code snippets above use confirmed class and method names from the official repo
  and client API docs, but were assembled into minimal examples rather than copied
  verbatim from a single official file. Validate against the `a2a-samples` Hello World
  before using in the demo: https://github.com/a2aproject/a2a-samples
- `AgentExecutor`, `Message`/`Part` construction, and `SendMessageRequest` field shapes
  should be checked against the installed `a2a-sdk` 1.1.0 types at build time; field
  naming (snake_case vs the spec's camelCase JSON) is handled by the SDK models but the
  exact constructor signatures were not captured verbatim here.
