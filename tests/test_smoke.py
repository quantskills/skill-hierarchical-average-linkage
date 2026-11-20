from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_average_linkage.py"


def prepare(tmp_path: Path) -> Path:
    curves = tmp_path / "curves.csv"
    subprocess.run(
        [sys.executable, str(ROOT / "examples/generate_smoke_curves.py"), "--output-file", str(curves)],
        check=True,
        text=True,
        capture_output=True,
    )
    return curves


def run_cli(tmp_path: Path, output_name: str) -> Path:
    curves = prepare(tmp_path)
    output = tmp_path / output_name
    command = [
        sys.executable,
        str(SCRIPT),
        "--curves",
        str(curves),
        "--output-dir",
        str(output),
        "--train-start",
        "2022-12-20",
        "--train-end",
        "2023-01-12",
        "--n-clusters",
        "3",
    ]
    result = subprocess.run(command, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    return output


def test_smoke_is_deterministic_and_emits_ranked_envelope(tmp_path: Path) -> None:
    first = run_cli(tmp_path / "first", "out")
    second = run_cli(tmp_path / "second", "out")
    first_output = first / "."
    second_output = second / "."
    envelope_a = json.loads((first_output / "ranked_factor_set.json").read_text(encoding="utf-8"))
    envelope_b = json.loads((second_output / "ranked_factor_set.json").read_text(encoding="utf-8"))
    assert envelope_a["$contract"]["profile"] == "ranked-factor-set"
    stable_a = [
        {key: value for key, value in record.items() if key != "lineage"}
        for record in envelope_a["payload"]["records"]
    ]
    stable_b = [
        {key: value for key, value in record.items() if key != "lineage"}
        for record in envelope_b["payload"]["records"]
    ]
    assert stable_a == stable_b
    sha_a = envelope_a["payload"]["records"][0]["lineage"]["sources"][0]["sha256"]
    sha_b = envelope_b["payload"]["records"][0]["lineage"]["sources"][0]["sha256"]
    assert sha_a == sha_b
    assignments_a = pd.read_csv(first_output / "cluster_assignments.csv")
    assignments_b = pd.read_csv(second_output / "cluster_assignments.csv")
    pd.testing.assert_frame_equal(assignments_a, assignments_b)
    assert assignments_a["representative"].sum() == 3
