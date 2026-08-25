from __future__ import annotations

from typing import Any

STRUCTURAL_FIELDS = (
    "path_with_namespace",
    "default_branch",
    "visibility",
    "archived",
    "description",
    "topics",
)


def _index(snapshot: dict[str, Any]) -> dict[Any, dict[str, Any]]:
    return {project.get("id"): project for project in snapshot.get("projects", []) if project.get("id") is not None}


def compare_snapshots(previous: dict[str, Any] | None, current: dict[str, Any]) -> dict[str, Any]:
    if not previous:
        return {
            "schema_version": "1",
            "baseline": "none",
            "previous_generated_at": None,
            "current_generated_at": current.get("generated_at"),
            "summary": {"added": 0, "removed": 0, "changed": 0, "activity_advanced": 0},
            "added": [],
            "removed": [],
            "changed": [],
            "activity_advanced": [],
        }

    before = _index(previous)
    after = _index(current)
    added_ids = sorted(set(after) - set(before))
    removed_ids = sorted(set(before) - set(after))
    shared_ids = sorted(set(before) & set(after))

    added = [after[project_id] for project_id in added_ids]
    removed = [before[project_id] for project_id in removed_ids]
    changed: list[dict[str, Any]] = []
    activity_advanced: list[dict[str, Any]] = []

    for project_id in shared_ids:
        old = before[project_id]
        new = after[project_id]
        fields: dict[str, dict[str, Any]] = {}
        for field in STRUCTURAL_FIELDS:
            if old.get(field) != new.get(field):
                fields[field] = {"before": old.get(field), "after": new.get(field)}
        if fields:
            changed.append({
                "id": project_id,
                "path_with_namespace": new.get("path_with_namespace") or old.get("path_with_namespace"),
                "fields": fields,
            })
        if old.get("last_activity_at") != new.get("last_activity_at"):
            activity_advanced.append({
                "id": project_id,
                "path_with_namespace": new.get("path_with_namespace") or old.get("path_with_namespace"),
                "before": old.get("last_activity_at"),
                "after": new.get("last_activity_at"),
            })

    return {
        "schema_version": "1",
        "baseline": "previous-snapshot",
        "previous_generated_at": previous.get("generated_at"),
        "current_generated_at": current.get("generated_at"),
        "summary": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
            "activity_advanced": len(activity_advanced),
        },
        "added": added,
        "removed": removed,
        "changed": changed,
        "activity_advanced": activity_advanced,
    }
