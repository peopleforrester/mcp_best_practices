# ABOUTME: A matched tool pair on one domain: an anti-pattern tool and a well-designed one.
# ABOUTME: getData is the wrong way (vague, dumps everything); contacts_search is the right way.
from __future__ import annotations

from typing import Annotated, TypedDict

from fastmcp import FastMCP
from pydantic import Field

# Pagination bounds: limit at least 1 (limit 0 advances the offset by 0 forever), offset non-negative.
# A numeric offset, named honestly: MCP's wire pagination is an opaque string cursor, but a demo over
# an in-memory list paginates by offset, so the parameter is called "offset" rather than "cursor".
Limit = Annotated[int, Field(ge=1, le=100)]
Offset = Annotated[int, Field(ge=0)]

# A small directory. The anti-pattern tool returns all of it as a blob; the good tool searches it.
_CONTACTS = [
    {"id": f"c{i:03d}", "name": name, "email": f"{name.lower().replace(' ', '.')}@example.com",
     "team": team}
    for i, (name, team) in enumerate(
        [
            ("Ada Lovelace", "platform"), ("Alan Turing", "platform"), ("Grace Hopper", "compilers"),
            ("Katherine Johnson", "flight"), ("Dorothy Vaughan", "flight"), ("Mary Jackson", "flight"),
            ("Margaret Hamilton", "flight"), ("Barbara Liskov", "platform"), ("Radia Perlman", "network"),
            ("Frances Allen", "compilers"), ("Karen Sparck Jones", "search"), ("Shafi Goldwasser", "crypto"),
            ("Hedy Lamarr", "network"), ("Annie Easley", "flight"), ("Evelyn Boyd Granville", "flight"),
        ],
        start=1,
    )
]


class ContactView(TypedDict):
    """The structured, human-readable shape for one contact in search results."""

    name: str
    email: str
    team: str


class ContactSearchPage(TypedDict):
    """A page of contact search results with pagination metadata."""

    contacts: list[ContactView]
    total: int
    next_offset: int | None


def build_contacts_server() -> FastMCP:
    """Build a server exposing both the anti-pattern tool and the well-designed tool."""
    mcp = FastMCP("tooling-contacts")

    @mcp.tool
    def getData(x: str = "") -> str:
        """gets data"""
        # Anti-pattern: vague name and param, terse description, no pagination, dumps everything
        # as one opaque text blob that the model must parse, including raw internal ids.
        lines = [f"{c['id']}|{c['name']}|{c['email']}|{c['team']}" for c in _CONTACTS]
        return "\n".join(lines)

    @mcp.tool
    def contacts_search(
        query: str = "", team: str | None = None, limit: Limit = 5, offset: Offset = 0
    ) -> ContactSearchPage:
        """Search the team directory by name substring and optional team.

        Returns a small page of human-readable contacts (name, email, team) with a next_offset for
        pagination. Search-focused rather than returning the whole directory, and it omits internal ids.
        """
        matches: list[ContactView] = [
            {"name": c["name"], "email": c["email"], "team": c["team"]}
            for c in _CONTACTS
            if query.lower() in c["name"].lower() and (team is None or c["team"] == team)
        ]
        page = matches[offset : offset + limit]
        next_offset = offset + limit if offset + limit < len(matches) else None
        return {"contacts": page, "total": len(matches), "next_offset": next_offset}

    return mcp
