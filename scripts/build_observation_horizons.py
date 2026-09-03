#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _parse_time(value: str) -> datetime:
    if not value:
        raise ValueError("observation timestamp is required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _fmt(value: str) -> str:
    return _parse_time(value).strftime("%Y-%m-%d %H:%M UTC")


def _read(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _project_record(project: dict) -> dict:
    return {
        "name": project.get("name") or "Unnamed",
        "path_with_namespace": project.get("path_with_namespace") or "unknown",
        "web_url": project.get("web_url") or "",
        "last_activity_at": project.get("last_activity_at"),
    }


def build_horizons(snapshot: dict) -> dict:
    observed_at = _parse_time(snapshot.get("generated_at") or "")
    month_start = observed_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    trailing_start = observed_at - timedelta(days=90)
    projects = snapshot.get("projects", [])

    def collect(start: datetime) -> list[dict]:
        result: list[tuple[datetime, dict]] = []
        for project in projects:
            value = project.get("last_activity_at")
            if not value:
                continue
            try:
                activity = _parse_time(value)
            except ValueError:
                continue
            if start <= activity <= observed_at:
                result.append((activity, _project_record(project)))
        result.sort(key=lambda item: item[0], reverse=True)
        return [item[1] for item in result]

    month_projects = collect(month_start)
    trailing_projects = collect(trailing_start)
    total = len(projects)

    def horizon(identifier: str, label: str, start: datetime, entries: list[dict]) -> dict:
        return {
            "id": identifier,
            "label": label,
            "start": start.isoformat().replace("+00:00", "Z"),
            "end": observed_at.isoformat().replace("+00:00", "Z"),
            "project_count": len(entries),
            "portfolio_project_count": total,
            "portfolio_share": round((len(entries) / total), 4) if total else 0.0,
            "projects": entries,
        }

    return {
        "schema_version": "1",
        "generated_at": snapshot.get("generated_at"),
        "basis": "project.last_activity_at",
        "interpretation": (
            "Observation horizons report projects whose recorded last_activity_at falls within the horizon. "
            "They are portfolio activity evidence, not counts of normative changes, structural changes, assurance failures, or trust decisions."
        ),
        "horizons": [
            horizon("month-to-observed-date", "Month to observed date", month_start, month_projects),
            horizon("trailing-90-days", "Trailing 90 days", trailing_start, trailing_projects),
        ],
    }


def build_evidence_index(changes: dict, impacts: dict, findings: dict) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}

    def mark(project: str | None, evidence: str) -> None:
        if project:
            index.setdefault(project, set()).add(evidence)

    for kind in ("added", "removed", "changed", "activity_advanced"):
        for item in changes.get(kind, []):
            mark(item.get("path_with_namespace"), "changes")

    for item in impacts.get("review_obligations", []):
        mark(item.get("review_project"), "impacts")
        mark(item.get("changed_project"), "impacts")

    for item in findings.get("findings", []):
        mark(item.get("subject_project"), "findings")
        mark(item.get("dependency_project"), "findings")

    return index


def _evidence_links(path: str, evidence_index: dict[str, set[str]]) -> str:
    evidence = evidence_index.get(path, set())
    links = []
    for key, href, label in (
        ("changes", "changes.html", "Changes"),
        ("impacts", "impacts.html", "Impact review"),
        ("findings", "findings.html", "Findings"),
    ):
        if key in evidence:
            links.append(f'<a class="evidence-link" href="{href}">{label}</a>')
    return " ".join(links) or '<span class="empty">No current-window evidence link</span>'


def _project_rows(horizon: dict, evidence_index: dict[str, set[str]]) -> str:
    rows = []
    for project in horizon.get("projects", []):
        name = escape(project.get("name") or "Unnamed")
        path_raw = project.get("path_with_namespace") or "unknown"
        path = escape(path_raw)
        url = escape(project.get("web_url") or "#", quote=True)
        activity = project.get("last_activity_at")
        rendered_activity = escape(_fmt(activity)) if activity else "Unknown"
        rows.append(
            f'<tr><td><a href="{url}">{name}</a><div class="path">{path}</div></td>'
            f'<td>{rendered_activity}</td><td>{_evidence_links(path_raw, evidence_index)}</td></tr>'
        )
    return "".join(rows) or '<tr><td colspan="3" class="empty">No project activity observed in this horizon.</td></tr>'


def render_horizons(data: dict, evidence_index: dict[str, set[str]] | None = None) -> str:
    evidence_index = evidence_index or {}
    sections = []
    for horizon in data.get("horizons", []):
        share = float(horizon.get("portfolio_share", 0)) * 100
        horizon_id = escape(horizon.get("id") or "horizon", quote=True)
        sections.append(
            f'''<section class="horizon" id="{horizon_id}"><div class="horizon-head"><div><h2>{escape(horizon.get('label') or '')}</h2>
<p class="lede"><strong>{escape(_fmt(horizon.get('start')))} → {escape(_fmt(horizon.get('end')))}</strong></p></div>
<a class="metric" href="#{horizon_id}-projects"><strong>{int(horizon.get('project_count', 0))}</strong><span>of {int(horizon.get('portfolio_project_count', 0))} projects ({share:.0f}%)</span><small>View observed projects ↓</small></a></div>
<div class="table-wrap" id="{horizon_id}-projects"><table><thead><tr><th>Project</th><th>Last recorded activity</th><th>Current-window evidence</th></tr></thead><tbody>{_project_rows(horizon, evidence_index)}</tbody></table></div></section>'''
        )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Observation Horizons</title><style>
:root{{--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1180px;margin:auto;padding:36px 22px 72px}}a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}h1{{margin-bottom:8px}}h2{{margin:0 0 4px}}.lede,.empty{{color:var(--muted)}}.nav{{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 24px}}.nav a,.evidence-link{{display:inline-block;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:6px 9px}}.note{{border-left:3px solid var(--accent);padding:12px 14px;background:var(--panel);margin:20px 0 28px}}.horizon{{margin:28px 0 40px;scroll-margin-top:16px}}.horizon-head{{display:flex;gap:18px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}}.metric{{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;min-width:210px;color:var(--text)}}.metric:hover{{border-color:var(--accent);text-decoration:none}}.metric strong,.metric span,.metric small{{display:block}}.metric strong{{font-size:28px}}.metric span,.metric small{{color:var(--muted)}}.table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;margin-top:14px;scroll-margin-top:16px}}table{{width:100%;border-collapse:collapse;min-width:820px}}th,td{{text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}tr:last-child td{{border-bottom:0}}.path{{font-size:12px;color:var(--muted);margin-top:3px}}.evidence-link{{margin:0 5px 5px 0;padding:4px 7px;font-size:13px}}
</style></head><body><main>
<nav class="nav" aria-label="Evidence navigation"><a href="index.html">Portfolio</a><a href="changes.html">Changes</a><a href="impacts.html">Impact review</a><a href="findings.html">Findings</a><a href="observation-horizons.json">Raw horizon JSON</a></nav>
<h1>Observation horizons</h1><p class="lede">Broader activity context for a slow-moving standards portfolio, anchored to the same observation timestamp as the monitor.</p>
<div class="note"><strong>Interpretation boundary:</strong> {escape(data.get('interpretation') or '')} Evidence links in project rows refer to the <strong>current snapshot-to-snapshot window</strong>; their presence does not mean the broader-horizon activity caused that finding or review obligation.</div>{''.join(sections)}
</main></body></html>'''


def homepage_fragment(data: dict) -> str:
    cards = []
    for horizon in data.get("horizons", []):
        share = float(horizon.get("portfolio_share", 0)) * 100
        horizon_id = escape(horizon.get("id") or "horizon", quote=True)
        cards.append(
            f'''<a class="layer" href="observation-horizons.html#{horizon_id}"><strong>{escape(horizon.get('label') or '')}</strong>
<span>{int(horizon.get('project_count', 0))} project(s)</span><small>{share:.0f}% of the discovered portfolio recorded activity between {escape(_fmt(horizon.get('start')))} and {escape(_fmt(horizon.get('end')))}.</small></a>'''
        )
    return f'''<h2>Observation horizons</h2>
<p class="lede">The latest evidence window remains the precise snapshot-to-snapshot comparison above. Broader horizons help distinguish a quiet scan from sustained portfolio inactivity or infrequent movement. These horizons use repository <code>last_activity_at</code> evidence; they do not count normative changes.</p>
<div class="layers">{''.join(cards)}</div>
<p class="lede"><a href="observation-horizons.html">Inspect observation-horizon evidence →</a> · <a href="findings.html">Findings</a> · <a href="impacts.html">Impact review</a> · <a href="observation-horizons.json">Raw JSON</a></p>
'''


def inject_homepage(html: str, fragment: str) -> str:
    marker = "<h2>How to read this monitor</h2>"
    if marker not in html:
        raise ValueError("homepage insertion marker not found")
    return html.replace(marker, fragment + marker, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and publish broader observation horizons")
    parser.add_argument("--portfolio", type=Path, default=ROOT / "site" / "portfolio.json")
    parser.add_argument("--changes", type=Path, default=ROOT / "site" / "changes.json")
    parser.add_argument("--impacts", type=Path, default=ROOT / "site" / "impacts.json")
    parser.add_argument("--findings", type=Path, default=ROOT / "site" / "findings.json")
    parser.add_argument("--index", type=Path, default=ROOT / "site" / "index.html")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()

    snapshot = json.loads(args.portfolio.read_text(encoding="utf-8"))
    changes = _read(args.changes, {})
    impacts = _read(args.impacts, {})
    findings = _read(args.findings, {})
    evidence_index = build_evidence_index(changes, impacts, findings)
    data = build_horizons(snapshot)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "observation-horizons.json").write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "observation-horizons.html").write_text(
        render_horizons(data, evidence_index), encoding="utf-8"
    )
    index_html = args.index.read_text(encoding="utf-8")
    args.index.write_text(inject_homepage(index_html, homepage_fragment(data)), encoding="utf-8")
    print("built month-to-observed-date and trailing-90-day observation horizons with evidence links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
