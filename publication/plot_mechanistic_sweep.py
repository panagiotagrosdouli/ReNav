"""Generate the publication figure for the retained canonical sweep CSV."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

METHODS = {
    "geometric": ("geometric", "#4C78A8", "o"),
    "hard_return_0.8": ("hard return, threshold 0.8", "#F58518", "s"),
    "history_weight_4": ("history A*, weight 4", "#54A24B", "^"),
}


def plot(input_path: Path, output_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams["svg.fonttype"] = "none"
    figure, axis = plt.subplots(figsize=(6.4, 4.2), layout="constrained")
    for key, (label, color, marker) in METHODS.items():
        selected = sorted(
            (row for row in rows if row["planner"] == key),
            key=lambda row: float(row["closure_probability"]),
        )
        x = [float(row["closure_probability"]) for row in selected]
        y = [float(row["empirical_success_rate"]) for row in selected]
        lower = [float(row["wilson_95_low"]) for row in selected]
        upper = [float(row["wilson_95_high"]) for row in selected]
        axis.errorbar(
            x,
            y,
            yerr=[
                [max(0.0, estimate - low) for estimate, low in zip(y, lower, strict=True)],
                [max(0.0, high - estimate) for estimate, high in zip(y, upper, strict=True)],
            ],
            label=label,
            color=color,
            marker=marker,
            linewidth=2,
            capsize=3,
        )

    axis.set(
        xlabel="Closure probability",
        ylabel="Mission-and-return success",
        xlim=(0.05, 0.95),
        ylim=(0, 1.03),
        xticks=sorted({float(row["closure_probability"]) for row in rows}),
    )
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False, loc="lower left")
    figure.text(
        0.5,
        -0.015,
        "One constructed 4×3 grid; 10,000 paired Bernoulli trials per probability. "
        "Not a map-generalization result.",
        ha="center",
        fontsize=8,
    )
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/mechanistic_sweep.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("publication/figures/mechanistic_sweep.svg"),
    )
    args = parser.parse_args()
    plot(args.input, args.output)


if __name__ == "__main__":
    main()
