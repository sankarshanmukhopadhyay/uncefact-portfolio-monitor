# Release codename governance

The UN/CEFACT Portfolio Monitor uses tributary names from a reviewed repository-local pool as human-readable release codenames. Semantic version tags remain the authoritative release identity.

This repository is the **reference implementation pattern** for the cross-repository codename approach. It does not acquire release authority over any adopting repository.

## Provenance and state

- `config/release-codenames.txt` — reviewed eligible tributary names.
- `config/release-codename-policy.json` — machine-readable source provenance and selection rules.
- `releases/vX.Y.Z.yaml` — persisted release candidate/release identity, including the selected codename.
- `scripts/release_codenames.py` — validates the pool and all persisted release bindings and selects an unused future name.
- `scripts/release_from_manifest.py` — validates a merged release manifest before Actions creates the tag and GitHub Release.

The provenance source is Wikipedia's **Category: Tributaries of the Ganges**. Wikipedia is not fetched during release execution.

## Lifecycle

```text
coherent capability boundary
  ↓
semantic candidate version
  ↓
select unused codename from pinned pool
  ↓
persist version + codename in releases/vX.Y.Z.yaml
  ↓
review candidate manifest with implementation/evidence
  ↓
merge accepted manifest
  ↓
Actions validates repository-local codename policy
  ↓
annotated tag + GitHub Release
```

Preview an unused codename with:

```bash
python scripts/release_codenames.py select --version vX.Y.Z
```

The selected result becomes authoritative presentation metadata only after it is persisted in the reviewed release manifest.

## Invariants

1. The external Wikipedia source is provenance, never a publication dependency.
2. Pool entries are unique case-insensitively and source-attributed.
3. Every persisted release codename must be a member of the pinned pool.
4. Unused names are preferred while available; reuse is currently forbidden.
5. The same semantic version always resolves to the already-persisted codename.
6. Pool exhaustion fails closed unless policy is deliberately revised through review.
7. Release publication consumes the merged manifest and cannot choose a different codename at runtime.
8. Existing historical release manifests and GitHub Releases are not rewritten.

## Cross-repository adoption contract

Other repositories may implement the same guarantees with different file layouts and naming sources. The portable contract is the behavior—**pinned pool, provenance, persisted candidate identity, executable validation, idempotent publication**—not this repository's exact paths or its tributary theme.
