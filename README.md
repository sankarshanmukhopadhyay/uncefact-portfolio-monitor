# UN/CEFACT Portfolio Monitor

Evidence-driven monitoring of the UN/CEFACT open-source portfolio: live project discovery, cross-project change impact, explicit dependency context, policy-matched findings, lifecycle history, and portfolio reporting.

**Published monitor:** https://sankarshanmukhopadhyay.github.io/uncefact-portfolio-monitor/

## v1.0 operating model

```text
UN/CEFACT GitLab discovery
        ↓
retained observation comparison
        ↓
observed structural change
        ↓
declared internal relationships
        ↓
direct review obligations
        ↓
declared evidence policies
        ↓
policy-matched findings
        ↓
persistent active/resolved lifecycle
        ↓
weekly portfolio assurance report
```

Declared external standards dependencies are published alongside this chain as review context. v1.0 does not claim automated external-change detection.

## Design principles

1. **Evidence before scores.** Findings must point to inspectable evidence.
2. **Portfolio coherence over activity volume.** A green repository can still create a cross-project review obligation.
3. **Declarations remain declarations.** Relationships, finding policies, and external dependencies are reviewed governance inputs, not inferred facts.
4. **Provider neutrality.** CI, repository inspection, specification checks, RAHP, and future analyzers may contribute evidence; none is the universal source of truth.
5. **Human review for material inference.** The monitor does not silently convert change into incompatibility or trust conclusions.
6. **History is retained.** Findings can resolve without disappearing from the evidence lifecycle.

## Evidence contract

The stable v1 evidence layers and invariants are defined in [docs/EVIDENCE-CONTRACT.md](docs/EVIDENCE-CONTRACT.md).

The core machine-readable outputs are:

- `portfolio.json` — discovered portfolio inventory;
- `changes.json` — structural/activity comparison with the previous observation;
- `relationships.json` — declared internal portfolio relationships;
- `impacts.json` — direct review obligations;
- `findings.json` — policy-matched current findings;
- `findings-lifecycle.json` — retained active/resolved lifecycle;
- `external-dependencies.json` — declared external standards/protocol context;
- `weekly-report.md` — evidence-linked human-readable portfolio report.

A finding is a policy-matched evidence condition requiring tracked disposition. It is **not automatically an incompatibility conclusion, assurance failure, or trust decision**.

## Operator guide

See [docs/OPERATIONS.md](docs/OPERATIONS.md) for the complete run sequence, interpretation order, failure handling, release operation, and v1 limitations.

The scheduled workflow runs weekly and is also manually dispatchable. A local run requires Python 3.11+.

## Development and release flow

Substantive work follows:

`Issue → branch → pull request → CI → merge → release manifest → GitHub Actions release`

Release manifests are validated by CI. The release workflow creates tags and GitHub Releases after a valid new manifest reaches `main`.

## v1.0 limitations and extension points

v1.0 intentionally does **not** automatically score repository health, poll external standards for semantic changes, infer normative compatibility, perform recursive multi-hop impact propagation, or make relying-party trust decisions.

Future evidence providers may add role-aware repository checks, semantic/schema drift analysis, external-source change polling, and additional specification pressure tests, but they must preserve the v1 evidence boundaries.

## Release history

- **v0.1.0 — Tamsa** — foundation, CI, release automation.
- **v0.2.0 — Ghaghara** — dynamic GitLab portfolio discovery.
- **v0.3.0 — Varuna** — published GitHub Pages portfolio.
- **v0.4.0 — Kosi** — retained baseline and change detection.
- **v0.5.0 — Ramganga** — declared internal relationship graph.
- **v0.6.0 — Gandaki** — direct dependency-aware review obligations.
- **v0.7.0 — Gomti** — deterministic evidence-policy findings.
- **v0.8.0 — Nandakini** — declared external standards dependency inventory.
- **v0.9.0 — Yamuna** — findings lifecycle and weekly report.
- **v1.0.0 — Alaknanda** — stable evidence contract and operational release baseline.

Release codenames are randomly selected from the configured pool derived from Wikipedia's `Category:Tributaries of the Ganges` and are permanently recorded in release manifests.

## License

Repository-authored code, documentation, configuration, and generated monitor outputs are licensed under the [Apache License 2.0](LICENSE).

Material observed, quoted, linked, or retrieved from UN/CEFACT repositories and other external sources is **not relicensed by this repository**. Such material remains subject to the terms, notices, and authority of its original source.
