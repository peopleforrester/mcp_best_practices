# ABOUTME: A matched tool pair on one domain: an anti-pattern tool and a well-designed one.
# ABOUTME: getData is the wrong way (vague, dumps everything); contacts_search is the right way.
from __future__ import annotations

from typing import TypedDict

from fastmcp import FastMCP

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
    next_cursor: int | None


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
    def contacts_search(query: str = "", team: str | None = None, limit: int = 5, cursor: int = 0) -> ContactSearchPage:
        """Search the team directory by name substring and optional team.

        Returns a small page of human-readable contacts (name, email, team) with a next_cursor for
        pagination. Search-focused rather than returning the whole directory, and it omits internal ids.
        """
        matches = [
            {"name": c["name"], "email": c["email"], "team": c["team"]}
            for c in _CONTACTS
            if query.lower() in c["name"].lower() and (team is None or c["team"] == team)
        ]
        page = matches[cursor : cursor + limit]
        next_cursor = cursor + limit if cursor + limit < len(matches) else None
        return {"contacts": page, "total": len(matches), "next_cursor": next_cursor}

    return mcp
