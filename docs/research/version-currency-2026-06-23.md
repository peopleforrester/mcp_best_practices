<!-- ABOUTME: Independently re-verified version/currency facts for the MCP portfolio, as of 2026-06-23.
ABOUTME: Source of truth where it diverges from the founding research report; refresh at build time. -->

# Version Currency: verified 2026-06-23

Two web-research spikes independently re-verified the fast-moving claims in
`mcp-sme-portfolio-research-2026-06.md` against official sources. Where this file and the
report disagree, **this file wins**. Re-verify anything here older than ~6 months at build time.

## Headline corrections to fold into the plan
1. **cosign is on the v3.x line (v3.0.0 GA in 2026; latest v3.1.1).** Pin v3, not v2. v3 makes
   the standardized Sigstore bundle format the default.
2. **Go SDK is already stable (v1.6.1, 2026-05-22)**: not "approaching stable ~August."
3. **Rust `rmcp` advanced to v1.7.0 (2026-05-13)**: report said v1.5.0.
4. **Python SDK v2 is still alpha (2.0.0a2); beta (target 2026-06-30) has NOT shipped.** Stable
   v1.x is **1.28.0**. Pin `mcp>=1.28,<2`.
5. **C#/.NET SDK does NOT require .NET 10**: core targets netstandard2.0/.NET 8 (runs on .NET 8
   LTS, 9, 10). Only the `dotnet new mcpserver` template / dnx distribution needs .NET 10.
6. **Pin Reveal.js to v6.0.1**; **cosign to v3.x**; other tools to the versions below.

## Spec & SDK currency (verified 2026-06-23)

