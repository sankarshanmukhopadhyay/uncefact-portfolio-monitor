#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from uncefact_portfolio_monitor.changes import compare_snapshots


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare UN/CEFACT portfolio snapshots")
    parser.add_argument("--previous", type=Path, default=ROOT / ".state" / "portfolio.json")
    parser.add_argument("--current", type=Path, default=ROOT / "reports" / "latest" / "portfolio.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "latest" / "changes.json")
    args = parser.parse_args()

    previous = None
    if args.previous.exists():
        previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    result = compare_snapshots(previous, current)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = result["summary"]
    print(
        "changes: "
        f"added={summary['added']} removed={summary['removed']} "
        f"changed={summary['changed']} activity={summary['activity_advanced']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
