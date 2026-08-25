#!/usr/bin/env python3
"""Validate a release manifest and emit GitHub Actions outputs."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "config" / "release-codenames.txt"
VERSION_RE = re.compile(r"^v\d+\.\d+\.\d+$")


def parse_manifest(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"invalid manifest line: {raw}")
        data[key.strip()] = value.strip()
    return data


def validate(path: Path) -> dict[str, str]:
    data = parse_manifest(path)
    version = data.get("version", "")
    codename = data.get("codename", "")
    if not VERSION_RE.match(version):
        raise ValueError(f"invalid semantic release tag: {version!r}")
    expected = f"{version}.yaml"
    if path.name != expected:
        raise ValueError(f"manifest filename must be {expected}")
    pool = {line.strip() for line in POOL.read_text(encoding="utf-8").splitlines() if line.strip()}
    if codename not in pool:
        raise ValueError(f"codename {codename!r} is not in configured tributary pool")
    if data.get("status") != "release":
        raise ValueError("release manifest status must be 'release'")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        data = validate(args.manifest)
    except (OSError, ValueError) as exc:
        print(f"release manifest error: {exc}", file=sys.stderr)
        return 2

    output = f"version={data['version']}\ncodename={data['codename']}\nsummary={data.get('summary', '')}\n"
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            handle.write(output)
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
