<!-- ABOUTME: Research spike on advanced FastMCP 3.x (Python) features for a Fundamentals client and a Tooling track. -->
<!-- ABOUTME: Verified against gofastmcp.com and the MCP spec on 2026-06-24; quotes the official docs for load-bearing API signatures. -->

# FastMCP Advanced Features (Python)

Spike date: 2026-06-24. Sources are the official FastMCP docs at gofastmcp.com
and the Model Context Protocol specification at modelcontextprotocol.io. API
signatures are quoted from those docs, not from training data. Pagination and
resource subscriptions are documented as "New in version 3.0.0"; the rest of
the surface below is current on the 3.x line.

Anything I could not confirm from an official page is flagged inline as
NOT CONFIRMED.

## 1. The FastMCP `Client` for in-memory testing

The in-memory transport connects the client directly to a `FastMCP` server
instance in the same Python process, with no network or subprocess. Pass the
server object straight to the `Client` constructor.

```python
from fastmcp import Client, FastMCP

server = FastMCP("TestServer")
client = Client(server)  # in-memory transport, inferred from the server instance
```

All client operations run inside the `async with` context manager, which owns
the connection lifecycle. Entering the context performs the MCP initialization
handshake automatically.

```python
async with Client(server) as client:
    await client.ping()
    tools = await client.list_tools()
    result = await client.call_tool("multiply", {"a": 5, "b": 3})
```

Source: https://gofastmcp.com/clients/client and
https://gofastmcp.com/clients/transports

### Listing tools

`await client.list_tools()` returns the full list of tool definitions. The
client fetches all pages transparently (see section 6). Each definition carries
`name`, `description`, `inputSchema`, optional `outputSchema`, and optional
`annotations`.

### Calling tools and reading the result

```python
result = await client.call_tool(
    name, arguments, timeout=None, progress_handler=None,
    raise_on_error=True, meta=None,
)
```

The return value is a `CallToolResult` with these fields (quoted from the docs):

| Field | Type | Meaning |
|---|---|---|
| `.data` | `Any` | FastMCP-only: fully hydrated Python objects (datetimes, UUIDs, custom types). `None` when the tool has no output schema. |
| `.content` | `list[mcp.types.ContentBlock]` | Standard MCP content blocks (TextContent, ImageContent, AudioContent). |
| `.structured_content` | `dict[str, Any] \| None` | Standard MCP structured JSON exactly as sent by the server. |
| `.is_error` | `bool` | Whether the call failed. |

`.data` is the FastMCP convenience layer: it deserializes `.structured_content`
back into rich Python objects. `.structured_content` is the raw JSON before that
reconstruction. `.content` is the protocol-standard, cross-client fallback. For
legacy tools with no output schema, `.data is None`, so read `.content` (for
example `result.content[0].text`).

```python
result = await client.call_tool("multiply", {"a": 5, "b": 3})
assert result.data == 15                 # hydrated Python value
assert result.content[0].text == "15"    # standard MCP block
```

Source: https://gofastmcp.com/clients/tools

### Capability negotiation

Entering the context manager runs the initialization handshake, which exchanges
capabilities, server metadata, and instructions. The negotiated result is on the
connected client as `client.initialize_result`.

```python
async with Client(server) as client:
    print(client.initialize_result.serverInfo.name)
    print(client.initialize_result.instructions)
    print(client.initialize_result.capabilities.tools)
```

`auto_initialize=False` defers the handshake so you can call
`await client.initialize()` yourself.

Source: https://gofastmcp.com/clients/client

## 2. Progress reporting and cancellation

### Reporting progress from a tool

A tool gets the `Context` object by declaring a parameter typed `Context`
(FastMCP injects it). In v2.14+, the documented preferred form is
`ctx: Context = CurrentContext()` from `fastmcp.dependencies`; the legacy
type-hint injection (`ctx: Context` parameter) still works. For helper functions
that lack the parameter, `get_context()` from `fastmcp.server.dependencies`
retrieves the active context.

```python
from fastmcp import Context

@mcp.tool
async def process(items: list[str], ctx: Context) -> str:
    total = len(items)
    for i, item in enumerate(items):
        await ctx.report_progress(progress=i, total=total)
        ...
    await ctx.report_progress(progress=total, total=total)
    return "done"
```

`ctx.report_progress()` takes `progress` (work done so far) and optional `total`
(full scope). The docs show only `progress` and `total` in the server-side
examples. The client-side progress handler receives a third `message` argument,
so a `message` parameter on `report_progress` is plausible but is
NOT CONFIRMED from the server-side docs.

Source: https://gofastmcp.com/servers/progress and
https://gofastmcp.com/servers/context

### Receiving progress on the client

Register a `progress_handler` on the `Client` (or per call on `call_tool`). The
handler signature is documented as:

```python
async def progress_handler(
    progress: float,
    total: float | None,
    message: str | None,
) -> None:
    ...

client = Client("my_server.py", progress_handler=progress_handler)
```

Source: https://gofastmcp.com/clients/progress

### Cancellation

