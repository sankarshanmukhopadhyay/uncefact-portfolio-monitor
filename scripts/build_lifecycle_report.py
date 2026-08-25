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
    return "\n".join(f"- **{r.get('severity','unknown').upper()}** `{r['finding_id']}` — `{r.get('subject_project')}` reviewing `{r.get('dependency_project')}` ({r.get('relationship_type')}, {r.get('change_type')}); observed {r.get('observation_count',1)} time(s)." for r in records)


def html_report(markdown: str, lifecycle: dict) -> str:
    lines = "".join(f"<p>{escape(line)}</p>" if line and not line.startswith('#') and not line.startswith('- ') else (f"<h2>{escape(line[3:])}</h2>" if line.startswith('## ') else (f"<h1>{escape(line[2:])}</h1>" if line.startswith('# ') else (f"<li>{escape(line[2:])}</li>" if line.startswith('- ') else ""))) for line in markdown.splitlines())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>UN/CEFACT Portfolio Assurance Report</title><style>body{{font:15px/1.6 system-ui,sans-serif;max-width:1000px;margin:auto;padding:36px 22px;color:#18202a}}a{{color:#155eef}}code{{font-family:ui-monospace,SFMono-Regular,monospace}}.note{{border-left:3px solid #155eef;padding:10px 14px;background:#f5f7fa}}</style></head><body><p><a href="index.html">← Portfolio</a> · <a href="findings.html">Current findings</a> · <a href="external-dependencies.html">External dependencies</a></p><div class="note">Machine-readable lifecycle: <a href="findings-lifecycle.json">findings-lifecycle.json</a> · Markdown report: <a href="weekly-report.md">weekly-report.md</a></div>{lines}<p><small>{escape(lifecycle.get('assurance_boundary',''))}</small></p></body></html>'''


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
    (args.output_dir / "findings-lifecycle.json").write_text(json.dumps(lifecycle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "weekly-report.md").write_text(md, encoding="utf-8")
    (args.output_dir / "weekly-report.html").write_text(html_report(md, lifecycle), encoding="utf-8")
    print(f"lifecycle: {lifecycle['summary']['active']} active, {lifecycle['summary']['resolved']} resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
