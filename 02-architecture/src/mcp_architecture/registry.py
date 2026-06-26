# ABOUTME: Offline validator for an MCP Registry server.json entry (a pragmatic subset of the schema).
# ABOUTME: Lets CI keep a published entry well-formed without contacting the preview registry service.
from __future__ import annotations


def validate_server_json(data: dict) -> list[str]:
    """Validate a registry server.json entry, returning a list of error strings (empty if valid).

    Checks the load-bearing fields: a namespaced name, a description, a version, and at least one
    install target (packages or remotes). This is a pragmatic subset of the official schema, enough
    to catch the mistakes that make an entry uninstallable. The registry itself is preview (API v0.1).
    """
    errors: list[str] = []

    name = data.get("name")
    if not name or not isinstance(name, str):
        errors.append("name is required and must be a string")
    elif "/" not in name:
        errors.append("name should be namespaced (reverse-DNS namespace and a slash, e.g. io.example/server)")

    if not data.get("description"):
        errors.append("description is required")

    if not data.get("version"):
        errors.append("version is required")

    has_packages = isinstance(data.get("packages"), list) and len(data["packages"]) > 0
    has_remotes = isinstance(data.get("remotes"), list) and len(data["remotes"]) > 0
    if not (has_packages or has_remotes):
        errors.append("at least one install target is required: packages or remotes")

    # A non-empty list is not enough: each entry must carry the fields that make it installable, or the
    # entry is uninstallable despite passing the presence check above.
    if isinstance(data.get("packages"), list):
        for i, pkg in enumerate(data["packages"]):
            if not isinstance(pkg, dict):
                errors.append(f"packages[{i}] must be an object")
                continue
            for field in ("identifier", "registryType", "transport"):
                if not pkg.get(field):
                    errors.append(f"packages[{i}] is missing required field {field!r}")

    if isinstance(data.get("remotes"), list):
        for i, remote in enumerate(data["remotes"]):
            if not isinstance(remote, dict) or not remote.get("type") or not remote.get("url"):
                errors.append(f"remotes[{i}] must have a type and a url")

    return errors
