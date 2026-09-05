# Public repository baseline

This record captures controls reviewed under issue #35. It is repository assurance evidence, not external certification.

| Control | State | Evidence | Residual risk |
|---|---|---|---|
| Purpose/adoption/authority boundary | PASS | `README.md`, `docs/`, config/release surfaces | Upstream UN/CEFACT repositories remain authoritative. |
| Licensing | PASS | top-level `LICENSE` (Apache-2.0) and README licensing boundary | Externally sourced UN/CEFACT and other third-party material is explicitly excluded from relicensing and remains subject to source terms. |
| Security reporting | PASS | `SECURITY.md` | Hosted private-reporting enablement remains platform evidence. |
| Contribution/community/support | PASS | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md`, issue/PR templates | None identified. |
| Dependency updates | PASS | `.github/dependabot.yml` | Hosted Dependabot enablement remains platform evidence. |
| Default-branch protection | EVIDENCE REQUIRED | rulesets API returned no active ruleset on 2026-09-05 | Tracked separately as a repository-setting control. |
| Tests/evidence/publication | PASS / bounded | `tests/`, workflows, generated reports/releases | Workflow green is not upstream decision evidence. |
| Authority boundary | PASS | README/docs methodology | Missing/inactive upstream evidence must not be interpreted as a decision or PASS. |

## Completion boundary

Repository-owned baseline and licensing gaps are closed through governed PRs. Default-branch protection remains an explicit bounded residual because it requires GitHub repository-administration authority rather than code-only inference.
