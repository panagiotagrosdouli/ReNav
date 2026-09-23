"""Augmented-state A* over position and executed hazard-activation history."""

from __future__ import annotations
import heapq
from dataclasses import dataclass
from renav.hazards import ActionTriggeredHazardModel, history_conditioned_return_probability
from renav.planners.grid_map import GridCell, GridMap, manhattan

State=tuple[GridCell,frozenset[int]]

@dataclass(frozen=True)
class HistoryAStarConfig:
    step_cost: float=1.0
    recoverability_weight: float=4.0

@dataclass(frozen=True)
class HistoryAStarResult:
    path: tuple[GridCell,...]
    success: bool
    cost: float
    final_return_probability: float
    activated_hazards: frozenset[int]

def history_astar(grid: GridMap,start: GridCell,goal: GridCell,*,safe_cells:set[GridCell],
                  hazard_model:ActionTriggeredHazardModel,config:HistoryAStarConfig=HistoryAStarConfig(),
                  initial_activated:frozenset[int]=frozenset()) -> HistoryAStarResult:
    grid.validate(); hazard_model.validate(grid)
    initial=(start,initial_activated); frontier=[(0.0,0,initial)]; costs={initial:0.0}; parents={}; counter=0
    while frontier:
        _,_,state=heapq.heappop(frontier); cell,active=state
        if cell==goal:
            states=[state]
            while states[-1] in parents: states.append(parents[states[-1]])
            states.reverse(); path=tuple(s[0] for s in states)
            rp=history_conditioned_return_probability(grid,cell,safe_cells,hazard_model,active)
            return HistoryAStarResult(path,True,costs[state],rp,active)
        for nxt in grid.neighbors4(cell):
            na=hazard_model.active_indices_after(cell,nxt,active); ns=(nxt,na)
            rp=history_conditioned_return_probability(grid,nxt,safe_cells,hazard_model,na)
            nc=costs[state]+config.step_cost+config.recoverability_weight*(1-rp)
            if nc < costs.get(ns,float("inf")):
                costs[ns]=nc; parents[ns]=state; counter+=1
                heapq.heappush(frontier,(nc+manhattan(nxt,goal),counter,ns))
    return HistoryAStarResult((),False,float("inf"),0.0,initial_activated)
