#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = [
    "README.md",
    "docs/EVIDENCE-CONTRACT.md",
    "docs/OPERATIONS.md",
    "config/portfolio.toml",
    "config/relationships.toml",
    "config/finding-policies.toml",
    "config/external-dependencies.toml",
    "scripts/discover_portfolio.py",
    "scripts/compare_snapshots.py",
    "scripts/build_site.py",
    "scripts/build_relationships.py",
    "scripts/build_impacts.py",
    "scripts/build_findings.py",
    "scripts/build_external_dependencies.py",
    "scripts/build_lifecycle_report.py",
    ".github/workflows/ci.yml",
    ".github/workflows/portfolio-scan.yml",
    ".github/workflows/release.yml",
    "releases/v1.0.0.yaml",
]


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            errors.append(f"missing required v1 path: {rel}")

    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    version = str(pyproject.get("project", {}).get("version", ""))
    if not version.startswith("1."):
        errors.append("pyproject version must remain on the stable 1.x line for v1 readiness")

    readme = (root / "README.md").read_text(encoding="utf-8")
    for phrase in ("Evidence contract", "Operator guide", "v1.0"):
        if phrase not in readme:
            errors.append(f"README missing v1 navigation phrase: {phrase}")

    scan = (root / ".github/workflows/portfolio-scan.yml").read_text(encoding="utf-8")
    for script in ("build_findings.py", "build_external_dependencies.py", "build_lifecycle_report.py", "build_site.py"):
        if script not in scan:
            errors.append(f"portfolio workflow does not invoke {script}")

    ci = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    if "release_readiness.py" not in ci:
        errors.append("CI does not enforce release_readiness.py")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"readiness error: {error}", file=sys.stderr)
        return 2
    print("v1 release readiness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
