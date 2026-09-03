#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.findings import derive_findings


def _finding_card(item: dict) -> str:
    severity = escape(str(item.get("severity") or "unknown")).upper()
    title = escape(str(item.get("title") or "Finding"))
    finding_id = escape(str(item.get("finding_id") or ""))
    status = escape(str(item.get("status") or "open")).upper()
    subject = escape(str(item.get("subject_project") or "unknown"))
    dependency = escape(str(item.get("dependency_project") or "unknown"))
    relationship = escape(str(item.get("relationship_type") or "unknown"))
    change = escape(str(item.get("change_type") or "unknown"))
    policy = escape(str(item.get("policy_id") or "unknown"))
    reason = escape(str(item.get("reason") or "Review required by declared evidence policy."))
    evidence = item.get("evidence") or {}
    impact_ref = escape(str(evidence.get("impact_ref") or ""), quote=True)
    change_evidence = escape(str(evidence.get("change_evidence") or ""))
    relationship_provenance = escape(str(evidence.get("relationship_provenance") or ""))
    policy_provenance = escape(str(evidence.get("policy_provenance") or ""))

    plain = (
        f"{subject} depends on {dependency} through the declared {relationship} relationship. "
        f"The dependency recorded a {change} structural change in the current observation, so the dependent project requires tracked review."
    )

    evidence_bits = []
    if impact_ref:
        evidence_bits.append(f'<a href="{impact_ref}">Review obligation</a>')
    if change_evidence:
        evidence_bits.append(f"Change evidence: <code>{change_evidence}</code>")
    if relationship_provenance:
        evidence_bits.append(f"Relationship provenance: <code>{relationship_provenance}</code>")
    if policy_provenance:
        evidence_bits.append(f"Policy provenance: <code>{policy_provenance}</code>")

    return f'''<article class="finding" id="{finding_id}">
<div class="finding-head"><div><span class="severity">{severity}</span><h2>{title}</h2></div><span class="status">{status}</span></div>
<p class="interpretation">{plain}</p>
<p class="reason"><strong>Why this was flagged:</strong> {reason}</p>
<dl><div><dt>Review project</dt><dd><code>{subject}</code></dd></div><div><dt>Changed dependency</dt><dd><code>{dependency}</code></dd></div><div><dt>Relationship</dt><dd>{relationship}</dd></div><div><dt>Change</dt><dd>{change}</dd></div><div><dt>Policy</dt><dd><code>{policy}</code></dd></div></dl>
<p class="evidence"><strong>Evidence:</strong> {' · '.join(evidence_bits) if evidence_bits else 'See machine-readable finding evidence.'}</p>
<p class="finding-id"><strong>Stable finding ID:</strong> <code>{finding_id}</code></p>
</article>'''


def render(data: dict) -> str:
    findings = data.get("findings", [])
    cards = "".join(_finding_card(item) for item in findings)
    if not cards:
        cards = '<div class="empty">No policy-matched findings in this observation.</div>'
    summary = data.get("summary", {})
    by_severity = summary.get("by_severity", {})
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Findings</title>
<style>:root{{--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1180px;margin:auto;padding:36px 22px 72px}}a{{color:var(--accent)}}.nav{{margin-bottom:24px}}.note,.finding{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:18px 0}}.note{{border-left:3px solid var(--accent)}}.finding-head{{display:flex;justify-content:space-between;gap:16px;align-items:flex-start}}h2{{margin:4px 0 0;font-size:21px}}.severity,.status{{font-size:12px;font-weight:700;letter-spacing:.05em}}.severity{{color:#9a3412}}.status{{background:#eef2ff;border-radius:999px;padding:4px 8px}}.interpretation{{font-size:16px}}.reason{{background:#f8fafc;padding:10px 12px;border-radius:8px}}dl{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin:16px 0}}dl div{{border-top:1px solid var(--line);padding-top:8px}}dt{{font-size:12px;text-transform:uppercase;color:var(--muted)}}dd{{margin:3px 0 0}}code{{font-family:ui-monospace,SFMono-Regular,monospace}}.evidence,.finding-id{{color:var(--muted)}}.finding-id{{font-size:13px}}.empty{{padding:20px;background:var(--panel);border:1px solid var(--line);border-radius:12px}}</style></head>
<body><main><p class="nav"><a href="index.html">← Portfolio</a> · <a href="relationships.html">Relationships</a> · <a href="impacts.html">Impact review</a> · <a href="changes.html">Changes</a></p><h1>Evidence-backed portfolio findings</h1>
<p>Each finding is presented first as a human-readable review condition. The alphanumeric finding ID is retained as stable secondary metadata for machine processing, cross-reference, and lifecycle tracking.</p>
<div class="note"><strong>{summary.get('open_findings',0)} open finding(s)</strong>: {by_severity.get('critical',0)} critical, {by_severity.get('high',0)} high, {by_severity.get('medium',0)} medium, {by_severity.get('low',0)} low. Machine-readable evidence: <a href="findings.json">findings.json</a>.</div>
{cards}
<p><small>{escape(data.get('assurance_boundary',''))}</small></p>
</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive findings from review obligations and declared evidence policies")
    parser.add_argument("--impacts", type=Path, default=ROOT / "site" / "impacts.json")
    parser.add_argument("--policies", type=Path, default=ROOT / "config" / "finding-policies.toml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    impacts = json.loads(args.impacts.read_text(encoding="utf-8"))
    policies = tomllib.loads(args.policies.read_text(encoding="utf-8"))
    data = derive_findings(impacts, policies)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "findings.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "findings.html").write_text(render(data), encoding="utf-8")
    print(f"published {data['summary']['open_findings']} policy-matched findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
