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


def render(data: dict) -> str:
    rows = []
    for item in data.get("findings", []):
        rows.append(
            "<tr>"
            f"<td><code>{escape(item['finding_id'])}</code></td>"
            f"<td>{escape(item['severity'])}</td>"
            f"<td><code>{escape(item['subject_project'])}</code></td>"
            f"<td><code>{escape(item['dependency_project'])}</code></td>"
            f"<td>{escape(item['relationship_type'])}</td>"
            f"<td>{escape(item['change_type'])}</td>"
            f"<td><code>{escape(item['policy_id'])}</code></td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="7">No policy-matched findings in this observation.</td></tr>')
    summary = data.get("summary", {})
    by_severity = summary.get("by_severity", {})
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Findings</title>
<style>body{{font:15px/1.55 system-ui,sans-serif;max-width:1250px;margin:auto;padding:36px 22px;color:#18202a}}a{{color:#155eef}}table{{width:100%;border-collapse:collapse;margin:24px 0}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd;vertical-align:top}}th{{font-size:12px;text-transform:uppercase}}code{{font-family:ui-monospace,SFMono-Regular,monospace}}.note{{border-left:3px solid #155eef;padding:10px 14px;background:#f5f7fa}}</style></head>
<body><p><a href="index.html">← Portfolio</a> · <a href="relationships.html">Relationships</a> · <a href="impacts.html">Impact review</a></p><h1>Evidence-backed portfolio findings</h1>
<p>Findings are deterministic matches between declared evidence policies and current review obligations. They require tracked disposition but are not automatically compatibility failures, assurance failures, or trust decisions.</p>
<div class="note">{summary.get('open_findings',0)} open finding(s): {by_severity.get('critical',0)} critical, {by_severity.get('high',0)} high, {by_severity.get('medium',0)} medium, {by_severity.get('low',0)} low. Machine-readable evidence: <a href="findings.json">findings.json</a>.</div>
<table><thead><tr><th>Finding</th><th>Severity</th><th>Review project</th><th>Changed dependency</th><th>Relationship</th><th>Change</th><th>Policy</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p><small>{escape(data.get('assurance_boundary',''))}</small></p>
</body></html>'''


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
