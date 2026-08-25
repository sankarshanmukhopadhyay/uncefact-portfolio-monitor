# Operator Guide

## Normal operation

The monitor runs weekly on GitHub Actions and can also be triggered manually through the `Portfolio scan and Pages` workflow.

Each successful observation performs the same pipeline:

```text
Discover portfolio
  → compare with retained baseline
  → publish internal relationships
  → derive direct review obligations
  → evaluate declared finding policies
  → publish external dependency context
  → update finding lifecycle
  → generate weekly report
  → retain state/evidence
  → deploy GitHub Pages
```

## Local run

Python 3.11 or newer is required.

```bash
python scripts/discover_portfolio.py
python scripts/compare_snapshots.py
python scripts/build_site.py
python scripts/build_relationships.py
python scripts/build_impacts.py
python scripts/build_findings.py
python scripts/build_external_dependencies.py
python scripts/build_lifecycle_report.py
```

A first local run has no retained baseline, so change comparison reports baseline establishment rather than treating the whole namespace as newly added.

## What to review first

1. `weekly-report.html` for the human-readable portfolio summary.
2. `findings.html` for current policy-matched findings.
3. `impacts.html` for direct review obligations that have not necessarily become findings.
4. `relationships.html` to inspect the declared internal dependency graph.
5. `external-dependencies.html` for declared external review context.
6. JSON evidence when investigating why a finding or obligation exists.

## Disposition model

The monitor currently derives active/resolved lifecycle state from whether a stable finding ID remains present in the current evidence. Human disposition beyond that evidence lifecycle — for example accepted risk, specification correction, false-positive policy adjustment, or governance decision — should be recorded through project workflow rather than inferred by the monitor.

## Release operation

Substantive development follows:

`Issue → branch → PR → CI → merge → release manifest → GitHub Actions release`

Release manifests are validated in CI. A merge to `main` containing a new valid manifest causes the release workflow to create the tag and GitHub Release automatically.

## Failure handling

- **Discovery/API failure:** do not advance the retained portfolio baseline.
- **Relationship/config validation failure:** treat as monitor configuration failure; do not publish a partial portfolio graph.
- **Policy validation failure:** do not publish findings from an invalid policy set.
- **Pages failure after evidence build:** evidence artifacts remain useful, but the publication surface is stale until deployment succeeds.
- **State-cache miss:** lifecycle/change processing falls back to first-observation semantics rather than inventing history.

## v1 limitations

v1.0 does not automatically poll external standards for semantic changes, score repository health, infer normative compatibility, or make trust decisions. Those remain future extension points under the evidence contract.
