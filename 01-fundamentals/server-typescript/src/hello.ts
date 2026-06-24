// ABOUTME: TypeScript MCP hello server mirroring the Python one (echo tool, greeting resource, prompt).
// ABOUTME: Built on @modelcontextprotocol/sdk v1.x; buildHelloServer returns a connectable McpServer.
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function buildHelloServer(): McpServer {
  const server = new McpServer({ name: "fundamentals-hello-ts", version: "0.1.0" });

  server.registerTool(
    "echo",
    {
      title: "Echo",
      description: "Return the given text unchanged. The smallest possible tool.",
      inputSchema: { text: z.string() },
    },
    async ({ text }) => ({ content: [{ type: "text", text }] }),
  );

  server.registerResource(
    "greeting",
    new ResourceTemplate("greeting://{name}", { list: undefined }),
    { title: "Greeting", description: "A templated greeting resource." },
    async (uri, variables) => ({
      contents: [{ uri: uri.href, text: `Hello, ${String(variables.name)}!` }],
    }),
  );

  server.registerPrompt(
    "summarize",
    {
      title: "Summarize",
      description: "A reusable prompt asking for a short summary of a topic.",
      argsSchema: { topic: z.string() },
    },
    ({ topic }) => ({
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Summarize the key points about ${topic} in three bullets.`,
          },
        },
      ],
    }),
  );

  return server;
}
