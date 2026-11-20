#!/usr/bin/env python3
"""Generate deterministic factor curves for clustering smoke tests."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", type=Path, required=True)
    args = parser.parse_args()
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2022-12-20", periods=24, freq="D")
    x = np.linspace(0.0, 2.0 * np.pi, len(dates))
    patterns = {
        "trend_a": 0.05 + 0.020 * np.sin(x),
        "trend_b": 0.04 + 0.018 * np.sin(x + 0.05),
        "wave_a": 0.03 + 0.020 * np.cos(x),
        "wave_b": 0.028 + 0.019 * np.cos(x + 0.07),
        "mix_a": 0.02 + 0.015 * np.sin(2.0 * x),
        "mix_b": 0.022 + 0.014 * np.sin(2.0 * x + 0.10),
    }
    rows = []
    for factor, values in patterns.items():
        for index, (date, value) in enumerate(zip(dates, values)):
            rows.append(
                {
                    "date": date.date().isoformat(),
                    "factor": factor,
                    "ic": float(value),
                    "layer_spread": float(value * 1.7 + 0.002 * np.cos(index)),
                    "layer_1": float(-value),
                    "layer_2": float(value),
                }
            )
    pd.DataFrame(rows).to_csv(args.output_file, index=False)
    print(args.output_file)


if __name__ == "__main__":
    main()
