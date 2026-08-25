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

from uncefact_portfolio_monitor.external import validate_external_dependencies


def render(data: dict) -> str:
    rows = []
    for dep in data.get("dependencies", []):
        projects = "<br>".join(f"<code>{escape(p)}</code>" for p in dep["affected_projects"])
        rows.append(
            "<tr>"
            f"<td><a href=\"{escape(dep['url'], quote=True)}\">{escape(dep['name'])}</a><div><code>{escape(dep['id'])}</code></div></td>"
            f"<td>{escape(dep['type'])}</td><td>{projects}</td><td>{escape(dep['note'])}</td></tr>"
        )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>UN/CEFACT External Dependencies</title><style>body{{font:15px/1.55 system-ui,sans-serif;max-width:1200px;margin:auto;padding:36px 22px;color:#18202a}}a{{color:#155eef}}table{{width:100%;border-collapse:collapse;margin:24px 0}}th,td{{text-align:left;padding:10px;border-bottom:1px solid #ddd;vertical-align:top}}th{{font-size:12px;text-transform:uppercase}}code{{font-family:ui-monospace,SFMono-Regular,monospace}}.note{{border-left:3px solid #155eef;padding:10px 14px;background:#f5f7fa}}</style></head>
<body><p><a href="index.html">← Portfolio</a> · <a href="findings.html">Findings</a></p><h1>Declared external standards dependencies</h1>
<p>This inventory identifies external specifications or protocols that may materially affect internal projects. It does not claim that an external source changed or that an internal project is incompatible.</p>
<div class="note">{data.get('dependency_count',0)} declared dependency record(s). Machine-readable evidence: <a href="external-dependencies.json">external-dependencies.json</a>.</div>
<table><thead><tr><th>External source</th><th>Type</th><th>Affected projects</th><th>Review note</th></tr></thead><tbody>{''.join(rows)}</tbody></table></body></html>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "external-dependencies.toml")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "site")
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    config = tomllib.loads(args.config.read_text(encoding="utf-8"))
    data = validate_external_dependencies(snapshot, config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "external-dependencies.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.output_dir / "external-dependencies.html").write_text(render(data), encoding="utf-8")
    print(f"published {data['dependency_count']} external dependencies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
