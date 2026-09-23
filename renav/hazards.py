"""Action-triggered stochastic topology hazards."""

from __future__ import annotations
from dataclasses import dataclass
from renav.planners.grid_map import GridCell, GridMap
from renav.recoverability import TopologyHazardBelief, exact_safe_return_probability

DirectedTransition=tuple[GridCell,GridCell]

@dataclass(frozen=True)
class ActionTriggeredClosure:
    trigger: DirectedTransition
    closure_cell: GridCell
    closure_probability: float

@dataclass(frozen=True)
class ActionTriggeredHazardModel:
    closures: tuple[ActionTriggeredClosure,...]

    def validate(self, grid: GridMap) -> None:
        seen=set()
        for h in self.closures:
            if h.trigger[1] not in grid.neighbors4(h.trigger[0]):
                raise ValueError(f"trigger is not a traversable grid edge: {h.trigger}")
            if not grid.in_bounds(h.closure_cell) or not grid.passable(h.closure_cell):
                raise ValueError(f"closure cell must be currently free: {h.closure_cell}")
            if not 0 <= h.closure_probability <= 1: raise ValueError("closure_probability must be in [0, 1]")
            if h.trigger in seen: raise ValueError(f"duplicate trigger: {h.trigger}")
            seen.add(h.trigger)

    def active_indices_after(self, source: GridCell, target: GridCell, active: frozenset[int]) -> frozenset[int]:
        return active | frozenset(i for i,h in enumerate(self.closures) if h.trigger==(source,target))

    def belief(self, active: frozenset[int], current: GridCell) -> TopologyHazardBelief:
        probs={}
        for i in active:
            h=self.closures[i]
            if h.closure_cell != current: probs[h.closure_cell]=h.closure_probability
        return TopologyHazardBelief(probs)

def history_conditioned_return_probability(grid: GridMap, current: GridCell, safe_cells: set[GridCell],
                                           model: ActionTriggeredHazardModel, active: frozenset[int]) -> float:
    return exact_safe_return_probability(grid,current,safe_cells,model.belief(active,current))
