# UN/CEFACT Portfolio Monitor

Evidence-driven monitoring of the UN/CEFACT open-source portfolio: repository health, specification dependencies, cross-project change impact, semantic alignment, and portfolio assurance.

## Design principles

1. **Evidence before scores.** Findings must point to inspectable evidence.
2. **Portfolio coherence over activity volume.** A green repository can still create a cross-project risk.
3. **Declarative relationships.** Portfolio membership and dependencies live in configuration, not hard-coded Python.
4. **Provider neutrality.** CI, repository inspection, specification checks, RAHP, and future analyzers may contribute evidence; none is the universal source of truth.
5. **Human review for material inference.** The monitor identifies review obligations; it does not silently convert change into trust conclusions.

## Current capability

`v0.2.x` adds dynamic discovery of the public UN/CEFACT GitLab portfolio under `un/unece/uncefact`.

Run locally:

```bash
python scripts/discover_portfolio.py
```

The collector:

- reads the namespace from `config/portfolio.toml`;
- follows GitLab pagination;
- includes subgroups;
- normalizes evidence-relevant project metadata;
- writes stable JSON to `reports/latest/portfolio.json`.

GitHub Actions also runs the scan weekly and on demand, retaining the resulting snapshot as an artifact for later inspection and comparison.

## Development flow

Substantive work follows:

`Issue → branch → pull request → CI → merge → release manifest → GitHub Actions release`

The repository's first README commit was the only bootstrap exception required to make branch/PR development possible.

## Release codenames

Each release receives a randomly selected codename from the direct pages in Wikipedia's `Category:Tributaries of the Ganges`. The selected name is recorded in the release manifest, making the outcome auditable even though selection is random.

- **v0.1.0 — Tamsa**: foundation, governance, CI, and release automation.
- **v0.2.0 — Ghaghara**: dynamic GitLab portfolio discovery and scan artifacts.

## Roadmap

Next milestones add change detection, repository-health evidence, explicit cross-project relationships, impact propagation, and portfolio findings. The monitor will remain evidence-driven and will not treat any single assurance provider as the portfolio-wide source of truth.
