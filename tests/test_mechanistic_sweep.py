from __future__ import annotations

import csv
from pathlib import Path
from runpy import run_path

run = run_path(
    str(Path(__file__).resolve().parents[1] / "experiments" / "run_mechanistic_sweep.py")
)["run"]


def test_mechanistic_sweep_records_paired_exact_and_empirical_results(tmp_path):
    output = tmp_path / "sweep.csv"
    run(trials=5000, seed=17, output=output)

    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 42
    with output.with_name("sweep_trials.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        raw_rows = list(csv.DictReader(stream))
    assert len(raw_rows) == 6 * 5000
    assert len(raw_rows[0]) == 11
    by_key = {
        (float(row["closure_probability"]), row["planner"]): row
        for row in rows
    }
    for probability in (0.1, 0.2, 0.4, 0.6, 0.8, 0.9):
        direct = by_key[(probability, "geometric")]
        assert int(direct["path_length"]) == 3
        assert direct["activated_hazards"] == "0"
        assert abs(
            float(direct["empirical_success_rate"])
            - float(direct["exact_success_probability"])
        ) < 0.03

        hard = by_key[(probability, "hard_return_0.8")]
        expected_length = 3 if probability <= 0.2 else 5
        expected_success = 1.0 - probability if probability <= 0.2 else 1.0
        assert int(hard["path_length"]) == expected_length
        assert float(hard["exact_success_probability"]) == expected_success
        assert abs(
            float(hard["empirical_success_rate"]) - expected_success
        ) < 0.03
        expected_paired_delta = probability if probability > 0.2 else 0.0
        assert abs(
            float(hard["paired_delta_vs_geometric"]) - expected_paired_delta
        ) < 0.03
