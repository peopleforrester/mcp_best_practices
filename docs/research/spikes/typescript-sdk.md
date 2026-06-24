<!-- ABOUTME: Research spike on the official TypeScript MCP SDK (@modelcontextprotocol/sdk v1.29) covering server, client, transports, testing, and packaging.
ABOUTME: Verified against github.com/modelcontextprotocol/typescript-sdk (v1.x branch) and the v1 docs site on 2026-06-24; pin ^1.29. -->

---
created: 2026-06-24
topic: typescript-sdk
status: fresh
---

# TypeScript MCP SDK (`@modelcontextprotocol/sdk`)

Spike date: 2026-06-24. Verified against the official repository
`github.com/modelcontextprotocol/typescript-sdk` and the v1 docs at
`ts.sdk.modelcontextprotocol.io`.

## Version and the v1/v2 split

The latest published stable release on npm is **`1.29.0`**
(`registry.npmjs.org/@modelcontextprotocol/sdk/latest`). Pin it as `^1.29`.

A caveat that bites immediately: the repository `main` branch is now **v2,
pre-alpha and in development**. The `main` README states verbatim: "This is
the `main` branch which contains v2 of the SDK (currently in development,
pre-alpha)." The stable v1 source lives on the **`v1.x` branch**, and the v1
API docs are at `ts.sdk.modelcontextprotocol.io`. Reading code off `main` will
give v2 shapes that do not match a `^1.29` install. Everything below is the
v1.x API.

The stable protocol spec this SDK targets is **2025-11-25**. The
**2026-07-28** revision is a release candidate, not final, so do not build
against it yet.

Source URLs:

- Repository (note: `main` is v2): https://github.com/modelcontextprotocol/typescript-sdk
- v1.x branch: https://github.com/modelcontextprotocol/typescript-sdk/tree/v1.x
- v1 API docs: https://ts.sdk.modelcontextprotocol.io/
- npm package: https://www.npmjs.com/package/@modelcontextprotocol/sdk

## 1. Minimal server

The high-level server class is `McpServer`, imported from
`@modelcontextprotocol/sdk/server/mcp.js`.

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

const server = new McpServer({ name: 'my-server', version: '1.0.0' });
```

### Register a tool

`registerTool(name, config, handler)`. The `inputSchema` and `outputSchema`
are a **Zod raw shape** (a plain object of Zod validators), not a wrapped
`z.object(...)`. When `outputSchema` is set, the handler should return
`structuredContent` alongside `content`.

```typescript
server.registerTool(
    'calculate-bmi',
    {
        title: 'BMI Calculator',
        description: 'Calculate Body Mass Index',
        inputSchema: {
            weightKg: z.number(),
            heightM: z.number()
        },
        outputSchema: { bmi: z.number() }
    },
    async ({ weightKg, heightM }) => {
        const output = { bmi: weightKg / (heightM * heightM) };
        return {
            content: [{ type: 'text', text: JSON.stringify(output) }],
            structuredContent: output
        };
    }
);
```

### Register a resource

`registerResource(name, template, metadata, handler)`. Dynamic resources use
`ResourceTemplate` with a URI template; template variables are passed to the
handler as the second argument.

```typescript
import { ResourceTemplate } from '@modelcontextprotocol/sdk/server/mcp.js';

server.registerResource(
    'user-profile',
    new ResourceTemplate('users://{userId}/profile', { list: undefined }),
    { title: 'User Profile', mimeType: 'application/json' },
    async (uri, { userId }) => ({
        contents: [
            { uri: uri.href, text: JSON.stringify(await getUser(userId)) }
        ]
    })
);
```

### Register a prompt

`registerPrompt(name, config, handler)`. Note the prompt argument schema key
is **`argsSchema`** (not `inputSchema`), also a Zod raw shape.

```typescript
server.registerPrompt(
    'review-code',
    {
        title: 'Code Review',
        description: 'Review code for best practices and potential issues',
        argsSchema: { code: z.string() }
    },
    ({ code }) => ({
        messages: [
            {
                role: 'user',
                content: { type: 'text', text: `Please review this code:\n\n${code}` }
            }
        ]
    })
);
```

## 2. Transports

### stdio

`StdioServerTransport` from `@modelcontextprotocol/sdk/server/stdio.js`. The
server reads JSON-RPC over stdin/stdout. This is the transport a local MCP
client (Claude Desktop, an IDE) spawns as a subprocess.

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new McpServer({ name: 'my-server', version: '1.0.0' });
// ... register tools, resources, prompts ...

const transport = new StdioServerTransport();
await server.connect(transport);
```

Run it with `node build/index.js`. Do not write anything other than protocol
JSON to stdout, because the transport owns that channel; send logs to stderr.

### Streamable HTTP

`StreamableHTTPServerTransport` from
`@modelcontextprotocol/sdk/server/streamableHttp.js`. This is the recommended
transport for remote servers. The transport is mounted on an HTTP route
(commonly Express `POST /mcp`) and you call `transport.handleRequest(req, res,
req.body)` to drive it. A `sessionIdGenerator` enables session reuse.

```typescript
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { randomUUID } from 'node:crypto';

// inside the POST /mcp handler, for a new session:
transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
    eventStore,
    onsessioninitialized: sessionId => {
        transports[sessionId] = transport;
    }
});

const server = getServer();
await server.connect(transport);

await transport.handleRequest(req, res, req.body);
```

