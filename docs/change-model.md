# Portfolio change model

The monitor compares normalized GitLab observations by stable project ID.

## Structural change

The following fields are treated as structural metadata: project path, default branch, visibility, archived state, description, and topics. A change record preserves before/after values.

## Activity advancement

`last_activity_at` movement is recorded separately. Activity is evidence that a repository changed, but it is not by itself a structural change or assurance finding.

## First observation

When no previous baseline is available, the current portfolio establishes the baseline. Projects are **not** reported as newly added merely because the monitor has seen them for the first time.

## Assurance boundary

Change data is observational evidence only. Relationship-aware review obligations and assurance findings are separate downstream layers.
