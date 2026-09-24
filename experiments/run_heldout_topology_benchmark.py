"""Held-out paired stress test over seeded wall-and-gap grid worlds."""
from __future__ import annotations

import argparse
import csv
import heapq
import random
from itertools import pairwise
from pathlib import Path

from renav.hazards import (
    ActionTriggeredClosure,
    ActionTriggeredHazardModel,
    history_conditioned_return_probability,
)
from renav.planners.grid_map import GridCell, GridMap
from renav.planners.history_astar import HistoryAStarConfig, history_astar
from renav.recoverability import TopologyHazardBelief, exact_safe_return_probability


def find_path(
    grid: GridMap,
    start: GridCell,
    goal: GridCell,
    *,
    blocked: set[GridCell] | None = None,
    forbidden_transition: tuple[GridCell, GridCell] | None = None,
) -> tuple[GridCell, ...]:
    blocked_cells = blocked or set()
    if start in blocked_cells or goal in blocked_cells:
        return ()
    parent: dict[GridCell, GridCell | None] = {start: None}
    queue = [start]
    for current in queue:
        if current == goal:
            break
        for nxt in grid.neighbors4(current):
            if nxt in blocked_cells or (current, nxt) == forbidden_transition:
                continue
            if nxt not in parent:
                parent[nxt] = current
                queue.append(nxt)
    if goal not in parent:
        return ()
    path = [goal]
    while path[-1] != start:
        previous = parent[path[-1]]
        assert previous is not None
        path.append(previous)
    return tuple(reversed(path))


def make_world(index: int, seed: int) -> tuple[dict, int]:
    rng = random.Random(seed)
    regime = ("no_effect", "harmless", "critical")[index % 5] if index % 5 < 2 else "critical"
    rejected = 0
    for _ in range(500):
        width = rng.randint(6, 9)
        height = rng.randint(5, 8)
        split = width // 2
        gap_y = rng.randint(1, height - 2)
        start = (0, rng.randrange(height))
        goal = (width - 1, rng.randrange(height))
        obstacles = {(split, y) for y in range(height) if y != gap_y}
        for x in range(width):
            for y in range(height):
                cell = (x, y)
                if x == split or cell == start or cell == goal:
                    continue
                if rng.random() < 0.12:
                    obstacles.add(cell)
        grid = GridMap.from_obstacles(width, height, obstacles)
        base_path = find_path(grid, start, goal)
        if not base_path:
            rejected += 1
            continue
        trigger_candidates = []
        for source, target in pairwise(base_path):
            if source[0] <= split or target[0] <= split:
                continue
            if find_path(
                grid,
                start,
                goal,
                forbidden_transition=(source, target),
            ):
                trigger_candidates.append((source, target))
        if not trigger_candidates:
            rejected += 1
            continue
        trigger = rng.choice(trigger_candidates)
        trigger_index = next(
            i
            for i, edge in enumerate(pairwise(base_path))
            if edge == trigger
        )
        if regime == "harmless":
            prior_cells = base_path[: trigger_index + 1]
            harmless_cells = [
                cell
                for cell in prior_cells
                if cell not in {start, goal, (split, gap_y)}
                and find_path(grid, start, goal, blocked={cell})
            ]
            if not harmless_cells:
                rejected += 1
                continue
            closure_cell = rng.choice(harmless_cells)
        else:
            closure_cell = (split, gap_y)
        probability = 0.0 if regime == "no_effect" else rng.uniform(0.3, 0.9)
        model = ActionTriggeredHazardModel(
            (ActionTriggeredClosure(trigger, closure_cell, probability),)
        )
        return {
            "index": index,
            "seed": seed,
            "regime": regime,
            "grid": grid,
            "start": start,
            "goal": goal,
            "safe": {start},
            "model": model,
            "base_path": base_path,
            "trigger": trigger,
            "closure_cell": closure_cell,
            "probability": probability,
            "split": split,
            "gap_y": gap_y,
        }, rejected
    raise RuntimeError(f"could not generate valid map {index} after 500 attempts")