- **Latest STABLE spec revision:** `2025-11-25` is current (released Nov 25, 2025, MCP's first anniversary; introduced Tasks, OIDC discovery, icon metadata). `modelcontextprotocol.io/specification` resolves to this. Source: https://modelcontextprotocol.io/specification/2025-11-25: ✓ matches report.
- **`2026-07-28` revision:** Still a **Release Candidate**. RC locked **2026-05-21**, final scheduled **2026-07-28** (10-week SDK-validation window). Delivers a stateless protocol core, Extensions framework, Tasks, MCP Apps, auth hardening, and a formal deprecation policy. No date or status change. Source: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/: ✓ matches report.
- **Python SDK (`mcp` on PyPI):** Latest stable **v1.28.0** (June 16, 2026), v1.x in maintenance mode and recommended for production. v2 latest pre-release is **2.0.0a2** (alpha, June 16, 2026): beta (target 2026-06-30) **has NOT shipped yet**; still alpha. Source: https://pypi.org/project/mcp/: ⚠ CHANGED: current stable is **1.28.0** and v2 remains **alpha (2.0.0a2)**, beta not yet released as of 2026-06-23.
- **FastMCP:** Latest **v3.4.2** (June 6, 2026). FastMCP 1.0 was folded into the official Python SDK in 2024; the standalone FastMCP project remains independently and actively maintained (~1M downloads/day; powers ~70% of MCP servers). Source: https://pypi.org/project/fastmcp/: ✓ matches report (now on the 3.x line, standalone).
- **TypeScript SDK (`@modelcontextprotocol/sdk` on npm):** Latest stable **v1.29.0**; v1.x recommended for production. v2 lives on `main` in pre-alpha development (companion `@modelcontextprotocol/client` published at `2.0.0-alpha.2`), stable v2 anticipated Q3 2026 alongside the new spec. Source: https://www.npmjs.com/package/@modelcontextprotocol/sdk: ✓ matches report (v1 stable, v2 pre-release).
- **Rust SDK (`rmcp`):** Latest **v1.7.0** (released 2026-05-13). Source: https://docs.rs/crate/rmcp/latest: ⚠ CHANGED: report said v1.5.0 by mid-April 2026; the crate has since advanced to **v1.7.0**.
- **Go SDK:** **v1.6.1** (May 22, 2026): already **v1.0 stable** (Google-maintained), past the "approaching stable" stage. Source: https://pkg.go.dev/github.com/modelcontextprotocol/go-sdk/mcp: ⚠ CHANGED: report said "approaching stable ~August"; it is **already stable at v1.6.1**.
- **C#/.NET SDK:** Stable; hit **v1.0 on 2026-03-05**, latest **v1.2.0** (March 27, 2026), Microsoft-maintained. Packages split into `ModelContextProtocol.Core`, `ModelContextProtocol`, `ModelContextProtocol.AspNetCore`; core targets `netstandard2.0`/.NET 8, so it runs on .NET 8 LTS, 9, and 10. Source: https://github.com/modelcontextprotocol/csharp-sdk: ⚠ CHANGED: .NET 10 is **NOT required** for the SDK itself; only the `dotnet new mcpserver` template and dnx distribution need .NET 10.

## Tooling & security tooling currency (verified 2026-06-23)

- **Reveal.js**: Latest **v6.0.1** (released ~April 2026); actively maintained by Hakim El Hattab, MIT-licensed. Source: https://github.com/hakimel/reveal.js/releases: ✓ matches report (pin v6.0.1).
- **MkDocs Material**: Confirmed in **maintenance mode**: announced **2025-11-05**, last feature release **9.7.0 on 2025-11-11** (merged all Insiders features into the public release and made Insiders free), bug/security fixes through at least **November 2026**. **Zensical** is the named, team-built successor (next-gen static site generator, reads `mkdocs.yml` natively for migration). Insiders repo scheduled for deletion 2026-05-01; an MkDocs 2.0 discussion exists (Feb 2026). Sources: https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/ , https://squidfunk.github.io/mkdocs-material/blog/2025/11/11/insiders-now-free-for-everyone/: ✓ matches report (feature-frozen at 9.7.0).
- **go-task (Taskfile)**: Latest **v3.51.1** (released **2026-05-17**). Source: https://github.com/go-task/task/releases: ✓ current.
- **uv (Astral)**: Latest **v0.11.23** (released **2026-06-19**). Source: https://github.com/astral-sh/uv/releases: ✓ current. **pnpm**: Latest **v11.8.0** (released ~2026-06-18); pnpm 11 GA was 2026-04-28 (requires Node.js ≥22, pure ESM, SQLite store index). Source: https://github.com/pnpm/pnpm/releases: ✓ current.
- **cosign / sigstore**: ⚠ CHANGED: cosign is now on the **v3.x** line (v3.0.0 GA in 2026; latest patch **v3.1.1**, with v2.6.2 on 2026-01-09 being the last planned v2 release). v3 makes the standardized Sigstore **bundle format** the default. **sigstore policy-controller** (Kubernetes admission controller) and **Kyverno** (`verifyImages` / `ImageValidatingPolicy` with Cosign) both remain supported, actively documented paths for admission-time signature/attestation verification. Sources: https://github.com/sigstore/cosign/releases , https://blog.sigstore.dev/cosign-3-0-available/ , https://kyverno.io/docs/policy-types/image-validating-policy/: ⚠ CHANGED: update any v2.x pin to v3.x GA.
- **agentgateway / kgateway**: Confirmed. **agentgateway** (Rust, AI-native MCP/A2A data plane) was contributed by Solo.io and accepted as a **Linux Foundation** project (contributors incl. AWS, Cisco, Huawei, IBM, Microsoft, Red Hat). **kgateway** is a **CNCF** project (Sandbox, accepted 2025-03-04), Envoy-based. **kgateway v2.1** (released **2025-11-18**) is the first version to integrate agentgateway; the Envoy-based AI Gateway and Inference Extension are being deprecated in favor of native agentgateway. Latest kgateway is in the **v2.3** line (v2.3.0-rc.1 seen 2026). Sources: https://www.linuxfoundation.org/press/linux-foundation-welcomes-agentgateway-project-to-accelerate-ai-agent-adoption-while-maintaining-security-observability-and-governance , https://www.cncf.io/blog/2025/11/18/kgateway-v2-1-is-released/: ✓ matches report.
- **CVE-2025-49596 (MCP Inspector RCE)**: Confirmed: CVSS **9.4**, critical RCE in Anthropic's MCP Inspector proxy (unauthenticated proxy + "0.0.0.0 Day" / DNS-rebinding browser exploit), reported by Oligo Security, **fixed in v0.14.1** (adds session-token auth and Host/Origin header validation). Sources: https://nvd.nist.gov/vuln/detail/CVE-2025-49596 , https://www.oligo.security/blog/critical-rce-vulnerability-in-anthropic-mcp-inspector-cve-2025-49596: ✓ matches report.
- **NSA MCP Cybersecurity Information Sheet**: Confirmed: "**Model Context Protocol (MCP): Security Design Considerations for AI-Driven Automation**," NSA Artificial Intelligence Security Center, **released 2026-05-20**, identifier **U/OO/6030316-26 (PP-26-1834), May 2026 Ver. 1.0**, ~17 pages. PDF: https://media.defense.gov/2026/Jun/02/2003943289/-1/-1/0/CSI_MCP_SECURITY.PDF (press release: https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/).: ✓ matches report (media.defense.gov 403s automated fetchers; corroborated via official-domain search snippets).

## Pinned versions (use these when scaffolding)

| Component | Pin |
|---|---|
| MCP spec | `2025-11-25` (stable); `2026-07-28` RC preview-only |
| Python SDK | `mcp>=1.28,<2` |
| FastMCP | `3.4.x` |
| TypeScript SDK | `@modelcontextprotocol/sdk@^1.29` |
| Rust SDK | `rmcp@1.7` |
| Go SDK | `github.com/modelcontextprotocol/go-sdk@v1.6.1` |
| C#/.NET SDK | `ModelContextProtocol.Core@1.2` (targets .NET 8+) |
| Reveal.js | `6.0.1` |
| MkDocs Material | `9.7.x` (maintenance mode; watch Zensical) |
| go-task | `3.51.x` |
| uv | `0.11.x` |
| pnpm | `11.8.x` (Node ≥22) |
| cosign | `3.x` (GA; bundle format default) |
