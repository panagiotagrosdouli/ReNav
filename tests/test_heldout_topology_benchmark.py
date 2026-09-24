from __future__ import annotations

import csv
from pathlib import Path
from runpy import run_path


run = run_path(
    str(
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "run_heldout_topology_benchmark.py"
    )
)["run"]


def test_heldout_topology_runner_retains_controls_and_paired_outcomes(tmp_path):
    rejected, completed = run(40, 20261024, tmp_path)

    assert completed == 40
    assert rejected >= 0
    with (tmp_path / "heldout_topology_trials.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 40
    assert {row["regime"] for row in rows} == {
        "critical",
        "harmless",
        "no_effect",
    }
    assert all(int(row["activated_geometric"]) == 1 for row in rows)
    for row in rows:
        if row["regime"] in {"no_effect", "harmless"}:
            for method in (
                "geometric",
                "static_marginal",
                "history_weight_4",
                "hard_return_0.8",
            ):
                assert float(row[f"exact_success_{method}"]) == 1.0

    with (tmp_path / "heldout_topology_summary.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        summary = list(csv.DictReader(stream))
    assert len(summary) == 16
    assert {row["regime"] for row in summary} == {
        "all",
        "critical",
        "harmless",
        "no_effect",
    }
