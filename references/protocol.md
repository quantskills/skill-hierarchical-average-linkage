# Protocol

## Temporal boundary

- Declare non-overlapping Train, Valid, and OOS or holdout ranges before computation.
- Estimate preprocessing, structure, parameters, representatives, and model state only from the ranges allowed by the declared workflow.
- Freeze the selection or model decision before sealed OOS or holdout access.

## Input audit

- Validate schema, primary keys, factor identifiers, date ordering, universe membership, finite values, and duplicate handling.
- Record the complete candidate manifest and SHA256 receipts before any filtering.
- Reject ambiguous time semantics rather than guessing whether a timestamp is an observation, availability, signal, or execution time.

## Method receipt

- Build a finite symmetric Train-only distance matrix with a zero diagonal.
- Freeze the cluster-count or cut-height rule before selecting real-factor representatives.
- Persist every resolved parameter, seed, software version, warning, failure, and deterministic tie-break.

## Output audit

- Emit the registered `ranked-factor-set` profile in a `quantskills-envelope` version `1.0.0`.
- Preserve local diagnostic artifacts needed to reproduce candidate outcomes and verify counts.
- Every candidate must have an explicit selected, excluded, outlier, or failed outcome where applicable.
- Hash the resolved configuration, main assignments or predictions, and final output envelope.

## Promotion gate

Keep `validation_level: listed` until the repository contains install instructions, dependencies, runnable code, example input/output, and a passing smoke test. Promotion to `verified` additionally requires data provenance, no-lookahead evidence, research evidence, and risk disclosure.
