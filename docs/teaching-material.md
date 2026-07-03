<!-- ABOUTME: Site index of the portfolio's teaching artifacts that live in the track directories.
ABOUTME: They link to source on GitHub; their track-relative links to sibling code do not resolve off-tree. -->

# Teaching material

The planning and research docs are in this site's nav. The teaching artifacts, one guidebook and one
Reveal.js deck per track, the STRIDE threat models, the ecosystem map, and the exam curriculum, live
next to the code they explain (their links point at sibling source, so they read best in the tree or
on GitHub). Each is linked below.

!!! note "Live demo"
    The exam-prep quiz app runs at
    [mcp-exam-quiz-production.up.railway.app](https://mcp-exam-quiz-production.up.railway.app).

## Guidebooks

One per track, narrating the design decisions behind the code.

- [Security (flagship)](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/guidebook.md)
- [Fundamentals](https://github.com/peopleforrester/mcp_best_practices/blob/main/01-fundamentals/guidebook.md)
- [Tooling](https://github.com/peopleforrester/mcp_best_practices/blob/main/03-tooling/guidebook.md)
- [Architecture](https://github.com/peopleforrester/mcp_best_practices/blob/main/02-architecture/guidebook.md)
- [Use cases & ecosystem](https://github.com/peopleforrester/mcp_best_practices/blob/main/05-use-cases-ecosystem/guidebook.md)
- [Exam prep](https://github.com/peopleforrester/mcp_best_practices/blob/main/06-exam-prep/guidebook.md)

## Threat models

STRIDE per trust zone, each threat mapped to OWASP MCP Top 10 + NSA CSI, with an explicit
implemented-vs-target-design boundary.

- [Overview + cross-component map](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/README.md)
- [Host](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/host.md)
  · [Client](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/client.md)
  · [LLM](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/llm.md)
  · [Server](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/server.md)
  · [Data stores](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/data-stores.md)
  · [Auth server](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/threat-models/auth-server.md)

## Slide decks

Reveal.js decks per track (open the `slides/index.html` for each).

- [Security](https://github.com/peopleforrester/mcp_best_practices/blob/main/04-security/slides/index.html)
  · [Fundamentals](https://github.com/peopleforrester/mcp_best_practices/blob/main/01-fundamentals/slides/index.html)
  · [Tooling](https://github.com/peopleforrester/mcp_best_practices/blob/main/03-tooling/slides/index.html)
  · [Architecture](https://github.com/peopleforrester/mcp_best_practices/blob/main/02-architecture/slides/index.html)
  · [Use cases](https://github.com/peopleforrester/mcp_best_practices/blob/main/05-use-cases-ecosystem/slides/index.html)
  · [Exam prep](https://github.com/peopleforrester/mcp_best_practices/blob/main/06-exam-prep/slides/index.html)

## Other

- [Ecosystem map](https://github.com/peopleforrester/mcp_best_practices/blob/main/05-use-cases-ecosystem/ecosystem-map.md):
  adoption claims labeled verified vs vendor-reported.
- [Exam curriculum](https://github.com/peopleforrester/mcp_best_practices/blob/main/06-exam-prep/curriculum/README.md):
  the ordered study path behind the quiz app.
