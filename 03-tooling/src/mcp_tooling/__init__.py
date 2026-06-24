# ABOUTME: Public API for the tooling track: a good/anti-pattern tool pair and a deterministic eval.
# ABOUTME: The eval harness scores tool-design quality offline, with no LLM or network calls.
from mcp_tooling.annotations import build_annotations_server
from mcp_tooling.contacts import build_contacts_server
from mcp_tooling.eval_harness import Scorecard, evaluate_server

__all__ = [
    "Scorecard",
    "build_annotations_server",
    "build_contacts_server",
    "evaluate_server",
]
