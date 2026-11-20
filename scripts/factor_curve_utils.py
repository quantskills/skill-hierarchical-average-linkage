"""Shared train-only curve loading and representative scoring utilities."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from ranked_factor_output import build_ranked_factor_set


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as handle:
            while chunk := handle.read(8 * 1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()
    if path.is_dir():
        files = sorted(item for item in path.rglob("*") if item.is_file())
        if not files:
            raise ValueError(f"Cannot hash empty directory: {path}")
        for item in files:
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            with item.open("rb") as handle:
                while chunk := handle.read(8 * 1024 * 1024):
                    digest.update(chunk)
        return digest.hexdigest()
    raise FileNotFoundError(path)


def read_curve_table(path: Path) -> pd.DataFrame:
    if path.is_dir() or path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _column(frame: pd.DataFrame, options: tuple[str, ...]) -> str | None:
    names = {str(column).lower(): str(column) for column in frame.columns}
    return next((names[name] for name in options if name in names), None)


def _layer_columns(frame: pd.DataFrame) -> list[str]:
    columns = []
    for column in frame.columns:
        text = str(column).lower().replace(" ", "_")
        if text.startswith("layer_"):
            try:
                int(text.split("_")[-1])
                columns.append(str(column))
            except ValueError:
                pass
    return sorted(columns, key=lambda value: int(str(value).lower().replace(" ", "_").split("_")[-1]))


def _percentile(values: np.ndarray) -> np.ndarray:
    return (rankdata(values, method="average") - 1.0) / max(1.0, len(values) - 1.0)


def load_train_curves(path: Path, start: str, end: str, impute_missing: bool = False) -> tuple[list[str], np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    frame = read_curve_table(path)
    date_col = _column(frame, ("date", "trade_date", "datetime"))
    factor_col = _column(frame, ("factor", "factor_name", "factor_id", "name"))
    ic_col = _column(frame, ("ic", "daily_ic", "pearson_ic", "rank_ic"))
    spread_col = _column(frame, ("layer_spread", "spread", "layer_spread_mean"))
    if not date_col or not factor_col or not ic_col or not spread_col:
        raise ValueError("Curve table needs date, factor, ic and layer_spread columns")
    frame = frame.copy()
    frame["__date"] = pd.to_datetime(frame[date_col], errors="coerce").dt.normalize()
    frame = frame.loc[frame["__date"].between(pd.Timestamp(start), pd.Timestamp(end))].copy()
    frame["__factor"] = frame[factor_col].astype(str)
    layer_cols = _layer_columns(frame)
    dates = sorted(frame["__date"].dropna().unique())
    if not dates:
        raise ValueError("No curve rows in the declared Train range")
    names: list[str] = []
    vectors: list[np.ndarray] = []
    records: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []
    for name, group in frame.groupby("__factor", sort=True):
        if group["__date"].isna().any():
            rejected.append({"factor": name, "reason": "invalid_train_curve_date"})
            continue
        group = group.sort_values("__date")
        duplicate_dates = int(group.duplicated("__date").sum())
        if duplicate_dates:
            rejected.append({"factor": name, "reason": f"duplicate_train_curve_date:{duplicate_dates}"})
            continue
        group = group.set_index("__date")
        columns = [ic_col, spread_col, *layer_cols]
        series = group.reindex(dates)[columns].apply(pd.to_numeric, errors="coerce")
        missing = int(series.isna().sum().sum())
        if missing and not impute_missing:
            rejected.append({"factor": name, "reason": f"missing_train_curve_values:{missing}"})
            continue
        if missing:
            series = series.fillna(series.median()).fillna(0.0)
        values = series.to_numpy(dtype=float).copy()
        if not np.isfinite(values).all():
            rejected.append({"factor": name, "reason": "non_finite_train_curve_values"})
            continue
        sign = -1.0 if np.nanmean(values[:, 0]) < 0 else 1.0
        values[:, :2] *= sign
        if sign < 0 and layer_cols:
            values[:, 2:] = values[:, 2:][:, ::-1]
        names.append(name)
        vectors.append(np.concatenate([values[:, 0], values[:, 1], values[:, 2:].reshape(-1)]))
        records.append({"factor": name, "orientation": int(sign), "missing_values": missing, "_ic": values[:, 0], "_spread": values[:, 1], "_layers": values[:, 2:]})
    if len(names) < 2:
        raise ValueError("Fewer than two usable factors remain after curve audit")
    matrix = np.vstack(vectors)
    dates_array = pd.to_datetime(dates).year.to_numpy()
    annual_icir, annual_spread_sharpe, monotonicity = [], [], []
    for year in np.unique(dates_array):
        mask = dates_array == year
        ic = np.stack([item["_ic"] for item in records])[:, mask]
        spread = np.stack([item["_spread"] for item in records])[:, mask]
        ic_std = ic.std(axis=1, ddof=1) if mask.sum() > 1 else np.zeros(len(records))
        spread_std = spread.std(axis=1, ddof=1) if mask.sum() > 1 else np.zeros(len(records))
        annual_icir.append(np.divide(ic.mean(axis=1), ic_std, out=np.zeros(len(records)), where=ic_std > 1e-12))
        annual_spread_sharpe.append(np.divide(spread.mean(axis=1), spread_std, out=np.zeros(len(records)), where=spread_std > 1e-12) * np.sqrt(242.0))
    for item in records:
        layers = item["_layers"]
        if layers.shape[1]:
            monotonicity.append(float(np.nan_to_num(spearmanr(np.arange(layers.shape[1]), layers.mean(axis=0)).statistic, nan=0.0)))
        else:
            monotonicity.append(0.0)
    median_icir = np.median(np.stack(annual_icir), axis=0)
    worst_icir = np.min(np.stack(annual_icir), axis=0)
    median_spread = np.median(np.stack(annual_spread_sharpe), axis=0)
    worst_spread = np.min(np.stack(annual_spread_sharpe), axis=0)
    quality = 0.35 * _percentile(median_icir) + 0.20 * _percentile(worst_icir) + 0.25 * _percentile(median_spread) + 0.10 * _percentile(worst_spread) + 0.10 * _percentile(np.asarray(monotonicity))
    for item, score in zip(records, quality):
        item["robust_quality"] = float(score)
        item.pop("_ic", None); item.pop("_spread", None); item.pop("_layers", None)
    metadata = {"train_dates": [str(pd.Timestamp(date).date()) for date in dates], "layer_columns": layer_cols, "rejected": rejected, "impute_missing": impute_missing}
    return names, matrix, records, metadata


def representative_rows(names: list[str], records: list[dict[str, Any]], labels: np.ndarray, distances: np.ndarray, embeddings: np.ndarray | None = None) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    quality = {item["factor"]: float(item["robust_quality"]) for item in records}
    rows: list[dict[str, Any]] = []
    selected: list[dict[str, Any]] = []
    for cluster in sorted(np.unique(labels)):
        indices = np.flatnonzero(labels == cluster)
        if embeddings is not None:
            center = embeddings[indices].mean(axis=0)
            centrality_raw = 1.0 / (1.0 + np.linalg.norm(embeddings[indices] - center, axis=1))
        else:
            centrality_raw = 1.0 / (1.0 + distances[np.ix_(indices, indices)].mean(axis=1))
        centrality = pd.Series(centrality_raw).rank(method="average", pct=True).to_numpy()
        scores = np.array([0.8 * quality[names[i]] + 0.2 * centrality[j] for j, i in enumerate(indices)])
        winner = int(indices[int(np.argmax(scores))])
        for j, index in enumerate(indices):
            row = {"factor": names[index], "cluster": int(cluster), "cluster_size": int(len(indices)), "robust_quality": quality[names[index]], "centrality": float(centrality[j]), "selection_score": float(scores[j]), "representative": bool(index == winner)}
            rows.append(row)
            if index == winner:
                selected.append(row)
    return selected, pd.DataFrame(rows).sort_values(["cluster", "representative", "selection_score"], ascending=[True, False, False])


def write_common_outputs(output: Path, selected: list[dict[str, Any]], assignments: pd.DataFrame, metadata: dict[str, Any], receipt: dict[str, Any]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "selected_factors.json").write_text(json.dumps({"schema_version": "1.0.0", "selected_factors": selected, "train_only": True}, indent=2, ensure_ascii=False), encoding="utf-8")
    assignments.to_csv(output / "cluster_assignments.csv", index=False)
    (output / "method_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    (output / "audit_receipt.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
    envelope = build_ranked_factor_set(
        selected,
        dataset_id=f"{receipt['method']}-k{receipt['n_clusters_requested']}-{receipt['train_range'][1]}",
        producer=receipt["producer"],
        selection_method=receipt["method"],
        source_profile="factor-curve-table",
        source_path=Path(receipt["input"]),
        source_sha256=receipt["input_sha256"],
        as_of=receipt["train_range"][1],
        score_key="selection_score",
        evaluation_ref="artifact://local/method_metadata.json",
        evidence_ref="artifact://local/audit_receipt.json",
        checks=["train-only-input", "finite-curves", "cluster-count", "real-factor-representatives"],
        warnings=[f"{len(metadata['curve_audit'].get('rejected', []))} factors rejected"]
        if metadata["curve_audit"].get("rejected")
        else [],
    )
    (output / "ranked_factor_set.json").write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8"
    )
