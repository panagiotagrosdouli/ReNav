from __future__ import annotations

import csv

from experiments.run_mechanistic_sweep import run


def test_mechanistic_sweep_records_paired_exact_and_empirical_results(tmp_path):
    output = tmp_path / "sweep.csv"
    run(trials=5000, seed=17, output=output)

    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    assert len(rows) == 42
    by_key = {
        (float(row["closure_probability"]), row["planner"]): row
        for row in rows
    }
    for probability in (0.1, 0.2, 0.4, 0.6, 0.8, 0.9):
        direct = by_key[(probability, "geometric")]
        assert int(direct["path_length"]) == 3
        assert int(direct["activated_hazards"]) == 0
        assert abs(
            float(direct["empirical_success_rate"])
            - float(direct["exact_success_probability"])
        ) < 0.03

        safe = by_key[(probability, "hard_return_0.8")]
        assert float(safe["empirical_success_rate"]) == 1.0
        assert float(safe["exact_success_probability"]) == 1.0
