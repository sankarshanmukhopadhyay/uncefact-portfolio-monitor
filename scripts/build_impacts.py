#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.impacts import propagate_impacts


def render(data: dict) -> str:
    rows = []
    for item in data.get("review_obligations", []):
        rows.append(
            "<tr>"
            f"<td><code>{escape(item['review_project'])}</code></td>"
            f"<td><code>{escape(item['changed_project'])}</code></td>"
            f"<td>{escape(item['relationship_type'])}</td>"
            f"<td>{escape(item['change_type'])}</td>"
            f"<td>{escape(item['reason'])}</td>"
            "</tr>"
        )
    if not rows:
        rows.append('<tr><td colspan="5">No direct review obligations in this observation.</td></tr>')
    info_count = data.get("summary", {}).get("informational", 0)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Impact Review</title>
<style>body{{font:15px/1.55 system-ui,sans-serif;max-width:1200px;margin:auto;padding:36px 22px;color:#18202a}}a{{color:#155eef}}table{{width:100%;border-collapse:collapse;margin:24px 0}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd;vertical-align:top}}th{{font-size:12px;text-transform:uppercase}}code{{font-family:ui-monospace,SFMono-Regular,monospace}}.note{{border-left:3px solid #155eef;padding:10px 14px;background:#f5f7fa}}</style></head>
<body><p><a href="index.html">← Portfolio</a> · <a href="relationships.html">Relationships</a></p><h1>Portfolio impact review obligations</h1>
<p>These are deterministic review obligations derived from observed structural change and declared dependency relationships. They are not assurance failures, compatibility conclusions, or trust decisions.</p>
<div class="note">{data.get('summary',{}).get('review_obligations',0)} direct review obligation(s); {info_count} informational event(s). Machine-readable evidence: <a href="impacts.json">impacts.json</a>.</div>
<table><thead><tr><th>Review project</th><th>Changed dependency</th><th>Relationship</th><th>Observed change</th><th>Why review</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Derive review obligations from change and relationship evidence")
    parser.add_argument("--changes", type=Path, default=ROOT / "reports" / "latest" / "changes.json")
    parser.add_argument("--relationships", type=Path, default=ROOT / "site" / "relationships.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    changes = json.loads(args.changes.read_text(encoding="utf-8"))
    relationships = json.loads(args.relationships.read_text(encoding="utf-8"))
    data = propagate_impacts(changes, relationships)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "impacts.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "impacts.html").write_text(render(data), encoding="utf-8")
    print(f"published {data['summary']['review_obligations']} review obligations and {data['summary']['informational']} informational events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
