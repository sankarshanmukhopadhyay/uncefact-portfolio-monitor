#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.lifecycle import update_lifecycle


def _read(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def markdown_report(portfolio: dict, changes: dict, impacts: dict, lifecycle: dict, external: dict) -> str:
    s = lifecycle.get("summary", {})
    c = changes.get("summary", {})
    return f"""# UN/CEFACT Portfolio Assurance Report

Observation: {portfolio.get('generated_at','unknown')}

## Portfolio summary

- Discovered projects: {portfolio.get('project_count', len(portfolio.get('projects', [])))}
- Structural changes: {int(c.get('added',0))+int(c.get('removed',0))+int(c.get('changed',0))}
- Activity-only advancements: {c.get('activity_advanced',0)}
- Direct review obligations: {impacts.get('summary',{}).get('review_obligations',0)}
- Active findings: {s.get('active',0)}
- Resolved findings retained: {s.get('resolved',0)}
- Declared external dependencies: {external.get('dependency_count',0)}

## Active findings

{_finding_lines(lifecycle, 'active')}

## Resolved findings retained

{_finding_lines(lifecycle, 'resolved')}

## Interpretation boundary

This report is generated from observable repository evidence, declared relationships, declared evidence policies, and declared external dependency context. Findings require tracked disposition but are not automatically compatibility failures, assurance failures, or trust decisions.
"""


def _finding_lines(lifecycle: dict, status: str) -> str:
    records = [r for r in lifecycle.get("records", []) if r.get("status") == status]
    if not records:
        return "_None in this observation._"
    return "\n".join(
        f"- **{r.get('severity','unknown').upper()}** `{r['finding_id']}` — "
        f"`{r.get('subject_project')}` reviewing `{r.get('dependency_project')}` "
        f"({r.get('relationship_type')}, {r.get('change_type')}); observed "
        f"{r.get('observation_count',1)} time(s)."
        for r in records
    )


def _finding_rows(lifecycle: dict, status: str) -> str:
    records = [r for r in lifecycle.get("records", []) if r.get("status") == status]
    if not records:
        return '<tr><td colspan="7" class="empty">None in this observation.</td></tr>'

    rows: list[str] = []
    for record in records:
        rows.append(
            "<tr>"
            f"<td><strong>{escape(str(record.get('severity') or 'unknown').upper())}</strong></td>"
            f"<td><code>{escape(str(record.get('finding_id') or 'unknown'))}</code></td>"
            f"<td><code>{escape(str(record.get('subject_project') or 'unknown'))}</code></td>"
            f"<td><code>{escape(str(record.get('dependency_project') or 'unknown'))}</code></td>"
            f"<td>{escape(str(record.get('relationship_type') or 'unknown'))}</td>"
            f"<td>{escape(str(record.get('change_type') or 'unknown'))}</td>"
            f"<td>{escape(str(record.get('observation_count', 1)))}</td>"
            "</tr>"
        )
    return "".join(rows)


def html_report(portfolio: dict, changes: dict, impacts: dict, lifecycle: dict, external: dict) -> str:
    summary = lifecycle.get("summary", {})
    change_summary = changes.get("summary", {})
    structural = (
        int(change_summary.get("added", 0))
        + int(change_summary.get("removed", 0))
        + int(change_summary.get("changed", 0))
    )
    project_count = portfolio.get("project_count", len(portfolio.get("projects", [])))
    activity = change_summary.get("activity_advanced", 0)
    obligations = impacts.get("summary", {}).get("review_obligations", 0)
    active = summary.get("active", 0)
    resolved = summary.get("resolved", 0)
    external_count = external.get("dependency_count", 0)
    observation = portfolio.get("generated_at", "unknown")
    assurance_boundary = lifecycle.get("assurance_boundary", "")

    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Assurance Report</title><style>
:root{{--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1200px;margin:auto;padding:36px 22px 72px}}a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}h1{{margin:0 0 8px}}h2{{margin-top:32px}}.lede,.empty,.meta{{color:var(--muted)}}.note{{border-left:3px solid var(--accent);padding:11px 14px;background:var(--panel);margin:20px 0}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0 28px}}.stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}}.stat strong{{display:block;font-size:24px}}.stat small{{display:block;color:var(--muted);margin-top:3px}}.table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:16px 0 28px}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}tr:last-child td{{border-bottom:0}}code{{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12px}}
</style></head><body><main>
<p><a href="index.html">← Portfolio</a> · <a href="findings.html">Current findings</a> · <a href="external-dependencies.html">External dependencies</a></p>
<h1>UN/CEFACT Portfolio Assurance Report</h1>
<p class="lede">Lifecycle-aware weekly view of observable portfolio evidence. This page is optimized for rapid inspection; the underlying evidence contracts and governance meaning are unchanged.</p>
<div class="note"><strong>Observation:</strong> {escape(str(observation))}. Machine-readable lifecycle: <a href="findings-lifecycle.json">findings-lifecycle.json</a> · Markdown report: <a href="weekly-report.md">weekly-report.md</a>.</div>
<div class="stats">
<div class="stat"><span>Projects</span><strong>{escape(str(project_count))}</strong><small>Discovered</small></div>
<div class="stat"><span>Structural changes</span><strong>{escape(str(structural))}</strong><small>Current observation</small></div>
<div class="stat"><span>Activity advanced</span><strong>{escape(str(activity))}</strong><small>Activity-only</small></div>
<div class="stat"><span>Review obligations</span><strong>{escape(str(obligations))}</strong><small>Direct</small></div>
<div class="stat"><span>Active findings</span><strong>{escape(str(active))}</strong><small>Require disposition</small></div>
<div class="stat"><span>Resolved retained</span><strong>{escape(str(resolved))}</strong><small>Lifecycle evidence</small></div>
<div class="stat"><span>External dependencies</span><strong>{escape(str(external_count))}</strong><small>Declared context</small></div>
</div>
<h2>Active findings</h2>
<p class="lede">Current policy-matched evidence conditions requiring tracked disposition.</p>
<div class="table-wrap"><table><thead><tr><th>Severity</th><th>Finding</th><th>Reviewing project</th><th>Dependency</th><th>Relationship</th><th>Change</th><th>Observations</th></tr></thead><tbody>{_finding_rows(lifecycle, 'active')}</tbody></table></div>
<h2>Resolved findings retained</h2>
<p class="lede">Previously observed findings no longer active in the current observation, retained as lifecycle evidence.</p>
<div class="table-wrap"><table><thead><tr><th>Severity</th><th>Finding</th><th>Reviewing project</th><th>Dependency</th><th>Relationship</th><th>Change</th><th>Observations</th></tr></thead><tbody>{_finding_rows(lifecycle, 'resolved')}</tbody></table></div>
<h2>Interpretation boundary</h2>
<div class="note">This report is generated from observable repository evidence, declared relationships, declared evidence policies, and declared external dependency context. Findings require tracked disposition but are not automatically compatibility failures, assurance failures, or trust decisions.</div>
<p class="meta">{escape(str(assurance_boundary))}</p>
</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--findings", type=Path, default=ROOT / "site" / "findings.json")
    parser.add_argument("--previous", type=Path, default=ROOT / ".state" / "findings-lifecycle.json")
    parser.add_argument("--portfolio", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--changes", type=Path, default=ROOT / "reports" / "latest" / "changes.json")
    parser.add_argument("--impacts", type=Path, default=ROOT / "site" / "impacts.json")
    parser.add_argument("--external", type=Path, default=ROOT / "site" / "external-dependencies.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    current = _read(args.findings, {"findings": []})
    previous = _read(args.previous, {})
    lifecycle = update_lifecycle(current, previous)
    portfolio = _read(args.portfolio, {})
    changes = _read(args.changes, {"summary": {}})
    impacts = _read(args.impacts, {"summary": {}})
    external = _read(args.external, {"dependency_count": 0})
    md = markdown_report(portfolio, changes, impacts, lifecycle, external)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "findings-lifecycle.json").write_text(
        json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "weekly-report.md").write_text(md, encoding="utf-8")
    (args.output_dir / "weekly-report.html").write_text(
        html_report(portfolio, changes, impacts, lifecycle, external), encoding="utf-8"
    )
    print(f"lifecycle: {lifecycle['summary']['active']} active, {lifecycle['summary']['resolved']} resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
