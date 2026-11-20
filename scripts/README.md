# Scripts

This project is currently a QuantSkills `listed` method contract. No runnable Hierarchical Average Linkage implementation is included yet.

Before changing `validation_level` to `runnable`, add:

- a deterministic command-line entrypoint;
- explicit dependency and Python-version declarations;
- schema validation and fail-closed temporal-boundary checks;
- a small public or synthetic example with expected outputs;
- tests for determinism, leakage boundaries, failure handling, and output contracts.

Do not add private datasets, credentials, generated signals, trained weights, caches, or temporary run logs.
