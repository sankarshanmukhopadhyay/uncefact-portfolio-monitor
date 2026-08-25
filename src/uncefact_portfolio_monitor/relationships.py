from __future__ import annotations

from typing import Any

ALLOWED_TYPES = {
    "depends-on",
    "profile-of",
    "semantic-dependency",
    "trust-infrastructure-dependency",
    "related-to",
}


def validate_relationships(snapshot: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    projects = {item.get("path_with_namespace") for item in snapshot.get("projects", [])}
    relationships = config.get("relationships", [])
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, rel in enumerate(relationships, start=1):
        source = rel.get("from")
        target = rel.get("to")
        kind = rel.get("type")
        if kind not in ALLOWED_TYPES:
            errors.append(f"relationship {index}: unsupported type {kind!r}")
        if source not in projects:
            errors.append(f"relationship {index}: unknown internal source {source!r}")
        if target not in projects:
            errors.append(f"relationship {index}: unknown internal target {target!r}")
        normalized.append({
            "from": source,
            "to": target,
            "type": kind,
            "note": rel.get("note", ""),
            "provenance": "declared",
        })

    if errors:
        raise ValueError("; ".join(errors))

    return {
        "schema_version": str(config.get("schema_version", "1")),
        "generated_from": snapshot.get("generated_at"),
        "provenance": "declared-portfolio-configuration",
        "relationship_count": len(normalized),
        "relationships": normalized,
    }


def mermaid_graph(data: dict[str, Any]) -> str:
    nodes: dict[str, str] = {}
    lines = ["graph LR"]
    for rel in data.get("relationships", []):
        for path in (rel["from"], rel["to"]):
            if path not in nodes:
                node_id = f"n{len(nodes) + 1}"
                nodes[path] = node_id
                lines.append(f'    {node_id}["{path.split("/")[-1]}"]')
        label = rel["type"].replace("-", " ")
        lines.append(f'    {nodes[rel["from"]]} -->|"{label}"| {nodes[rel["to"]]}')
    return "\n".join(lines) + "\n"