The transport also accepts `enableDnsRebindingProtection`, `allowedHosts`, and
`allowedOrigins` options. The docs recommend enabling DNS-rebinding protection
and constraining allowed hosts/origins for any locally-bound HTTP server so a
malicious web page cannot reach it. The reference example
(`src/examples/server/simpleStreamableHttp.ts`) does not set them, so treat
those as opt-in hardening you add deliberately.

Source: https://github.com/modelcontextprotocol/typescript-sdk/blob/v1.x/src/examples/server/simpleStreamableHttp.ts

## 3. Minimal client

`Client` from `@modelcontextprotocol/sdk/client/index.js`. Construct it,
connect a transport, then use the high-level helpers `listTools`, `callTool`,
`listResources`, `readResource`, `listPrompts`, `getPrompt`.

```typescript
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const transport = new StdioClientTransport({
    command: 'node',
    args: ['server.js'],
    env: { NODE_ENV: 'production' },
    cwd: '/path/to/server'
});

const client = new Client({ name: 'my-client', version: '1.0.0' });
await client.connect(transport);

const page = await client.listTools();        // { tools, nextCursor? }
const result = await client.callTool({
    name: 'add',
    arguments: { a: 21, b: 21 }
});
// result.content, result.structuredContent, result.isError
```

`callTool` resolves rather than throws on a tool failure, so inspect
`result.isError` and the returned `content`. `listTools` accepts an optional
`{ cursor }` and returns `{ tools, nextCursor }` for pagination.

For remote servers use `StreamableHTTPClientTransport` from
`@modelcontextprotocol/sdk/client/streamableHttp.js`, constructed with a
`URL`:

```typescript
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';

const transport = new StreamableHTTPClientTransport(new URL(serverUrl));
await client.connect(transport);
```

### Capability negotiation

Capabilities are declared in the second `Client` constructor argument and
exchanged during `connect` (the MCP `initialize` handshake). The handshake is
automatic; you only declare what your side supports.

```typescript
const client = new Client(
    { name: 'my-client', version: '1.0.0' },
    { capabilities: { roots: { listChanged: true } } }
);
```

After connecting, the client knows the server's advertised capabilities, and
calling an unsupported method is rejected. The lower-level escape hatch is
`client.request(request, ResultSchema)` with the schemas exported from
`@modelcontextprotocol/sdk/types.js` (e.g. `ListToolsResultSchema`,
`CallToolResultSchema`); the example client uses this form, but the high-level
helpers above are preferred for ordinary use.

Source: https://github.com/modelcontextprotocol/typescript-sdk/blob/v1.x/src/examples/client/simpleStreamableHttp.ts

## 4. Testing

The SDK ships an in-memory transport pair so a client and server can talk
in-process with no subprocess. `InMemoryTransport.createLinkedPair()` returns
a two-element tuple of linked transports; give one to the client and one to
the server.

```typescript
static createLinkedPair(): [InMemoryTransport, InMemoryTransport]
```

```typescript
import { InMemoryTransport } from '@modelcontextprotocol/sdk/inMemory.js';

const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
await Promise.all([
    client.connect(clientTransport),
    server.connect(serverTransport)
]);

const result = await client.callTool({ name: 'add', arguments: { a: 1, b: 2 } });
```

Recommended runner is **vitest**. Minimal setup:

```bash
pnpm add -D vitest
```

```json
// package.json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

vitest reads native ESM and TypeScript without extra config for most setups;
add a `vitest.config.ts` only when you need path aliases or a non-default
environment. The in-memory pair plus vitest is the standard unit-test loop:
register tools on a real `McpServer`, link it to a real `Client`, and assert on
`callTool` results without spawning a process.

Source: https://github.com/modelcontextprotocol/typescript-sdk/blob/v1.x/src/inMemory.ts

## 5. Packaging with pnpm

The SDK is ESM-only and ships its own types. The package consumes it as a
normal dependency; tooling is dev dependencies.

```json
// package.json
{
  "name": "my-mcp-server",
  "version": "0.1.0",
  "type": "module",
  "bin": { "my-mcp-server": "build/index.js" },
  "files": ["build"],
  "scripts": {
    "build": "tsc && chmod +x build/index.js",
    "start": "node build/index.js",
    "test": "vitest run"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.29",
    "zod": "^3"
  },
  "devDependencies": {
    "typescript": "^5",
    "vitest": "^3",
    "@types/node": "^22"
  }
}
```

`"type": "module"` is required because the SDK is ESM and all its import paths
carry the `.js` extension. The `bin` entry is what lets a client launch the
server over stdio.

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true
  },
  "include": ["src/**/*"]
}
```

`module`/`moduleResolution` set to `Node16` (or `NodeNext`) is what makes the
SDK's explicit `.js` import specifiers resolve correctly under ESM. Build with
`pnpm build`; the compiled entry is `build/index.js`.

## Open items / not confirmed from official source

- The exact public **import path for `InMemoryTransport`** is given here as
  `@modelcontextprotocol/sdk/inMemory.js`, inferred from the source file
  `src/inMemory.ts` and the package's file-per-module export convention. The
  v1.x source confirms the file and the `createLinkedPair` signature; the
  literal published subpath was not quoted from a docs page in this spike.
  Verify against the installed package's `package.json` `exports` map before
  relying on it.
- `enableDnsRebindingProtection` / `allowedHosts` / `allowedOrigins` are
  documented transport options but were not shown set in the reference
  example. Confirm their exact types against the installed
  `StreamableHTTPServerTransport` type definitions when wiring them.
- The `tsconfig.json` and `package.json` shapes above follow standard ESM
  Node conventions and the SDK's ESM requirement; they are not lifted verbatim
  from an official scaffold. Treat them as a sound starting point, not a quoted
  canonical file.
