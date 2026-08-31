#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fmt_date(value: str | None) -> str:
    if not value:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError:
        return value


def _read(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def _change_detail(changes: dict, limit: int = 8) -> str:
    items: list[str] = []
    for item in changes.get("changed", []):
        fields = ", ".join(sorted((item.get("fields") or {}).keys())) or "metadata"
        items.append(
            f"<li><code>{escape(item.get('path_with_namespace') or 'unknown')}</code> — "
            f"changed {escape(fields)}</li>"
        )
        if len(items) >= limit:
            break
    for kind, label in (("added", "added to discovery"), ("removed", "removed from discovery")):
        if len(items) >= limit:
            break
        for item in changes.get(kind, []):
            items.append(
                f"<li><code>{escape(item.get('path_with_namespace') or 'unknown')}</code> — {label}</li>"
            )
            if len(items) >= limit:
                break
    return "".join(items) or '<li class="empty">No structural changes in this observation.</li>'


def _review_detail(impacts: dict, limit: int = 8) -> str:
    items: list[str] = []
    for item in impacts.get("review_obligations", [])[:limit]:
        reason = item.get("reason") or item.get("relationship_type") or "relationship-aware review"
        items.append(
            f"<li><code>{escape(item.get('review_project') or 'unknown')}</code> reviews "
            f"<code>{escape(item.get('changed_project') or 'unknown')}</code> — {escape(reason)}</li>"
        )
    return "".join(items) or '<li class="empty">No direct review obligations in this observation.</li>'


def _finding_detail(lifecycle: dict, limit: int = 8) -> str:
    items: list[str] = []
    for item in lifecycle.get("records", []):
        if item.get("status") != "active":
            continue
        items.append(
            f"<li><strong>{escape(str(item.get('severity') or 'unknown').upper())}</strong> "
            f"<code>{escape(item.get('finding_id') or 'unknown')}</code> — "
            f"<code>{escape(item.get('subject_project') or 'unknown')}</code> reviewing "
            f"<code>{escape(item.get('dependency_project') or 'unknown')}</code></li>"
        )
        if len(items) >= limit:
            break
    return "".join(items) or '<li class="empty">No active lifecycle findings in this observation.</li>'


def render(
    snapshot: dict,
    changes: dict | None = None,
    impacts: dict | None = None,
    lifecycle: dict | None = None,
    external: dict | None = None,
) -> str:
    changes = changes or {"summary": {}}
    impacts = impacts or {"summary": {}}
    lifecycle = lifecycle or {"summary": {}}
    external = external or {"dependency_count": 0}
    projects = snapshot.get("projects", [])
    generated_at = snapshot.get("generated_at", "unknown")
    source = snapshot.get("source", {})
    change_summary = changes.get("summary", {})
    lifecycle_summary = lifecycle.get("summary", {})
    structural = (
        int(change_summary.get("added", 0))
        + int(change_summary.get("removed", 0))
        + int(change_summary.get("changed", 0))
    )
    obligations = int(impacts.get("summary", {}).get("review_obligations", 0))
    active_findings = int(lifecycle_summary.get("active", 0))
    resolved_findings = int(lifecycle_summary.get("resolved", 0))
    external_count = int(external.get("dependency_count", 0))

    rows = []
    for project in projects:
        topics = ", ".join(project.get("topics") or [])
        search_blob = " ".join(
            [
                project.get("name") or "",
                project.get("path_with_namespace") or "",
                project.get("description") or "",
                topics,
            ]
        ).lower()
        state = "Archived" if project.get("archived") else "Active"
        rows.append(
            f'''<tr data-search="{escape(search_blob, quote=True)}" data-state="{state.lower()}">
<td><a href="{escape(project.get('web_url') or '#', quote=True)}">{escape(project.get('name') or 'Unnamed')}</a><div class="path">{escape(project.get('path_with_namespace') or '')}</div></td>
<td>{escape(project.get('default_branch') or '—')}</td><td>{state}</td><td>{escape(fmt_date(project.get('last_activity_at')))}</td><td>{escape(topics or '—')}</td></tr>'''
        )

    nav = [
        ("changes.html", "Changes", f"{structural} structural change(s)", "Observed snapshot-to-snapshot differences."),
        ("relationships.html", "Relationships", "Declared graph", "Portfolio dependency and profile relationships."),
        ("impacts.html", "Impact review", f"{obligations} obligation(s)", "Direct review obligations derived from changes plus relationships."),
        ("findings.html", "Findings", f"{active_findings} active", "Current policy-matched findings requiring tracked disposition."),
        ("external-dependencies.html", "External dependencies", f"{external_count} declared", "Standards and protocol context declared by portfolio projects."),
        ("weekly-report.html", "Weekly report", f"{resolved_findings} resolved retained", "Lifecycle-aware human-readable portfolio assurance report."),
    ]
    cards = "".join(
        f'''<a class="layer" href="{href}"><strong>{escape(title)}</strong><span>{escape(metric)}</span><small>{escape(desc)}</small></a>'''
        for href, title, metric, desc in nav
    )
    observation_window = (
        f"{escape(fmt_date(changes.get('previous_generated_at')))} → "
        f"{escape(fmt_date(changes.get('current_generated_at') or generated_at))}"
        if changes.get("previous_generated_at")
        else f"Current snapshot: {escape(fmt_date(generated_at))}"
    )

    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Monitor</title><style>
:root{{--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef;--soft:#eef4ff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}main{{max-width:1240px;margin:auto;padding:40px 24px 72px}}h1{{font-size:36px;margin:0 0 8px}}h2{{margin-top:36px}}.lede{{color:var(--muted);max-width:920px;margin:0 0 20px}}.boundary{{border-left:3px solid var(--accent);padding:11px 14px;background:var(--panel);margin:20px 0 28px}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:20px 0}}.stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:17px}}.stat strong{{display:block;font-size:26px}}.stat small{{display:block;color:var(--muted);margin-top:3px}}.layers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:18px 0 30px}}.layer{{display:block;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:17px;color:var(--text)}}.layer:hover{{border-color:var(--accent);text-decoration:none}}.layer strong,.layer span,.layer small{{display:block}}.layer span{{font-size:20px;margin:5px 0}}.layer small{{color:var(--muted)}}.detail-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin:18px 0}}.detail{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:17px}}.detail h3{{margin:0 0 10px;font-size:17px}}.detail ul{{margin:0;padding-left:20px}}.detail li{{margin:7px 0}}.empty{{color:var(--muted)}}.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}}input,select{{font:inherit;padding:10px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--text)}}input{{min-width:min(100%,360px);flex:1}}.table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px}}table{{width:100%;border-collapse:collapse;min-width:900px}}th,td{{text-align:left;padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}}tr:last-child td{{border-bottom:0}}.path{{font-size:12px;color:var(--muted);margin-top:3px}}footer{{color:var(--muted);font-size:13px;margin-top:28px}}code{{font-size:12px}}
</style></head><body><main>
<h1>UN/CEFACT Portfolio Monitor</h1><p class="lede">Evidence-driven view of the public UN/CEFACT open-source portfolio. The dashboard connects inventory, observed change, declared relationships, review obligations, policy-matched findings, lifecycle state, and external dependency context.</p>
<div class="boundary"><strong>Interpretation boundary:</strong> these counts summarize inspectable evidence. They are not an aggregate assurance score and do not by themselves establish incompatibility, assurance failure, or a trust decision.</div>
<div class="stats"><div class="stat"><span>Projects</span><strong>{len(projects)}</strong><small>Current discovery</small></div><div class="stat"><span>Structural changes</span><strong>{structural}</strong><small>Since previous observation</small></div><div class="stat"><span>Review obligations</span><strong>{obligations}</strong><small>Direct relationship-aware review</small></div><div class="stat"><span>Active findings</span><strong>{active_findings}</strong><small>Policy matched</small></div><div class="stat"><span>External dependencies</span><strong>{external_count}</strong><small>Declared context</small></div><div class="stat"><span>Observed</span><strong>{escape(fmt_date(generated_at))}</strong><small>Latest snapshot</small></div></div>
<h2>Evidence layers</h2><div class="layers">{cards}</div>
<h2>Current observation</h2>
<p class="lede">Decision-first summary for the latest evidence window: <strong>{observation_window}</strong>. Drill into the linked evidence before drawing compatibility, assurance, or trust conclusions.</p>
<div class="detail-grid">
<section class="detail"><h3>What changed</h3><ul>{_change_detail(changes)}</ul><p><a href="changes.html">Inspect all observed changes →</a></p></section>
<section class="detail"><h3>Direct review queue</h3><ul>{_review_detail(impacts)}</ul><p><a href="impacts.html">Inspect review obligations →</a></p></section>
<section class="detail"><h3>Active findings</h3><ul>{_finding_detail(lifecycle)}</ul><p><a href="findings.html">Inspect finding evidence →</a></p></section>
</div>
<h2>How to read this monitor</h2>
<p class="lede"><strong>Observed change</strong> is evidence, not a defect. <strong>Review obligations</strong> are relationship-aware prompts for examination. <strong>Findings</strong> are policy-matched evidence conditions requiring tracked disposition. None of these layers is an aggregate trust score.</p>
<h2>Portfolio inventory</h2><p class="lede">Search the current discovery below. Exact normalized discovery evidence is available as <a href="portfolio.json">portfolio.json</a>.</p><div class="controls"><input id="q" type="search" placeholder="Search projects, paths, descriptions or topics…" aria-label="Search portfolio"><select id="state"><option value="all">All states</option><option value="active">Active</option><option value="archived">Archived</option></select></div><div class="table-wrap"><table><thead><tr><th>Project</th><th>Default branch</th><th>State</th><th>Last activity</th><th>Topics</th></tr></thead><tbody id="rows">{''.join(rows)}</tbody></table></div>
<footer>Generated from <code>{escape(source.get('base_url',''))}/{escape(source.get('group',''))}</code> at {escape(generated_at)}. Follow the linked evidence layers for interpretation and disposition.</footer></main><script>const q=document.getElementById('q'),state=document.getElementById('state');function filter(){{const text=q.value.trim().toLowerCase(),s=state.value;document.querySelectorAll('#rows tr').forEach(row=>{{row.hidden=!((!text||row.dataset.search.includes(text))&&(s==='all'||row.dataset.state===s));}})}}q.addEventListener('input',filter);state.addEventListener('change',filter);</script></body></html>'''


def render_changes(changes: dict) -> str:
    summary = changes.get("summary", {})
    activity_rows = []
    for item in changes.get("activity_advanced", []):
        activity_rows.append(
            "<tr>"
            f"<td><code>{escape(item.get('path_with_namespace') or 'unknown')}</code></td>"
            f"<td>{escape(fmt_date(item.get('before')))}</td>"
            f"<td>{escape(fmt_date(item.get('after')))}</td>"
            "</tr>"
        )
    if not activity_rows:
        activity_rows.append('<tr><td colspan="3" class="empty">No activity-only advancements.</td></tr>')

    structural_rows = []
    for kind in ("added", "removed"):
        for item in changes.get(kind, []):
            structural_rows.append(
                "<tr>"
                f"<td>{escape(kind.title())}</td>"
                f"<td><code>{escape(item.get('path_with_namespace') or 'unknown')}</code></td>"
                "<td>—</td><td>—</td>"
                "</tr>"
            )
    for item in changes.get("changed", []):
        fields = item.get("fields") or {}
        if not fields:
            structural_rows.append(
                "<tr><td>Changed</td>"
                f"<td><code>{escape(item.get('path_with_namespace') or 'unknown')}</code></td>"
                "<td>metadata</td><td>Observed value changed</td></tr>"
            )
            continue
        for field, delta in sorted(fields.items()):
            structural_rows.append(
                "<tr><td>Changed</td>"
                f"<td><code>{escape(item.get('path_with_namespace') or 'unknown')}</code></td>"
                f"<td><code>{escape(field)}</code></td>"
                f"<td><code>{escape(json.dumps(delta.get('before'), ensure_ascii=False))}</code> → "
                f"<code>{escape(json.dumps(delta.get('after'), ensure_ascii=False))}</code></td></tr>"
            )
    if not structural_rows:
        structural_rows.append('<tr><td colspan="4" class="empty">No structural changes in this observation.</td></tr>')

    window = (
        f"{escape(fmt_date(changes.get('previous_generated_at')))} → "
        f"{escape(fmt_date(changes.get('current_generated_at')))}"
    )
    structural = (
        int(summary.get("added", 0))
        + int(summary.get("removed", 0))
        + int(summary.get("changed", 0))
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Changes</title><style>
:root{{--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}}main{{max-width:1200px;margin:auto;padding:36px 22px 72px}}a{{color:var(--accent);text-decoration:none}}a:hover{{text-decoration:underline}}h1{{margin-bottom:8px}}.lede,.empty{{color:var(--muted)}}.note{{border-left:3px solid var(--accent);padding:11px 14px;background:var(--panel);margin:20px 0}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}}.stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}}.stat strong{{display:block;font-size:24px}}.table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:16px 0 28px}}table{{width:100%;border-collapse:collapse;min-width:720px}}th,td{{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}}code{{font-family:ui-monospace,SFMono-Regular,monospace;font-size:12px}}
</style></head><body><main><p><a href="index.html">← Portfolio</a> · <a href="changes.json">Raw JSON</a></p>
<h1>Observed portfolio changes</h1><p class="lede">Human-readable snapshot comparison. This page renders the canonical <a href="changes.json">changes.json</a> evidence without changing its machine-readable contract.</p>
<div class="note"><strong>Observation window:</strong> {window}. Structural change is evidence requiring interpretation; it is not automatically incompatibility or assurance failure.</div>
<div class="stats"><div class="stat"><span>Structural</span><strong>{structural}</strong></div><div class="stat"><span>Added</span><strong>{summary.get('added',0)}</strong></div><div class="stat"><span>Removed</span><strong>{summary.get('removed',0)}</strong></div><div class="stat"><span>Changed</span><strong>{summary.get('changed',0)}</strong></div><div class="stat"><span>Activity advanced</span><strong>{summary.get('activity_advanced',0)}</strong></div></div>
<h2>Structural changes</h2><div class="table-wrap"><table><thead><tr><th>Type</th><th>Project</th><th>Field</th><th>Before → after</th></tr></thead><tbody>{''.join(structural_rows)}</tbody></table></div>
<h2>Activity advancements</h2><p class="lede">Projects whose last-activity timestamp advanced between observations. These are reported separately from structural metadata changes.</p><div class="table-wrap"><table><thead><tr><th>Project</th><th>Previous activity</th><th>Current activity</th></tr></thead><tbody>{''.join(activity_rows)}</tbody></table></div>
</main></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the static v1 portfolio assurance dashboard")
    parser.add_argument("--input", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--changes", type=Path, default=ROOT / "reports" / "latest" / "changes.json")
    parser.add_argument("--impacts", type=Path, default=ROOT / "site" / "impacts.json")
    parser.add_argument("--lifecycle", type=Path, default=ROOT / "site" / "findings-lifecycle.json")
    parser.add_argument("--external", type=Path, default=ROOT / "site" / "external-dependencies.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    snapshot = _read(args.input, {})
    changes = _read(args.changes, {"summary": {}})
    impacts = _read(args.impacts, {"summary": {}})
    lifecycle = _read(args.lifecycle, {"summary": {}})
    external = _read(args.external, {"dependency_count": 0})
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "index.html").write_text(
        render(snapshot, changes, impacts, lifecycle, external), encoding="utf-8"
    )
    (args.output_dir / "portfolio.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "changes.json").write_text(
        json.dumps(changes, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output_dir / "changes.html").write_text(render_changes(changes), encoding="utf-8")
    print(
        f"built dashboard with {snapshot.get('project_count', len(snapshot.get('projects', [])))} "
        f"projects -> {args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
