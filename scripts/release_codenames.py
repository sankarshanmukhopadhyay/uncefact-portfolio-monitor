#!/usr/bin/env python3
"""Repository-local release codename policy for the portfolio monitor."""
from __future__ import annotations

import argparse
import json
import random
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "config" / "release-codenames.txt"
POLICY = ROOT / "config" / "release-codename-policy.json"
RELEASES = ROOT / "releases"

class PolicyError(ValueError):
    pass


def load_pool() -> list[str]:
    return [line.strip() for line in POOL.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]


def load_policy() -> dict:
    return json.loads(POLICY.read_text(encoding="utf-8"))


def parse_manifest(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise PolicyError(f"invalid manifest line in {path.name}: {raw}")
        data[key.strip()] = value.strip()
    return data


def release_bindings() -> list[dict[str, str]]:
    return [parse_manifest(path) for path in sorted(RELEASES.glob("v*.yaml"))]


def validate() -> None:
    pool = load_pool()
    policy = load_policy()
    errors: list[str] = []
    if policy.get("schemaVersion") != 1:
        errors.append("policy schemaVersion must be 1")
    if policy.get("pool") != "config/release-codenames.txt":
        errors.append("policy must reference config/release-codenames.txt")
    if len(pool) < int(policy.get("minimumPoolSize", 20)):
        errors.append("codename pool is below minimumPoolSize")
    folded = [name.casefold() for name in pool]
    if len(folded) != len(set(folded)):
        errors.append("codename pool contains case-insensitive duplicates")
    if not str(policy.get("source", {}).get("url", "")).startswith("https://"):
        errors.append("source URL must use https")
    selection = policy.get("selection", {})
    if selection.get("liveSourceFetchAtRelease") is not False:
        errors.append("release-time source fetching must be disabled")
    if selection.get("persistBeforeAcceptance") is not True:
        errors.append("codename must be persisted before release acceptance")
    allowed = {name.casefold() for name in pool}
    bindings = release_bindings()
    versions = [item.get("version", "") for item in bindings]
    if len(versions) != len(set(versions)):
        errors.append("release manifests contain duplicate semantic versions")
    used: list[str] = []
    for item in bindings:
        codename = item.get("codename", "")
        if codename.casefold() not in allowed:
            errors.append(f"release codename is outside pinned pool: {codename!r}")
        used.append(codename.casefold())
    if not selection.get("allowReuseAfterExhaustion", False) and len(used) != len(set(used)):
        errors.append("release manifests reuse a codename while policy forbids reuse")
    if errors:
        raise PolicyError("; ".join(errors))


def select(version: str, seed: str | None = None) -> tuple[str, bool]:
    validate()
    bindings = release_bindings()
    existing = next((item for item in bindings if item.get("version") == version), None)
    if existing:
        return existing["codename"], True
    pool = load_pool()
    policy = load_policy()
    used = {item.get("codename", "").casefold() for item in bindings}
    candidates = [name for name in pool if name.casefold() not in used]
    if not candidates:
        if policy["selection"].get("allowReuseAfterExhaustion", False):
            candidates = pool
        else:
            raise PolicyError("codename pool exhausted and reuse is forbidden")
    chosen = secrets.choice(candidates) if seed is None else random.Random(seed).choice(candidates)
    return chosen, False


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    choose = sub.add_parser("select")
    choose.add_argument("--version", required=True)
    choose.add_argument("--seed")
    args = parser.parse_args()
    if args.command == "validate":
        validate()
        print("PASS release codename governance")
        return 0
    codename, existing = select(args.version, args.seed)
    print(json.dumps({"version": args.version, "codename": codename, "existing": existing}))
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PolicyError as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(2)
