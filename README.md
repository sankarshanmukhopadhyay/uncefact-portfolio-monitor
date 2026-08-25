# UN/CEFACT Portfolio Monitor

Evidence-driven monitoring of the UN/CEFACT open-source portfolio: repository health, specification dependencies, cross-project change impact, semantic alignment, and portfolio assurance.

## Design principles

1. **Evidence before scores.** Findings must point to inspectable evidence.
2. **Portfolio coherence over activity volume.** A green repository can still create a cross-project risk.
3. **Declarative relationships.** Portfolio membership and dependencies live in configuration, not hard-coded Python.
4. **Provider neutrality.** CI, repository inspection, specification checks, RAHP, and future analyzers may contribute evidence; none is the universal source of truth.
5. **Human review for material inference.** The monitor identifies review obligations; it does not silently convert change into trust conclusions.

## Development flow

Substantive work follows:

`Issue → branch → pull request → CI → merge → release manifest → GitHub Actions release`

The repository's first README commit was the only bootstrap exception required to make branch/PR development possible.

## Release codenames

Each release receives a randomly selected codename from the direct pages in Wikipedia's `Category:Tributaries of the Ganges`. The selected name is recorded in the release manifest, making the outcome auditable even though selection is random.

Current foundation release: **v0.1.0 — Tamsa**.

## Status

Early development. The first milestone establishes governance and release automation; portfolio discovery follows in v0.2.x.
