"""Build a QuantSkills ranked-factor-set 1.0.0 envelope."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from pathlib import Path
from typing import Any


FIELDS = {
    "set_id": {"type": "string", "nullable": False},
    "as_of": {"type": "string", "nullable": False, "format": "date-time"},
    "factor_id": {"type": "string", "nullable": False},
    "rank": {"type": "integer", "nullable": False, "unit": "rank"},
    "score": {"type": "number", "nullable": False, "unit": "score"},
    "selection_method": {"type": "string", "nullable": False},
    "evaluation_ref": {"type": "string", "nullable": False},
    "lineage": {"type": "object", "nullable": False},
}


def _rfc3339(value: str) -> str:
    text = str(value).strip()
    if "T" not in text:
        text = f"{text}T00:00:00Z"
    elif text.endswith("+00:00"):
        text = text[:-6] + "Z"
    if not (text.endswith("Z") or _has_timezone(text)):
        raise ValueError(f"Timestamp must include an RFC3339 timezone: {value}")
    return text


def _has_timezone(value: str) -> bool:
    if len(value) < 6:
        return False
    suffix = value[-6:]
    return suffix[0] in "+-" and suffix[3] == ":" and suffix[1:3].isdigit() and suffix[4:].isdigit()


def _generated_at() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def build_ranked_factor_set(
    selected: list[dict[str, Any]],
    *,
    dataset_id: str,
    producer: str,
    selection_method: str,
    source_profile: str,
    source_path: Path,
    source_sha256: str,
    as_of: str,
    score_key: str,
    evaluation_ref: str,
    evidence_ref: str,
    checks: list[str],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    if not selected:
        raise ValueError("A ranked-factor-set requires at least one selected factor")
    digest = source_sha256.removeprefix("sha256:")
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise ValueError("source_sha256 must be a lowercase SHA256 digest")
    ranked: list[tuple[str, float]] = []
    for item in selected:
        factor_id = str(item.get("factor", item.get("name", ""))).strip()
        if not factor_id:
            raise ValueError(f"Selected item has no factor identifier: {item}")
        score = float(item[score_key])
        if not math.isfinite(score):
            raise ValueError(f"Selected factor has a non-finite score: {factor_id}")
        ranked.append((factor_id, score))
    ranked.sort(key=lambda item: (-item[1], item[0]))
    timestamp = _rfc3339(as_of)
    source_ref = source_path.resolve().as_uri()
    source = {
        "profile": source_profile,
        "version": "1.0.0",
        "artifact_ref": source_ref,
        "sha256": f"sha256:{digest}",
    }
    records = [
        {
            "set_id": dataset_id,
            "as_of": timestamp,
            "factor_id": factor_id,
            "rank": rank,
            "score": score,
            "selection_method": selection_method,
            "evaluation_ref": evaluation_ref,
            "lineage": {"sources": [source], "evidence_refs": [evidence_ref]},
        }
        for rank, (factor_id, score) in enumerate(ranked, start=1)
    ]
    return {
        "$contract": {
            "envelope": "quantskills-envelope",
            "envelope_version": "1.0.0",
            "profile": "ranked-factor-set",
            "profile_version": "1.0.0",
        },
        "meta": {
            "dataset_id": dataset_id,
            "producer": producer,
            "generated_at": _generated_at(),
            "as_of": timestamp,
            "timezone": "UTC",
            "provenance": [
                {
                    "provider": "user-provided-local-data",
                    "dataset": source_path.name,
                    "raw_ref": source_ref,
                    "raw_sha256": f"sha256:{digest}",
                }
            ],
        },
        "schema": {"primary_key": ["set_id", "factor_id"], "fields": FIELDS},
        "payload": {
            "native": {"provider": "user-provided-local-data", "raw_ref": source_ref},
            "records": records,
        },
        "quality": {
            "status": "warning" if warnings else "pass",
            "checks": checks,
            "warnings": warnings or [],
        },
    }
