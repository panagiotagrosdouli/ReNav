"""Exact safe-return probability for small independent topology-hazard sets."""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from itertools import product

from renav.planners.grid_map import GridCell, GridMap


@dataclass(frozen=True)
class TopologyHazardBelief:
    closure_probability: Mapping[GridCell, float]

    def validate(self, grid: GridMap) -> None:
        for cell, probability in self.closure_probability.items():
            if not grid.in_bounds(cell) or cell in grid.obstacles:
                raise ValueError(f"hazard cell must be currently free: {cell}")
            if not 0.0 <= probability <= 1.0:
                raise ValueError("closure probability must be in [0, 1]")


def _reachable(grid: GridMap, start: GridCell, safe: set[GridCell]) -> bool:
    if not grid.in_bounds(start) or not grid.passable(start):
        return False
    targets = {cell for cell in safe if grid.in_bounds(cell) and grid.passable(cell)}
    if not targets:
        return False
    queue: deque[GridCell] = deque([start])
    seen = {start}
    while queue:
        current = queue.popleft()
        if current in targets:
            return True
        for neighbor in grid.neighbors4(current):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return False


def exact_safe_return_probability(
    grid: GridMap,
    start: GridCell,
    safe_cells: set[GridCell],
    hazard: TopologyHazardBelief,
    *,
    max_hazard_cells: int = 16,
) -> float:
    grid.validate()
    hazard.validate(grid)
    if max_hazard_cells < 0:
        raise ValueError("max_hazard_cells must be non-negative")
    cells = sorted(cell for cell in hazard.closure_probability if cell != start)
    if len(cells) > max_hazard_cells:
        raise ValueError(f"exact enumeration limited to {max_hazard_cells} hazard cells")

    total = 0.0
    for flags in product((False, True), repeat=len(cells)):
        realization_probability = 1.0
        obstacles = set(grid.obstacles)
        for cell, closed in zip(cells, flags, strict=True):
            probability = float(hazard.closure_probability[cell])
            realization_probability *= probability if closed else 1.0 - probability
            if closed:
                obstacles.add(cell)
        realized = GridMap.from_obstacles(grid.width, grid.height, obstacles)
        if realization_probability and _reachable(realized, start, safe_cells):
            total += realization_probability
    return min(1.0, max(0.0, total))
