#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.gitlab import GitLabSource, build_snapshot, discover_projects


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover the configured UN/CEFACT GitLab portfolio")
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "portfolio.toml")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    config = tomllib.loads(args.config.read_text(encoding="utf-8"))
    source_config = config["source"]
    source = GitLabSource(
        base_url=source_config["base_url"],
        group=source_config["group"],
        include_subgroups=source_config.get("include_subgroups", True),
        archived=source_config.get("archived", False),
    )
    projects = discover_projects(source)
    snapshot = build_snapshot(source, projects)
    output = args.output or ROOT / config["output"]["path"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"discovered {len(projects)} projects -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
