# ABOUTME: A deterministic, offline eval harness scoring MCP tool-design quality (no LLM, no network).
# ABOUTME: Measures namespacing, description, parameter clarity, pagination, and response conciseness.
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from fastmcp import Client

_log = logging.getLogger("mcp_tooling.eval_harness")

# Parameter names that signal a poorly-specified tool (ambiguous to the model).
_VAGUE_PARAM_NAMES = {"x", "data", "id", "input", "val", "value", "obj", "arg", "args", "payload"}

# Estimated token budget for a single tool response. A full-directory dump should blow this;
# a small, paginated page should fit. Token estimate is chars/4 (a standard rough proxy).
_TOKEN_BUDGET = 150


@dataclass(frozen=True)
class Scorecard:
    """The measured design qualities of one tool. score is the count of passed checks.

    concise_response is None when it was not measured (the harness only invokes read-only tools, so a
    non-read-only or required-param tool is never called). An unmeasured metric never earns its point,
    so score never credits an unverified property.
    """

    namespaced: bool
    described: bool
    clear_params: bool
    paginated: bool
    concise_response: bool | None

    @property
    def score(self) -> int:
        checks = [self.namespaced, self.described, self.clear_params, self.paginated, self.concise_response]
        return sum(1 for c in checks if c is True)


def _estimate_tokens(text: str) -> int:
    return len(text) // 4


def _response_text(result: Any) -> str:
    """Serialize a tool result to text for sizing, preferring structured content."""
    if result.structured_content is not None:
        return json.dumps(result.structured_content)
    return "".join(getattr(block, "text", "") or "" for block in result.content)


async def evaluate_server(client: Client) -> dict[str, Scorecard]:
    """Score every tool on the connected server. Deterministic: same server, same scores.

    Each tool is introspected via list_tools and the four static design metrics are scored from its
    schema. The response-size metric needs a call, which is best-effort: a tool with a required
    parameter cannot be invoked with empty arguments, so its response size is not measured (recorded as
    not-penalized and logged). No model or network is involved.
    """
    scores: dict[str, Scorecard] = {}
    for tool in await client.list_tools():
        schema = tool.inputSchema or {}
        param_names = set((schema.get("properties") or {}).keys())
        required = set(schema.get("required") or [])

        namespaced = "_" in tool.name and tool.name == tool.name.lower()
        description = (tool.description or "").strip()
        described = len(description) >= 20
        # A tool with no vague parameter names is clear, including a tool with no parameters at all.
        clear_params = param_names.isdisjoint(_VAGUE_PARAM_NAMES)
        paginated = bool(param_names & {"limit", "cursor", "page", "offset"})

        # Measuring response size means executing the tool, so it is gated on safety: invoke only a
        # tool the server declares read-only (readOnlyHint) and that takes no required arguments. A
        # non-read-only or required-param tool is never called (so the harness cannot mutate state), and
        # its conciseness is left unmeasured (None) rather than assumed to pass.
        annotations = tool.annotations
        read_only = bool(annotations is not None and annotations.readOnlyHint)
        concise_response: bool | None
        if read_only and not required:
            result = await client.call_tool(tool.name, {})
            concise_response = _estimate_tokens(_response_text(result)) <= _TOKEN_BUDGET
        else:
            skip = "not read-only" if not read_only else f"required params {sorted(required)}"
            _log.info("eval: %s response size unmeasured (%s)", tool.name, skip)
            concise_response = None

        scores[tool.name] = Scorecard(
            namespaced=namespaced,
            described=described,
            clear_params=clear_params,
            paginated=paginated,
            concise_response=concise_response,
        )
    return scores
