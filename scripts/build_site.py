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
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return value


def render(snapshot: dict) -> str:
    projects = snapshot.get("projects", [])
    generated_at = snapshot.get("generated_at", "unknown")
    source = snapshot.get("source", {})
    rows = []
    for project in projects:
        topics = ", ".join(project.get("topics") or [])
        search_blob = " ".join([
            project.get("name") or "",
            project.get("path_with_namespace") or "",
            project.get("description") or "",
            topics,
        ]).lower()
        state = "Archived" if project.get("archived") else "Active"
        rows.append(f'''<tr data-search="{escape(search_blob, quote=True)}" data-state="{state.lower()}">
<td><a href="{escape(project.get('web_url') or '#', quote=True)}">{escape(project.get('name') or 'Unnamed')}</a><div class="path">{escape(project.get('path_with_namespace') or '')}</div></td>
<td>{escape(project.get('default_branch') or '—')}</td>
<td>{state}</td>
<td>{escape(fmt_date(project.get('last_activity_at')))}</td>
<td>{escape(topics or '—')}</td>
</tr>''')

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Monitor</title>
<style>
:root{{color-scheme:light dark;--bg:#f7f8fa;--panel:#fff;--text:#18202a;--muted:#667085;--line:#dfe3e8;--accent:#155eef}}
@media(prefers-color-scheme:dark){{:root{{--bg:#101318;--panel:#171b21;--text:#f4f6f8;--muted:#a9b2bd;--line:#303640;--accent:#84adff}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}} a{{color:var(--accent);text-decoration:none}} a:hover{{text-decoration:underline}}
main{{max-width:1240px;margin:auto;padding:40px 24px 72px}} h1{{font-size:34px;margin:0 0 8px}} .lede{{color:var(--muted);max-width:800px;margin:0 0 28px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:24px 0}} .stat{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}} .stat strong{{display:block;font-size:25px}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}} input,select{{font:inherit;padding:10px 12px;border-radius:8px;border:1px solid var(--line);background:var(--panel);color:var(--text)}} input{{min-width:min(100%,360px);flex:1}}
.table-wrap{{overflow:auto;background:var(--panel);border:1px solid var(--line);border-radius:12px}} table{{width:100%;border-collapse:collapse;min-width:900px}} th,td{{text-align:left;padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top}} th{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}} tr:last-child td{{border-bottom:0}} .path{{font-size:12px;color:var(--muted);margin-top:3px}} footer{{color:var(--muted);font-size:13px;margin-top:28px}} code{{font-size:12px}} .note{{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel);margin:24px 0}}
</style>
</head>
<body><main>
<h1>UN/CEFACT Portfolio Monitor</h1>
<p class="lede">Live discovery of public projects in the UN/CEFACT GitLab namespace. This page reports observable repository metadata only; it does not yet assign health, impact, or assurance conclusions.</p>
<div class="stats">
<div class="stat"><span>Discovered projects</span><strong>{len(projects)}</strong></div>
<div class="stat"><span>Source</span><strong>GitLab</strong><small>{escape(source.get('group',''))}</small></div>
<div class="stat"><span>Observed</span><strong>{escape(fmt_date(generated_at))}</strong><small>UTC snapshot</small></div>
</div>
<div class="note">The exact normalized evidence used to generate this view is available as <a href="portfolio.json">portfolio.json</a>.</div>
<div class="controls"><input id="q" type="search" placeholder="Search projects, paths, descriptions or topics…" aria-label="Search portfolio"><select id="state"><option value="all">All states</option><option value="active">Active</option><option value="archived">Archived</option></select></div>
<div class="table-wrap"><table><thead><tr><th>Project</th><th>Default branch</th><th>State</th><th>Last activity</th><th>Topics</th></tr></thead><tbody id="rows">{''.join(rows)}</tbody></table></div>
<footer>Generated from <code>{escape(source.get('base_url',''))}/{escape(source.get('group',''))}</code> at {escape(generated_at)}. Portfolio inventory is observational evidence, not an assurance score.</footer>
</main>
<script>
const q=document.getElementById('q'), state=document.getElementById('state');
function filter(){{const text=q.value.trim().toLowerCase(), s=state.value;document.querySelectorAll('#rows tr').forEach(row=>{{const matchesText=!text||row.dataset.search.includes(text);const matchesState=s==='all'||row.dataset.state===s;row.hidden=!(matchesText&&matchesState);}})}}
q.addEventListener('input',filter);state.addEventListener('change',filter);
</script></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the static portfolio site from a normalized snapshot")
    parser.add_argument("--input", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    snapshot = json.loads(args.input.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "index.html").write_text(render(snapshot), encoding="utf-8")
    (args.output_dir / "portfolio.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"built site with {snapshot.get('project_count', len(snapshot.get('projects', [])))} projects -> {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