The MCP protocol cancels an in-flight request with a `notifications/cancelled`
message carrying the original request id. In the Python async stack this
surfaces inside the running tool as `asyncio.CancelledError` propagating through
the task. The official FastMCP docs do not currently document a tool-author API
for observing or cleanly handling cancellation; server-side tool cancellation is
tracked as an open feature request (jlowin/fastmcp issue #1305), and several
issues describe `CancelledError` propagating on client disconnect (#508) and on
client-side cancel (python-sdk #1152, #1410). Treat clean mid-tool cancellation
handling as NOT CONFIRMED in the public docs as of this spike; design tools to
tolerate `CancelledError` rather than to rely on a documented hook.

Sources: https://github.com/jlowin/fastmcp/issues/1305 ,
https://github.com/jlowin/fastmcp/issues/508 ,
https://github.com/modelcontextprotocol/python-sdk/issues/1410

## 3. Tool annotations

Set the four behavior hints with `ToolAnnotations` passed to the `annotations`
parameter of the `@mcp.tool` decorator.

```python
from mcp.types import ToolAnnotations

@mcp.tool(
    annotations=ToolAnnotations(
        title="Calculate Sum",
        readOnlyHint=True,
        openWorldHint=False,
    )
)
def calculate_sum(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b
```

The hints (quoted from the FastMCP docs):

- `readOnlyHint`: the tool only reads, makes no changes.
- `destructiveHint`: for non-read-only tools, signals whether changes are
  destructive.
- `idempotentHint`: repeated identical calls have the same effect as one call.
- `openWorldHint`: the tool interacts with external systems.

Source: https://gofastmcp.com/servers/tools

### Spec note: annotations are untrusted

The MCP specification is explicit. Verbatim from the 2025-06-18 tools spec:

> For trust & safety and security, clients MUST consider tool annotations to be
> untrusted unless they come from trusted servers.

A tool with no annotations is assumed worst-case: non-read-only, potentially
destructive, non-idempotent, and open-world. Hints are advice, not guarantees;
a client decides how much weight to give them based on whether the server is
trusted.

Source: https://modelcontextprotocol.io/specification/2025-06-18/server/tools

## 4. Structured output

FastMCP generates an output schema from the function's return type annotation:
"When you add return type annotations to your functions, FastMCP automatically
generates JSON schemas that describe the expected output format."

For a primitive return type (for example `int`), FastMCP wraps the value under a
`"result"` key to form a valid object-typed structured output.

Override the generated schema with the `output_schema` parameter on the
decorator:

```python
@mcp.tool(output_schema={
    "type": "object",
    "properties": {
        "data": {"type": "string"},
        "metadata": {"type": "object"},
    },
})
def custom_schema_tool() -> dict:
    """Tool with a custom output schema."""
    return {"data": "Hello", "metadata": {"version": "1.0"}}
```

`structuredContent` is the result field that carries the JSON object alongside
the traditional `content` blocks, so clients can deserialize programmatically
instead of parsing text. Per the spec: when an output schema is provided the
server MUST return structured results that conform to it, the client SHOULD
validate against it, and for backward compatibility the tool SHOULD also return
the serialized JSON inside a TextContent block.

Sources: https://gofastmcp.com/servers/tools and
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

## 5. Elicitation

`ctx.elicit()` pauses tool execution to request a value from the user. Signature
from the docs:

```python
await ctx.elicit(
    message: str,
    response_type: Type,
    response_title: str | None = None,
    response_description: str | None = None,
)
```

Return shape: the result has `action` (one of `"accept"`, `"decline"`,
`"cancel"`) and `data` (the user value, or `None` when no response type was
requested). It is pattern-matchable as `AcceptedElicitation`,
`DeclinedElicitation`, or `CancelledElicitation`.

```python
result = await ctx.elicit("Enter your name:", response_type=str)
if result.action == "accept":
    name = result.data
elif result.action == "decline":
    ...
else:  # "cancel"
    ...
```

Allowed response types (the MCP spec restricts elicitation to JSON objects with
primitive properties; FastMCP auto-wraps scalars):

- Scalars: `str`, `int`, `bool`.
- Constrained options: `Literal[...]`, a list of strings as shorthand, or a
  Python `Enum`.
- Multi-select: list-of-list shorthand, or `list[EnumType]`.
- Structured: dataclass, `TypedDict`, or Pydantic `BaseModel` whose properties
  are scalars or enums only.
- Approval-only flows: `None` (no data expected).

Use elicitation for missing parameters, clarification, progressive disclosure of
complex input, and approval gates inside a running tool. Always handle all three
actions; a client may decline or cancel.

Sources: https://gofastmcp.com/servers/elicitation and
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

## 6. Pagination and resource subscriptions

### Pagination (New in version 3.0.0)

A server enables paging by setting `list_page_size` on the constructor:

```python
server = FastMCP("ComponentRegistry", list_page_size=50)
```

This caps items per page on `tools/list`, `resources/list`,
`resources/templates/list`, and `prompts/list`. The client convenience methods
(`list_tools()`, `list_resources()`, `list_resource_templates()`,
`list_prompts()`) fetch every page and return the complete list automatically.

For manual control, the `_mcp` variants take a cursor and return the raw
protocol object with items plus `nextCursor`:

```python
result = await client.list_tools_mcp(cursor=None)
while result.nextCursor:
    result = await client.list_tools_mcp(cursor=result.nextCursor)
```

Cursors are opaque base64 strings per the spec; treat them as black boxes and
pass them unchanged. `nextCursor is None` means the end of the result set.

Sources: https://gofastmcp.com/servers/pagination and
https://modelcontextprotocol.io/specification/2025-06-18/server/tools

### Resource subscriptions and list-changed notifications

FastMCP sends `notifications/resources/list_changed` to connected clients when
resources or templates are added, enabled, or disabled, so a client stays
current without polling. The protocol also defines per-resource subscriptions
(the client subscribes to a resource URI and receives update notifications);
resource links returned by tools are subscribable. The exact FastMCP server-side
API for emitting per-URI `resources/updated` notifications (versus the
list-changed notification above) is NOT CONFIRMED from the pages reviewed in
this spike; the list-changed behavior is confirmed.

Sources: https://gofastmcp.com/servers/resources and
https://gofastmcp.com/clients/resources
