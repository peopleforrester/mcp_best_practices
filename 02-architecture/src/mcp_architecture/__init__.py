# ABOUTME: Public API for the architecture track: handle pattern, composition, registry validation.
# ABOUTME: Builders return FastMCP servers; validate_server_json checks a registry entry offline.
from mcp_architecture.composition import build_composite_server, build_math_server
from mcp_architecture.handles import build_basket_server
from mcp_architecture.registry import validate_server_json

__all__ = [
    "build_basket_server",
    "build_composite_server",
    "build_math_server",
    "validate_server_json",
]
