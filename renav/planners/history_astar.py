"""Augmented-state A* over position and executed hazard-activation history."""

from __future__ import annotations

import heapq
from dataclasses import dataclass

from renav.hazards import (
    ActionTriggeredHazardModel,
    history_conditioned_return_probability,
)
from renav.planners.grid_map import GridCell, GridMap, manhattan

State = tuple[GridCell, frozenset[int]]


@dataclass(frozen=True)
class HistoryAStarConfig:
    step_cost: float = 1.0
    recoverability_weight: float = 4.0

    def validate(self) -> None:
        if self.step_cost <= 0.0:
            raise ValueError("step_cost must be positive")
        if self.recoverability_weight < 0.0:
            raise ValueError("recoverability_weight must be non-negative")


@dataclass(frozen=True)
class HistoryAStarResult:
    path: tuple[GridCell, ...]
    success: bool
    cost: float
    final_return_probability: float
    activated_hazards: frozenset[int]


def history_astar(
    grid: GridMap,
    start: GridCell,
    goal: GridCell,
    *,
    safe_cells: set[GridCell],
    hazard_model: ActionTriggeredHazardModel,
    config: HistoryAStarConfig | None = None,
    initial_activated: frozenset[int] = frozenset(),
) -> HistoryAStarResult:
    grid.validate()
    hazard_model.validate(grid)
    cfg = config or HistoryAStarConfig()
    cfg.validate()
    if not grid.in_bounds(start) or not grid.in_bounds(goal):
        raise ValueError("start and goal must be inside the grid")
    if not grid.passable(start) or not grid.passable(goal):
        return HistoryAStarResult((), False, float("inf"), 0.0, initial_activated)

    initial: State = (start, initial_activated)
    frontier: list[tuple[float, int, State]] = [(0.0, 0, initial)]
    costs: dict[State, float] = {initial: 0.0}
    parents: dict[State, State] = {}
    counter = 0

    while frontier:
        _, _, state = heapq.heappop(frontier)
        cell, active = state
        if cell == goal:
            states = [state]
            while states[-1] in parents:
                states.append(parents[states[-1]])
            states.reverse()
            path = tuple(item[0] for item in states)
            probability = history_conditioned_return_probability(
                grid, cell, safe_cells, hazard_model, active
            )
            return HistoryAStarResult(path, True, costs[state], probability, active)

        for neighbor in grid.neighbors4(cell):
            next_active = hazard_model.active_indices_after(cell, neighbor, active)
            next_state: State = (neighbor, next_active)
            probability = history_conditioned_return_probability(
                grid, neighbor, safe_cells, hazard_model, next_active
            )
            new_cost = (
                costs[state]
                + cfg.step_cost
                + cfg.recoverability_weight * (1.0 - probability)
            )
            if new_cost < costs.get(next_state, float("inf")):
                costs[next_state] = new_cost
                parents[next_state] = state
                counter += 1
                priority = new_cost + cfg.step_cost * manhattan(neighbor, goal)
                heapq.heappush(frontier, (priority, counter, next_state))

    return HistoryAStarResult((), False, float("inf"), 0.0, initial_activated)
