"""Action-triggered stochastic topology hazards."""

from __future__ import annotations

from dataclasses import dataclass

from renav.planners.grid_map import GridCell, GridMap
from renav.recoverability import TopologyHazardBelief, exact_safe_return_probability

DirectedTransition = tuple[GridCell, GridCell]


@dataclass(frozen=True)
class ActionTriggeredClosure:
    trigger: DirectedTransition
    closure_cell: GridCell
    closure_probability: float


@dataclass(frozen=True)
class ActionTriggeredHazardModel:
    closures: tuple[ActionTriggeredClosure, ...]

    def validate(self, grid: GridMap) -> None:
        seen: set[DirectedTransition] = set()
        for hazard in self.closures:
            if hazard.trigger[1] not in grid.neighbors4(hazard.trigger[0]):
                raise ValueError(f"trigger is not a traversable grid edge: {hazard.trigger}")
            if not grid.in_bounds(hazard.closure_cell) or not grid.passable(hazard.closure_cell):
                raise ValueError(f"closure cell must be currently free: {hazard.closure_cell}")
            if not 0.0 <= hazard.closure_probability <= 1.0:
                raise ValueError("closure_probability must be in [0, 1]")
            if hazard.trigger in seen:
                raise ValueError(f"duplicate trigger: {hazard.trigger}")
            seen.add(hazard.trigger)

    def active_indices_after(
        self,
        source: GridCell,
        target: GridCell,
        active: frozenset[int],
    ) -> frozenset[int]:
        additions = {
            index
            for index, hazard in enumerate(self.closures)
            if hazard.trigger == (source, target)
        }
        return active | frozenset(additions)

    def belief(
        self,
        active: frozenset[int],
        current: GridCell,
    ) -> TopologyHazardBelief:
        probabilities: dict[GridCell, float] = {}
        for index in active:
            if index < 0 or index >= len(self.closures):
                raise ValueError(f"activated hazard index out of range: {index}")
            hazard = self.closures[index]
            if hazard.closure_cell == current:
                continue
            existing = probabilities.get(hazard.closure_cell)
            if existing is not None and existing != hazard.closure_probability:
                raise ValueError(
                    "active hazards assign conflicting probabilities "
                    f"to {hazard.closure_cell}"
                )
            probabilities[hazard.closure_cell] = hazard.closure_probability
        return TopologyHazardBelief(probabilities)


def history_conditioned_return_probability(
    grid: GridMap,
    current: GridCell,
    safe_cells: set[GridCell],
    model: ActionTriggeredHazardModel,
    active: frozenset[int],
) -> float:
    return exact_safe_return_probability(
        grid,
        current,
        safe_cells,
        model.belief(active, current),
    )
