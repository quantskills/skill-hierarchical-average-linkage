#!/usr/bin/env python3
"""Run train-only correlation-distance average-linkage clustering."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from factor_curve_utils import load_train_curves, representative_rows, sha256_file, write_common_outputs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curves", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--train-start", required=True)
    parser.add_argument("--train-end", required=True)
    parser.add_argument("--n-clusters", type=int, default=160)
    parser.add_argument("--impute-missing", action="store_true")
    args = parser.parse_args()
    names, matrix, records, curve_meta = load_train_curves(args.curves, args.train_start, args.train_end, args.impute_missing)
    if args.n_clusters < 1 or args.n_clusters > len(names):
        raise ValueError(f"n_clusters must be between 1 and {len(names)}")
    train_days = len(curve_meta["train_dates"])
    ic = matrix[:, :train_days]
    spread = matrix[:, train_days : 2 * train_days]
    def row_corr(values: np.ndarray) -> np.ndarray:
        centered = values - values.mean(axis=1, keepdims=True)
        scale = np.linalg.norm(centered, axis=1, keepdims=True)
        normalized = np.divide(centered, scale, out=np.zeros_like(centered), where=scale > 1e-12)
        return np.clip(normalized @ normalized.T, -1.0, 1.0)
    corr = 0.5 * (row_corr(ic) + row_corr(spread))
    distance = 1.0 - corr
    np.fill_diagonal(distance, 0.0)
    tree = linkage(squareform(distance, checks=False), method="average")
    labels = fcluster(tree, t=args.n_clusters, criterion="maxclust")
    if len(set(labels)) != args.n_clusters:
        raise ValueError(f"average-linkage produced {len(set(labels))} clusters, expected {args.n_clusters}")
    selected, assignments = representative_rows(names, records, labels, distance)
    output = args.output_dir
    receipt = {"input": str(args.curves.resolve()), "input_sha256": sha256_file(args.curves.resolve()), "producer": "skill-hierarchical-average-linkage", "method": "average_linkage", "distance": "correlation_distance", "train_range": [args.train_start, args.train_end], "n_clusters_requested": args.n_clusters, "n_clusters_observed": int(len(set(labels))), "factor_count": len(names), "no_valid_or_oos_used": True}
    metadata = {"method": "average_linkage", "distance_matrix": "train-only correlation distance", "representative_rule": "0.80 robust quality + 0.20 within-cluster centrality", "curve_audit": curve_meta}
    write_common_outputs(output, selected, assignments, metadata, receipt)
    np.save(output / "correlation_distance.npy", distance)
    print(json.dumps({"factors": len(names), "clusters": int(len(set(labels))), "selected": len(selected)}))


if __name__ == "__main__":
    main()
