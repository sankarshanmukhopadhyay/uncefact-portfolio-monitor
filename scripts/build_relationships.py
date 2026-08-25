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

from uncefact_portfolio_monitor.relationships import mermaid_graph, validate_relationships


def render(data: dict, mermaid: str) -> str:
    rows = []
    for rel in data.get("relationships", []):
        rows.append(
            "<tr>"
            f"<td><code>{escape(rel['from'])}</code></td>"
            f"<td>{escape(rel['type'])}</td>"
            f"<td><code>{escape(rel['to'])}</code></td>"
            f"<td>{escape(rel.get('note') or '—')}</td>"
            "</tr>"
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT Portfolio Relationships</title>
<style>body{{font:15px/1.55 system-ui,sans-serif;max-width:1200px;margin:auto;padding:36px 22px;color:#18202a}}a{{color:#155eef}}table{{width:100%;border-collapse:collapse;margin:24px 0}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd;vertical-align:top}}th{{font-size:12px;text-transform:uppercase}}code,pre{{font-family:ui-monospace,SFMono-Regular,monospace}}pre{{overflow:auto;background:#f5f7fa;padding:16px;border-radius:8px}}.note{{border-left:3px solid #155eef;padding:10px 14px;background:#f5f7fa}}</style></head>
<body><p><a href="index.html">← Portfolio</a></p><h1>Declared portfolio relationships</h1>
<p>This view publishes manually reviewed relationship declarations over the discovered portfolio. These declarations are governance inputs, not facts inferred from repository activity and not statements of trust or authority.</p>
<div class="note">Machine-readable evidence: <a href="relationships.json">relationships.json</a> · Mermaid source: <a href="relationships.mmd">relationships.mmd</a></div>
<table><thead><tr><th>From</th><th>Relationship</th><th>To</th><th>Note</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<h2>Mermaid graph source</h2><pre>{escape(mermaid)}</pre>
</body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and publish declared portfolio relationships")
    parser.add_argument("--snapshot", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "relationships.toml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()

    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    config = tomllib.loads(args.config.read_text(encoding="utf-8"))
    data = validate_relationships(snapshot, config)
    mermaid = mermaid_graph(data)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "relationships.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "relationships.mmd").write_text(mermaid, encoding="utf-8")
    (args.output_dir / "relationships.html").write_text(render(data, mermaid), encoding="utf-8")
    print(f"validated and published {data['relationship_count']} relationships")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
