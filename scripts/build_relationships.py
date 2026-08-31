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


MERMAID_VERSION = "11.4.1"


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
<style>
:root{{--bg:#fff;--panel:#f5f7fa;--text:#18202a;--muted:#667085;--line:#ddd;--accent:#155eef}}
*{{box-sizing:border-box}}body{{font:15px/1.55 system-ui,sans-serif;max-width:1200px;margin:auto;padding:36px 22px;color:var(--text);background:var(--bg)}}a{{color:var(--accent)}}table{{width:100%;border-collapse:collapse;margin:24px 0}}th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:12px;text-transform:uppercase}}code,pre{{font-family:ui-monospace,SFMono-Regular,monospace}}pre{{overflow:auto;background:var(--panel);padding:16px;border-radius:8px}}.note{{border-left:3px solid var(--accent);padding:10px 14px;background:var(--panel)}}.graph{{margin:24px 0;padding:20px;border:1px solid var(--line);border-radius:10px;overflow:auto;background:var(--bg)}}.mermaid{{min-width:640px;text-align:center}}.render-error{{display:none;color:#b42318;background:#fef3f2;border:1px solid #fecdca;border-radius:8px;padding:12px;margin-top:12px}}details{{margin-top:28px}}summary{{cursor:pointer;font-weight:600;color:var(--accent)}}.lede{{color:var(--muted)}}
</style></head>
<body><p><a href="index.html">← Portfolio</a></p><h1>Declared portfolio relationships</h1>
<p class="lede">This view publishes manually reviewed relationship declarations over the discovered portfolio. These declarations are governance inputs, not facts inferred from repository activity and not statements of trust or authority.</p>
<div class="note">Machine-readable evidence: <a href="relationships.json">relationships.json</a> · Mermaid source: <a href="relationships.mmd">relationships.mmd</a></div>
<h2>Relationship graph</h2>
<div class="graph" aria-label="Declared portfolio relationship graph"><pre class="mermaid">{escape(mermaid)}</pre><div id="mermaid-error" class="render-error" role="alert">The relationship graph could not be rendered in this browser. Use the relationship table below or inspect <a href="relationships.mmd">relationships.mmd</a>.</div></div>
<h2>Declared relationships</h2>
<table><thead><tr><th>From</th><th>Relationship</th><th>To</th><th>Note</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<details><summary>View Mermaid graph source</summary><pre>{escape(mermaid)}</pre></details>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs';
try {{
  mermaid.initialize({{startOnLoad: false, securityLevel: 'strict', theme: 'default'}});
  await mermaid.run({{querySelector: '.mermaid'}});
}} catch (error) {{
  console.error('Mermaid relationship graph failed to render', error);
  document.getElementById('mermaid-error').style.display = 'block';
}}
</script>
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
