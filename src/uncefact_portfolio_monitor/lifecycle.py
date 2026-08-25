from __future__ import annotations

from typing import Any


def update_lifecycle(current_findings: dict[str, Any], previous: dict[str, Any] | None) -> dict[str, Any]:
    observed_at = current_findings.get("generated_from", {}).get("observation") or current_findings.get("generated_at")
    prior_records = {r["finding_id"]: dict(r) for r in (previous or {}).get("records", []) if r.get("finding_id")}
    current = {f["finding_id"]: f for f in current_findings.get("findings", []) if f.get("finding_id")}
    records: list[dict[str, Any]] = []

    for finding_id, finding in current.items():
        prior = prior_records.get(finding_id)
        records.append({
            "finding_id": finding_id,
            "status": "active",
            "severity": finding.get("severity"),
            "policy_id": finding.get("policy_id"),
            "subject_project": finding.get("subject_project"),
            "dependency_project": finding.get("dependency_project"),
            "relationship_type": finding.get("relationship_type"),
            "change_type": finding.get("change_type"),
            "first_observed": (prior or {}).get("first_observed") or observed_at,
            "last_observed": observed_at,
            "observation_count": int((prior or {}).get("observation_count", 0)) + 1,
            "resolved_at": None,
            "evidence": finding,
        })

    for finding_id, prior in prior_records.items():
        if finding_id in current:
            continue
        prior["status"] = "resolved"
        prior["resolved_at"] = prior.get("resolved_at") or observed_at
        records.append(prior)

    records.sort(key=lambda r: (r["status"] != "active", r.get("severity") or "", r["finding_id"]))
    active = sum(1 for r in records if r["status"] == "active")
    resolved = sum(1 for r in records if r["status"] == "resolved")
    return {
        "schema_version": "1",
        "observed_at": observed_at,
        "summary": {"active": active, "resolved": resolved, "total_records": len(records)},
        "records": records,
        "assurance_boundary": "Lifecycle status records evidence persistence and disposition state; it does not turn a finding into a compatibility or trust conclusion.",
    }
