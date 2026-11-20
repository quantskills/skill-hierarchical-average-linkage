---
name: skill-hierarchical-average-linkage
description: Select representative factors with train-only average-linkage agglomerative clustering. Use when an
  agent needs balanced hierarchical factor clustering based on pairwise average distances. Do not use this skill
  when complete-linkage, Ward geometry, or a density-based outlier model is required.
quantSkills:
  schema_version: 2.0.0
  organization: quantskills
  organization_url: https://github.com/quantskills
  repository: skill-hierarchical-average-linkage
  repository_url: https://github.com/quantskills/skill-hierarchical-average-linkage
  project_type: skill
  license: GPL-3.0-only
  maintainer: X-Tech-group
  collection: factor-research
  catalog:
    category: '02'
    subcategory: 02.factor-selection
  workflow:
    primary_stage: factor-screening
    workflow_stages:
    - factor-screening
    - evaluation
  tags:
  - factor-selection
  - hierarchical-clustering
  - agglomerative
  - average-linkage
  requires: []
  summary_zh: 使用训练期 IC 与 layer-spread 曲线执行 Average-linkage 凝聚性层次聚类。
  summary_en: Train-only average-linkage agglomerative clustering for representative factor selection.
  status: active
  validation_level: runnable
  maintainer_type: community
  platforms:
  - cursor
  - claude-code
  - codex
  - hermes
  - openclaw
  interface:
    mode: hybrid
    envelope:
      name: quantskills-envelope
      version: 1.0.0
    inputs: []
    outputs:
    - profile: ranked-factor-set
      version: 1.0.0
    adapters: []
---
# Hierarchical Average Linkage

Select representative factors with train-only average-linkage agglomerative clustering.

## Use This Skill When

- Use it when an agent needs balanced hierarchical factor clustering based on pairwise average distances.
- Do not use this skill when complete-linkage, Ward geometry, or a density-based outlier model is required.
- Treat all outputs as quantitative research artifacts, not investment advice or production approval.

## Inputs

- A schema-compatible factor panel with stable factor identifiers.
- Optional market bars or labels when the declared factor-curve construction needs them.
- Explicit Train/Valid/OOS boundaries, universe rules, method parameters, and output directory.

Read `references/protocol.md` before preparing inputs or interpreting outputs.

## Method Decisions

- Build a finite symmetric Train-only distance matrix with a zero diagonal.
- Freeze the cluster-count or cut-height rule before selecting real-factor representatives.

## Workflow

1. Validate the factor panel, candidate manifest, keys, finite values, and non-overlapping time boundaries.
2. Freeze candidate identifiers, parameters, preprocessing, seed, and failure policy before computation.
3. Fit preprocessing, similarities, distances, embeddings, or graphs on Train only.
4. Run the declared method and record convergence, outliers, exclusions, and assignments.
5. Select real candidate representatives with a deterministic score and tie-break.
6. Freeze the ranked factor set before any OOS access.
7. Use Valid only for a predeclared comparison; keep OOS diagnostic and non-confirmatory.

## Output Contract

- Emit a QuantSkills `quantskills-envelope` with profile `ranked-factor-set` version `1.0.0`.
- Preserve a resolved configuration, candidate outcomes, method diagnostics, date boundaries, seed, and input/output SHA256 receipts.
- Never silently drop failed factors, non-finite distances, outliers, disconnected nodes, or non-converged runs.

## Research Invariants

- Train may determine preprocessing, structure, clustering, and representatives.
- Valid may be used only by a comparison or selection rule declared before it is read.
- OOS data must not influence construction, tuning, selection, stopping, or method choice.
- Every selected representative must be a traceable member of the original candidate pool.
- Record data provenance, assumptions, limitations, and all deviations from the declared protocol.

## Research Disclosure

- Data source: use only public data, user-provided local data, or material the user has the right to use; record provenance.
- Assumptions: document time semantics, universe construction, factor direction, missing-value handling, and label availability.
- Parameters: persist every threshold, seed, split boundary, preprocessing option, and method setting.
- Limitations: disclose sample dependence, instability, approximation, missingness, and any untested operating regime.
- Risk boundary: outputs are research evidence only and are not investment advice, promised returns, or production approval.

## Runnable Implementation

Install dependencies with `python -m pip install -r requirements.txt` and run:

```bash
python scripts/run_average_linkage.py \
  --curves /path/to/train_curves.csv \
  --output-dir /path/to/output \
  --train-start 2020-01-01 \
  --train-end 2023-12-31 \
  --n-clusters 20
```

The CLI writes `ranked_factor_set.json` using the registered `ranked-factor-set` 1.0.0 profile together with method-specific audit artifacts. Generate synthetic smoke inputs from `examples/` and run `python -m pytest -q` before release.

## Optional qsh-form

```json qsh-form
{"version":1,"task":{"placeholder":"Describe the Hierarchical Average Linkage research task and attach the required local inputs","required":true},"fields":[],"prompt_template":"Handle this task: {{task}}. Attachments: {{#attachments}}"}
```

## References

- `references/protocol.md`: input, temporal, output, and validation contract.
- `references/source_boundary.md`: source, licensing, privacy, and research boundaries.
