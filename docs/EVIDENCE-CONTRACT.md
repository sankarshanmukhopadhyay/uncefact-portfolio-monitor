# v1 Evidence Contract

UN/CEFACT Portfolio Monitor v1.0 is an evidence and review system. It does not make autonomous trust decisions and does not convert repository activity into assurance conclusions.

## Evidence layers

The v1 contract is intentionally layered. Each layer must preserve the provenance of the layer beneath it.

1. **Portfolio inventory — `portfolio.json`**  
   Observable public GitLab project metadata discovered from the configured UN/CEFACT namespace.
2. **Observed change — `changes.json`**  
   Deterministic comparison with the preceding retained portfolio observation. Structural change and activity-only advancement are separate.
3. **Declared internal relationships — `relationships.json`**  
   Reviewed configuration describing internal dependency/profile relationships. These are declarations, not inferred trust facts.
4. **Impact candidates — `impacts.json`**  
   Direct review obligations derived when observed structural change occurs in a declared dependency. An obligation is not a failure.
5. **Policy-matched findings — `findings.json`**  
   Stable findings created only when an explicit evidence policy matches a review obligation. Severity is declared policy, not an aggregate score.
6. **Finding lifecycle — `findings-lifecycle.json`**  
   Persistent active/resolved state keyed by stable finding ID, preserving first/last observation and history.
7. **External dependency context — `external-dependencies.json`**  
   Reviewed declarations of external specifications/protocols that may require attention. v1 does not claim automated external change detection.
8. **Portfolio report — `weekly-report.md` / `weekly-report.html`**  
   Human-readable synthesis generated from the evidence layers above.

## Invariants

- Observable evidence and declared governance inputs remain distinguishable.
- Activity-only advancement cannot become a material finding by itself.
- `related-to` relationships do not create dependency review obligations.
- A review obligation is not an incompatibility conclusion.
- A finding is not automatically an assurance failure or trust decision.
- Resolved findings remain retained as history.
- No aggregate portfolio score is authoritative in v1.
- Every generated conclusion must be traceable to inspectable evidence and/or reviewed configuration.

## Stable extension points

Future releases may add role-aware repository-health checks, semantic/schema drift analysis, external-source change polling, additional evidence providers, and multi-hop impact analysis. Such providers must enter through explicit evidence contracts and must not silently weaken the invariants above.