def static_marginal_path(world: dict, weight: float = 4.0) -> tuple[GridCell, ...]:
    grid, start, goal = world["grid"], world["start"], world["goal"]
    closure = world["closure_cell"]
    probability = world["probability"]
    belief = TopologyHazardBelief({closure: probability})
    frontier = [(0.0, 0, start)]
    costs = {start: 0.0}
    parent: dict[GridCell, GridCell | None] = {start: None}
    counter = 0
    while frontier:
        _, _, cell = heapq.heappop(frontier)
        if cell == goal:
            break
        for nxt in grid.neighbors4(cell):
            risk = exact_safe_return_probability(grid, nxt, world["safe"], belief)
            candidate = costs[cell] + 1.0 + weight * (1.0 - risk)
            if candidate < costs.get(nxt, float("inf")):
                costs[nxt] = candidate
                parent[nxt] = cell
                counter += 1
                heapq.heappush(frontier, (candidate, counter, nxt))
    if goal not in parent:
        return ()
    path = [goal]
    while path[-1] != start:
        previous = parent[path[-1]]
        assert previous is not None
        path.append(previous)
    return tuple(reversed(path))


def hard_return_path(world: dict, threshold: float = 0.8) -> tuple[GridCell, ...]:
    grid, start, goal, model, safe = (
        world["grid"],
        world["start"],
        world["goal"],
        world["model"],
        world["safe"],
    )
    initial = (start, frozenset())
    queue = [initial]
    parent = {initial: None}
    final = None
    for cell, active in queue:
        if cell == goal:
            final = (cell, active)
            break
        for nxt in grid.neighbors4(cell):
            next_active = model.active_indices_after(cell, nxt, active)
            risk = history_conditioned_return_probability(
                grid, nxt, safe, model, next_active
            )
            if risk < threshold:
                continue
            state = (nxt, next_active)
            if state not in parent:
                parent[state] = (cell, active)
                queue.append(state)
    if final is None:
        return ()
    states = [final]
    while parent[states[-1]] is not None:
        previous = parent[states[-1]]
        assert previous is not None
        states.append(previous)
    states.reverse()
    return tuple(state[0] for state in states)


def policy_paths(world: dict, weight: float) -> dict[str, tuple[GridCell, ...]]:
    result = history_astar(
        world["grid"],
        world["start"],
        world["goal"],
        safe_cells=world["safe"],
        hazard_model=world["model"],
        config=HistoryAStarConfig(recoverability_weight=weight),
    )
    return {
        "geometric": world["base_path"],
        "static_marginal": static_marginal_path(world),
        "history_weight_4": result.path if result.success else (),
        "hard_return_0.8": hard_return_path(world),
    }


def path_success(world: dict, path: tuple[GridCell, ...], draw: float) -> tuple[int, float, bool]:
    if not path:
        return 0, 0.0, False
    active = False
    trigger_index = -1
    for index, edge in enumerate(pairwise(path)):
        if edge == world["trigger"]:
            active = True
            trigger_index = index
            break
    if not active:
        return 1, 1.0, False

    probability = world["probability"]
    closed_grid = GridMap.from_obstacles(
        world["grid"].width,
        world["grid"].height,
        set(world["grid"].obstacles) | {world["closure_cell"]},
    )
    closure_already_passed = world["closure_cell"] in path[: trigger_index + 2]
    closed_success = int(
        closure_already_passed
        and bool(find_path(closed_grid, world["goal"], world["start"]))
    )
    realized_success = 1 if draw >= probability else closed_success
    exact_success = (1.0 - probability) + probability * closed_success
    return realized_success, exact_success, True


def wilson(successes: int, n: int) -> tuple[float, float]:
    z = 1.959963984540054
    estimate = successes / n
    denominator = 1.0 + z * z / n
    center = (estimate + z * z / (2.0 * n)) / denominator
    radius = z * (
        estimate * (1.0 - estimate) / n + z * z / (4.0 * n * n)
    ) ** 0.5 / denominator
    return center - radius, center + radius


