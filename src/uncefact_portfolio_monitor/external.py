from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

ALLOWED_TYPES = {
    "technical-resolution-dependency",
    "trust-model-dependency",
    "protocol-alignment",
    "semantic-dependency",
    "normative-dependency",
}


def validate_external_dependencies(snapshot: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    projects = {item.get("path_with_namespace") for item in snapshot.get("projects", [])}
    dependencies = config.get("dependencies", [])
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, dep in enumerate(dependencies, start=1):
        dep_id = dep.get("id")
        dep_type = dep.get("type")
        url = dep.get("url", "")
        affected = dep.get("affected_projects", [])
        if not dep_id or dep_id in seen:
            errors.append(f"dependency {index}: missing or duplicate id {dep_id!r}")
        else:
            seen.add(dep_id)
        if dep_type not in ALLOWED_TYPES:
            errors.append(f"dependency {index}: unsupported type {dep_type!r}")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            errors.append(f"dependency {index}: invalid URL {url!r}")
        if not affected:
            errors.append(f"dependency {index}: affected_projects must not be empty")
        unknown = sorted(project for project in affected if project not in projects)
        if unknown:
            errors.append(f"dependency {index}: unknown affected projects {unknown!r}")
        normalized.append({
            "id": dep_id,
            "name": dep.get("name", dep_id),
            "url": url,
            "type": dep_type,
            "affected_projects": sorted(affected),
            "note": dep.get("note", ""),
            "provenance": "declared-external-dependency",
        })

    if errors:
        raise ValueError("; ".join(errors))

    normalized.sort(key=lambda item: item["id"])
    return {
        "schema_version": str(config.get("schema_version", "1")),
        "generated_from": snapshot.get("generated_at"),
        "provenance": "declared-external-dependency-configuration",
        "dependency_count": len(normalized),
        "dependencies": normalized,
        "assurance_boundary": "External dependency declarations identify review context; they do not assert current external change, incompatibility, or assurance failure.",
    }
