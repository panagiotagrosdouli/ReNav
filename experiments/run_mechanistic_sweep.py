"""Paired Monte Carlo mechanism sweep for the canonical ReNav trap map.

This is a narrow constructed-instance experiment, not evidence of map generalization.
It retains both per-trial paired outcomes and exact route-level expectations.
"""
from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import random

from renav.hazards import (
    ActionTriggeredClosure,
    ActionTriggeredHazardModel,
    history_conditioned_return_probability,
)
from renav.planners.grid_map import GridCell, GridMap
from renav.planners.history_astar import HistoryAStarConfig, history_astar


def make_case(
    closure_probability: float,
) -> tuple[GridMap, GridCell, GridCell, ActionTriggeredHazardModel]:
    grid = GridMap.from_obstacles(4, 3, {(1, 0), (1, 2)})
    model = ActionTriggeredHazardModel(
        (ActionTriggeredClosure(((2, 1), (3, 1)), (1, 1), closure_probability),)
    )
    return grid, (0, 1), (3, 1), model


def geometric_path(grid: GridMap, start: GridCell, goal: GridCell) -> tuple[GridCell, ...]:
    frontier = [start]
    parent: dict[GridCell, GridCell | None] = {start: None}
    for current in frontier:
        if current == goal:
            break
        for nxt in grid.neighbors4(current):
            if nxt not in parent:
                parent[nxt] = current
                frontier.append(nxt)
    if goal not in parent:
        return ()
    path = [goal]
    while path[-1] != start:
        previous = parent[path[-1]]
        assert previous is not None
        path.append(previous)
    return tuple(reversed(path))


def hard_threshold_path(
    grid: GridMap,
    start: GridCell,
    goal: GridCell,
    *,
    safe_cells: set[GridCell],
    model: ActionTriggeredHazardModel,
    threshold: float,
) -> tuple[GridCell, ...]:
    initial = (start, frozenset())
    frontier = [initial]
    parent: dict[tuple[GridCell, frozenset[int]], tuple[GridCell, frozenset[int]] | None] = {
        initial: None
    }
    final = None
    for state in frontier:
        cell, active = state
        if cell == goal:
            final = state
            break
        for nxt in grid.neighbors4(cell):
            next_active = model.active_indices_after(cell, nxt, active)
            if history_conditioned_return_probability(
                grid, nxt, safe_cells, model, next_active
            ) < threshold:
                continue
            next_state = (nxt, next_active)
            if next_state not in parent:
                parent[next_state] = state
                frontier.append(next_state)
    if final is None:
        return ()
    states = [final]
    while parent[states[-1]] is not None:
        previous = parent[states[-1]]
        assert previous is not None
        states.append(previous)
    states.reverse()
    return tuple(state[0] for state in states)


def activated_hazards(
    path: tuple[GridCell, ...], model: ActionTriggeredHazardModel
) -> frozenset[int]:
    active: frozenset[int] = frozenset()
    for source, target in zip(path, path[1:]):
        active = model.active_indices_after(source, target, active)
    return active


def wilson(successes: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    estimate = successes / n
    denom = 1 + z * z / n
    center = (estimate + z * z / (2 * n)) / denom
    radius = z * math.sqrt(estimate * (1 - estimate) / n + z * z / (4 * n * n)) / denom
    return center - radius, center + radius


def run(
    trials: int,
    seed: int,
    output: Path,
    raw_output: Path | None = None,
) -> None:
    probabilities = (0.1, 0.2, 0.4, 0.6, 0.8, 0.9)
    weights = (0.0, 1.0, 2.0, 4.0, 8.0)
    threshold = 0.8
    rng = random.Random(seed)
    rows = []
    raw_rows = []
    for probability in probabilities:
        grid, start, goal, model = make_case(probability)
        geometric = geometric_path(grid, start, goal)
        hard = hard_threshold_path(
            grid, start, goal, safe_cells={start}, model=model, threshold=threshold
        )
        paths = {"geometric": geometric, "hard_return_0.8": hard}
        for weight in weights:
            result = history_astar(
                grid,
                start,
                goal,
                safe_cells={start},
                hazard_model=model,
                config=HistoryAStarConfig(recoverability_weight=weight),
            )
            paths[f"history_weight_{weight:g}"] = result.path if result.success else ()

        uniforms = [rng.random() for _ in range(trials)]
        active_by_planner = {
            name: activated_hazards(path, model) for name, path in paths.items()
        }
        outcomes = {
            name: [
                int(not (bool(active) and draw < probability))
                for draw in uniforms
            ]
            for name, active in active_by_planner.items()
        }
        for trial_index, draw in enumerate(uniforms):
            raw_row = {
                "seed": seed,
                "closure_probability": probability,
                "trial_index": trial_index,
                "uniform_draw": draw,
            }
            raw_row.update(
                {f"success_{name}": outcomes[name][trial_index] for name in paths}
            )
            raw_rows.append(raw_row)

        geometric_outcomes = outcomes["geometric"]
        for name, path in paths.items():
            successes = sum(outcomes[name])
            lower, upper = wilson(successes, trials)
            differences = [
                outcome - baseline
                for outcome, baseline in zip(
                    outcomes[name], geometric_outcomes, strict=True
                )
            ]
            paired_delta = sum(differences) / trials
            if trials > 1:
                variance = sum((value - paired_delta) ** 2 for value in differences) / (
                    trials - 1
                )
                paired_se = math.sqrt(variance / trials)
            else:
                paired_se = 0.0
            active = active_by_planner[name]
            rows.append(
                {
                    "seed": seed,
                    "trials": trials,
                    "closure_probability": probability,
                    "hard_threshold": threshold,
                    "planner": name,
                    "path_length": len(path) - 1 if path else "",
                    "activated_hazards": ";".join(map(str, sorted(active))),
                    "empirical_success_rate": successes / trials,
                    "wilson_95_low": lower,
                    "wilson_95_high": upper,
                    "paired_delta_vs_geometric": paired_delta,
                    "paired_delta_95_low": paired_delta - 1.96 * paired_se,
                    "paired_delta_95_high": paired_delta + 1.96 * paired_se,
                    "exact_success_probability": 1.0 - probability * bool(active),
                }
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    if raw_output is None:
        raw_output = output.with_name(f"{output.stem}_trials.csv")
    raw_output.parent.mkdir(parents=True, exist_ok=True)
    with raw_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(raw_rows[0]))
        writer.writeheader()
        writer.writerows(raw_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mechanistic_sweep.csv"),
    )
    parser.add_argument(
        "--raw-output",
        type=Path,
        default=Path("results/mechanistic_sweep_trials.csv"),
    )
    args = parser.parse_args()
    if args.trials <= 0:
        parser.error("--trials must be positive")
    run(args.trials, args.seed, args.output, args.raw_output)


if __name__ == "__main__":
    main()
