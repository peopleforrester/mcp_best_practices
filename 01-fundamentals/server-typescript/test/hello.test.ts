// ABOUTME: Conformance-style tests for the TS hello server over the SDK in-memory transport pair.
// ABOUTME: Exercises capability negotiation, the echo tool, the templated resource, and the prompt.
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { describe, expect, it } from "vitest";

import { buildHelloServer } from "../src/hello";

async function connectedClient(): Promise<Client> {
  const server = buildHelloServer();
  const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
  const client = new Client({ name: "test-client", version: "0.1.0" });
  await Promise.all([server.connect(serverTransport), client.connect(clientTransport)]);
  return client;
}

describe("fundamentals hello server (TypeScript)", () => {
  it("lists the echo tool after capability negotiation", async () => {
    const client = await connectedClient();
    const { tools } = await client.listTools();
    expect(tools.map((t) => t.name)).toContain("echo");
  });

  it("echoes the input text", async () => {
    const client = await connectedClient();
    const result = await client.callTool({ name: "echo", arguments: { text: "hello mcp" } });
    const content = result.content as Array<{ type: string; text: string }>;
    expect(content.length).toBeGreaterThan(0);
    expect(content[0]?.text).toBe("hello mcp");
  });

  it("reads the templated greeting resource", async () => {
    const client = await connectedClient();
    const result = await client.readResource({ uri: "greeting://world" });
    const contents = result.contents as Array<{ text: string }>;
    expect(contents.length).toBeGreaterThan(0);
    expect(contents[0]?.text).toContain("world");
  });

  it("exposes the summarize prompt", async () => {
    const client = await connectedClient();
    const { prompts } = await client.listPrompts();
    expect(prompts.map((p) => p.name)).toContain("summarize");
  });
});
