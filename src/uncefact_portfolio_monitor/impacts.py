from __future__ import annotations

from typing import Any

PROPAGATING_TYPES = {
    "depends-on",
    "profile-of",
    "semantic-dependency",
    "trust-infrastructure-dependency",
}


def _observed_structural_changes(changes: dict[str, Any]) -> list[dict[str, Any]]:
    observed: list[dict[str, Any]] = []
    for kind in ("added", "removed", "changed"):
        for item in changes.get(kind, []):
            path = item.get("path_with_namespace")
            if path:
                observed.append({"project": path, "change_type": kind, "evidence": item})
    return observed


def propagate_impacts(changes: dict[str, Any], relationships: dict[str, Any]) -> dict[str, Any]:
    observed = _observed_structural_changes(changes)
    rels = relationships.get("relationships", [])
    obligations: list[dict[str, Any]] = []
    informational: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()

    for change in observed:
        changed_project = change["project"]
        for rel in rels:
            kind = rel.get("type")
            source = rel.get("from")
            target = rel.get("to")
            if kind in PROPAGATING_TYPES and target == changed_project:
                key = (source, target, kind, change["change_type"])
                if key not in seen:
                    seen.add(key)
                    obligations.append({
                        "review_project": source,
                        "changed_project": target,
                        "relationship_type": kind,
                        "change_type": change["change_type"],
                        "reason": "observed structural change in declared dependency",
                        "change_evidence": change["evidence"],
                        "relationship_provenance": rel.get("provenance", "declared"),
                    })
            elif kind == "related-to" and changed_project in {source, target}:
                peer = target if changed_project == source else source
                informational.append({
                    "project": peer,
                    "changed_project": changed_project,
                    "relationship_type": kind,
                    "change_type": change["change_type"],
                    "reason": "related project changed; no dependency is asserted",
                })

    for item in changes.get("activity_advanced", []):
        path = item.get("path_with_namespace")
        if path:
            informational.append({
                "project": path,
                "changed_project": path,
                "relationship_type": None,
                "change_type": "activity_advanced",
                "reason": "repository activity advanced without observed structural metadata change",
            })

    obligations.sort(key=lambda x: (x["review_project"] or "", x["changed_project"] or "", x["relationship_type"] or ""))
    informational.sort(key=lambda x: (x["project"] or "", x["changed_project"] or "", x["change_type"] or ""))
    return {
        "schema_version": "1",
        "generated_from": {
            "changes_current_generated_at": changes.get("current_generated_at"),
            "relationships_generated_from": relationships.get("generated_from"),
        },
        "provenance": "derived-from-observed-change-and-declared-relationships",
        "summary": {
            "review_obligations": len(obligations),
            "informational": len(informational),
        },
        "review_obligations": obligations,
        "informational": informational,
        "assurance_boundary": "Review obligations are impact candidates, not assurance failures or trust conclusions.",
    }
