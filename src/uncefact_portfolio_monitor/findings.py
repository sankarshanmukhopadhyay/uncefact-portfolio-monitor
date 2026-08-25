from __future__ import annotations

from hashlib import sha256
from typing import Any

ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}


def validate_policies(config: dict[str, Any]) -> list[dict[str, Any]]:
    policies = config.get("policies", [])
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, policy in enumerate(policies, start=1):
        policy_id = str(policy.get("id") or "").strip()
        severity = str(policy.get("severity") or "").strip()
        relationship_types = list(policy.get("relationship_types") or [])
        change_types = list(policy.get("change_types") or [])
        if not policy_id:
            errors.append(f"policy {index}: id is required")
        elif policy_id in seen:
            errors.append(f"policy {index}: duplicate id {policy_id!r}")
        else:
            seen.add(policy_id)
        if severity not in ALLOWED_SEVERITIES:
            errors.append(f"policy {index}: unsupported severity {severity!r}")
        if not relationship_types:
            errors.append(f"policy {index}: relationship_types is required")
        if not change_types:
            errors.append(f"policy {index}: change_types is required")
        normalized.append({
            "id": policy_id,
            "title": str(policy.get("title") or policy_id),
            "severity": severity,
            "relationship_types": relationship_types,
            "change_types": change_types,
            "description": str(policy.get("description") or ""),
            "provenance": "declared-policy",
        })

    if errors:
        raise ValueError("; ".join(errors))
    return normalized


def _finding_id(policy_id: str, obligation: dict[str, Any]) -> str:
    material = "|".join([
        policy_id,
        str(obligation.get("review_project") or ""),
        str(obligation.get("changed_project") or ""),
        str(obligation.get("relationship_type") or ""),
        str(obligation.get("change_type") or ""),
    ])
    digest = sha256(material.encode("utf-8")).hexdigest()[:12].upper()
    return f"{policy_id}-{digest}"


def derive_findings(impacts: dict[str, Any], policy_config: dict[str, Any]) -> dict[str, Any]:
    policies = validate_policies(policy_config)
    observed_at = impacts.get("generated_from", {}).get("changes_current_generated_at")
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    for impact_index, obligation in enumerate(impacts.get("review_obligations", [])):
        for policy in policies:
            if obligation.get("relationship_type") not in policy["relationship_types"]:
                continue
            if obligation.get("change_type") not in policy["change_types"]:
                continue
            finding_id = _finding_id(policy["id"], obligation)
            if finding_id in seen:
                continue
            seen.add(finding_id)
            findings.append({
                "finding_id": finding_id,
                "status": "open",
                "severity": policy["severity"],
                "title": policy["title"],
                "policy_id": policy["id"],
                "subject_project": obligation.get("review_project"),
                "dependency_project": obligation.get("changed_project"),
                "relationship_type": obligation.get("relationship_type"),
                "change_type": obligation.get("change_type"),
                "reason": policy["description"],
                "first_observed": observed_at,
                "last_observed": observed_at,
                "evidence": {
                    "impact_ref": f"impacts.json#/review_obligations/{impact_index}",
                    "change_evidence": obligation.get("change_evidence"),
                    "relationship_provenance": obligation.get("relationship_provenance"),
                    "policy_provenance": policy["provenance"],
                },
                "provenance": "derived-from-review-obligation-and-declared-policy",
            })

    findings.sort(key=lambda item: (item["severity"], item["finding_id"]))
    by_severity = {severity: 0 for severity in ("critical", "high", "medium", "low")}
    for finding in findings:
        by_severity[finding["severity"]] += 1

    return {
        "schema_version": "1",
        "generated_from": {
            "impacts": impacts.get("generated_from"),
            "policy_schema_version": str(policy_config.get("schema_version", "1")),
        },
        "provenance": "deterministic-policy-evaluation",
        "summary": {
            "open_findings": len(findings),
            "by_severity": by_severity,
        },
        "findings": findings,
        "assurance_boundary": "A finding is a policy-matched evidence condition requiring tracked disposition; it is not by itself a trust decision or proof of incompatibility.",
    }
