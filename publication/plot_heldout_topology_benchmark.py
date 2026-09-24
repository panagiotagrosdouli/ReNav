"""Plot held-out topology benchmark success by hazard regime and planner."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

REGIMES = ("critical", "harmless", "no_effect", "all")
METHODS = (
    ("geometric", "Geometric"),
    ("static_marginal", "Static marginal"),
    ("history_weight_4", "History A*, weight 4"),
    ("hard_return_0.8", "Hard return, threshold 0.8"),
)


def plot(input_path: Path, output_path: Path) -> None:
    with input_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    lookup = {(row["regime"], row["planner"]): row for row in rows}
    figure, axis = plt.subplots(figsize=(8.0, 4.8), layout="constrained")
    x = np.arange(len(REGIMES))
    width = 0.18
    offsets = np.linspace(-1.5 * width, 1.5 * width, len(METHODS))
    for (method, label), offset in zip(METHODS, offsets, strict=True):
        selected = [lookup[(regime, method)] for regime in REGIMES]
        success = [float(row["success_rate"]) for row in selected]
        lower = [float(row["success_95_low"]) for row in selected]
        upper = [float(row["success_95_high"]) for row in selected]
        axis.bar(
            x + offset,
            success,
            width,
            label=label,
            yerr=[
                [max(0.0, estimate - low) for estimate, low in zip(success, lower, strict=True)],
                [max(0.0, high - estimate) for estimate, high in zip(success, upper, strict=True)],
            ],
            capsize=2,
        )
    axis.set_xticks(x, REGIMES)
    axis.set(
        xlabel="Hazard regime",
        ylabel="Mission-and-return success",
        ylim=(0, 1.08),
    )
    axis.grid(axis="y", alpha=0.25)
    axis.legend(frameon=False, ncols=2, loc="lower center")
    figure.text(
        0.5,
        -0.015,
        "500 generated wall-and-gap grids; 95% Wilson intervals. Synthetic stress test only.",
        ha="center",
        fontsize=8,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams["svg.fonttype"] = "none"
    figure.savefig(output_path, format="svg", metadata={"Date": None})
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/heldout_topology_summary.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("publication/figures/heldout_topology.svg"),
    )
    args = parser.parse_args()
    plot(args.input, args.output)


if __name__ == "__main__":
    main()
