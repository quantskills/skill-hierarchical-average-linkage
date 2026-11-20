# Hierarchical Average Linkage

[Simplified Chinese](README.md) | English

`skill-hierarchical-average-linkage` is an independent QuantSkills Community Project. Select representative factors with train-only average-linkage agglomerative clustering.

## Scope

- Use when an agent needs balanced hierarchical factor clustering based on pairwise average distances.
- Do not use this skill when complete-linkage, Ward geometry, or a density-based outlier model is required.
- Valid and OOS or holdout data must follow the freeze and leakage rules in `SKILL.md`.

## Research disclosure

- Data source: use only public data, user-provided local data, or material the user has the right to use, and record provenance.
- Assumptions: state time semantics, universe construction, factor direction, missing-value handling, and label availability.
- Parameters: persist thresholds, seeds, split boundaries, preprocessing, and method settings.
- Limitations: disclose sample dependence, instability, approximations, missingness, and untested regimes.
- Risk boundary: all artifacts are for quantitative research and education only.

## Current status

- Catalog: `02.factor-selection`
- Workflow: `factor-screening`
- Validation: `listed`
- License: `GPL-3.0-only`

The repository currently defines the method, interfaces, and research boundaries but does not contain a runnable implementation. Do not claim `runnable` status until dependencies, a CLI, a synthetic example, expected outputs, and tests are present.

## Entrypoints

- `SKILL.md`: canonical Skill instructions and QuantSkills frontmatter.
- `references/protocol.md`: temporal boundary, input audit, and output acceptance contract.
- `references/source_boundary.md`: data, licensing, privacy, and research-risk boundary.

## Disclaimer

This project is for quantitative research and education only. It is not investment advice, a return guarantee, or production approval.
