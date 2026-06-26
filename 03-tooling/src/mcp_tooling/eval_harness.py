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
    """The measured design qualities of one tool. score is the count of passed checks (0 to 5)."""

    namespaced: bool
    described: bool
    clear_params: bool
    paginated: bool
    concise_response: bool

    @property
    def score(self) -> int:
        return sum(
            [self.namespaced, self.described, self.clear_params, self.paginated, self.concise_response]
        )


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

        # Only the response-size metric needs a call, and it is only callable with {} when nothing is
        # required. A required-param tool is not penalized for being uncallable here (required params
        # are good design); its conciseness is simply unmeasured.
        if required:
            _log.info(
                "eval: %s has required params %s; skipping the response-size probe",
                tool.name,
                sorted(required),
            )
            concise_response = True
        else:
            result = await client.call_tool(tool.name, {})
            concise_response = _estimate_tokens(_response_text(result)) <= _TOKEN_BUDGET

        scores[tool.name] = Scorecard(
            namespaced=namespaced,
            described=described,
            clear_params=clear_params,
            paginated=paginated,
            concise_response=concise_response,
        )
    return scores
