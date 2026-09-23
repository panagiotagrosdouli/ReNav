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
        for cell, p in self.closure_probability.items():
            if not grid.in_bounds(cell) or cell in grid.obstacles:
                raise ValueError(f"hazard cell must be currently free: {cell}")
            if not 0.0 <= p <= 1.0:
                raise ValueError("closure probability must be in [0, 1]")

def _reachable(grid: GridMap, start: GridCell, safe: set[GridCell]) -> bool:
    if not grid.in_bounds(start) or not grid.passable(start):
        return False
    targets={c for c in safe if grid.in_bounds(c) and grid.passable(c)}
    q=deque([start]); seen={start}
    while q:
        cur=q.popleft()
        if cur in targets: return True
        for nxt in grid.neighbors4(cur):
            if nxt not in seen: seen.add(nxt); q.append(nxt)
    return False

def exact_safe_return_probability(grid: GridMap, start: GridCell, safe_cells: set[GridCell],
                                  hazard: TopologyHazardBelief, *, max_hazard_cells: int=16) -> float:
    grid.validate(); hazard.validate(grid)
    cells=sorted(c for c in hazard.closure_probability if c != start)
    if len(cells)>max_hazard_cells:
        raise ValueError(f"exact enumeration limited to {max_hazard_cells} hazard cells")
    total=0.0
    for flags in product((False,True), repeat=len(cells)):
        p=1.0; obs=set(grid.obstacles)
        for cell,closed in zip(cells,flags,strict=True):
            pc=float(hazard.closure_probability[cell]); p*=pc if closed else 1-pc
            if closed: obs.add(cell)
        if p and _reachable(GridMap.from_obstacles(grid.width,grid.height,obs),start,safe_cells):
            total+=p
    return min(1.0,max(0.0,total))