def summarize(rows: list[dict], regimes: tuple[str, ...]) -> list[dict]:
    methods = ("geometric", "static_marginal", "history_weight_4", "hard_return_0.8")
    summary = []
    for regime in (*regimes, "all"):
        subset = [row for row in rows if regime == "all" or row["regime"] == regime]
        n = len(subset)
        for method in methods:
            successes = [int(row[f"success_{method}"]) for row in subset]
            delta = [
                value - int(row["success_geometric"])
                for value, row in zip(successes, subset, strict=True)
            ]
            mean_success = sum(successes) / n
            success_low, success_high = wilson(sum(successes), n)
            mean_exact_success = sum(
                float(row[f"exact_success_{method}"]) for row in subset
            ) / n
            history_delta = [
                value - int(row["success_history_weight_4"])
                for value, row in zip(successes, subset, strict=True)
            ]
            mean_history_delta = sum(history_delta) / n
            history_variance = (
                sum((value - mean_history_delta) ** 2 for value in history_delta)
                / (n - 1)
                if n > 1
                else 0.0
            )
            history_se = (history_variance / n) ** 0.5
            mean_delta = sum(delta) / n
            variance = (
                sum((value - mean_delta) ** 2 for value in delta) / (n - 1)
                if n > 1
                else 0.0
            )
            se = (variance / n) ** 0.5
            summary.append(
                {
                    "regime": regime,
                    "n_maps": n,
                    "planner": method,
                    "success_rate": mean_success,
                    "success_95_low": success_low,
                    "success_95_high": success_high,
                    "mean_exact_success_probability": mean_exact_success,
                    "paired_delta_vs_history_weight_4": mean_history_delta,
                    "history_delta_95_low": mean_history_delta - 1.96 * history_se,
                    "history_delta_95_high": mean_history_delta + 1.96 * history_se,
                    "paired_delta_vs_geometric": mean_delta,
                    "paired_95_low": mean_delta - 1.96 * se,
                    "paired_95_high": mean_delta + 1.96 * se,
                    "mean_path_length": sum(float(row[f"path_length_{method}"]) for row in subset)
                    / n,
                    "trigger_activation_rate": sum(
                        int(row[f"activated_{method}"]) for row in subset
                    )
                    / n,
                }
            )
    return summary


def run(n_maps: int, first_seed: int, output_dir: Path) -> tuple[int, int]:
    raw_rows = []
    rejected_total = 0
    for index in range(n_maps):
        world, rejected = make_world(index, first_seed + index)
        rejected_total += rejected
        paths = policy_paths(world, weight=4.0)
        draw = random.Random(world["seed"] ^ 0x9E3779B9).random()
        row = {
            "index": index,
            "seed": world["seed"],
            "regime": world["regime"],
            "width": world["grid"].width,
            "height": world["grid"].height,
            "start": world["start"],
            "goal": world["goal"],
            "closure_cell": world["closure_cell"],
            "trigger": world["trigger"],
            "closure_probability": world["probability"],
            "uniform_draw": draw,
            "rejected_candidates": rejected,
        }
        for method, path in paths.items():
            success, exact_success, activated = path_success(world, path, draw)
            row[f"path_length_{method}"] = len(path) - 1 if path else ""
            row[f"activated_{method}"] = int(activated)
            row[f"exact_success_{method}"] = exact_success
            row[f"success_{method}"] = success
        raw_rows.append(row)

    summary = summarize(raw_rows, ("critical", "harmless", "no_effect"))
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_path = output_dir / "heldout_topology_trials.csv"
    summary_path = output_dir / "heldout_topology_summary.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(raw_rows[0]))
        writer.writeheader()
        writer.writerows(raw_rows)
    with summary_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    return rejected_total, len(raw_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--maps", type=int, default=500)
    parser.add_argument("--first-seed", type=int, default=20261024)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    if args.maps < 3:
        parser.error("--maps must be at least 3")
    rejected, completed = run(args.maps, args.first_seed, args.output_dir)
    print(f"completed_maps={completed} rejected_candidates={rejected}")


if __name__ == "__main__":
    main()
