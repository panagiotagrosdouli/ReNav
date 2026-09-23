import pytest
from renav.hazards import ActionTriggeredClosure, ActionTriggeredHazardModel, history_conditioned_return_probability
from renav.planners.grid_map import GridMap
from renav.planners.history_astar import HistoryAStarConfig, history_astar

def trap():
    grid=GridMap.from_obstacles(4,3,{(1,0),(1,2)})
    model=ActionTriggeredHazardModel((ActionTriggeredClosure(((2,1),(3,1)),(1,1),0.8),))
    return grid,(0,1),(3,1),model

def test_same_state_different_history():
    grid,start,goal,model=trap()
    assert history_conditioned_return_probability(grid,goal,{start},model,frozenset()) == pytest.approx(1.0)
    assert history_conditioned_return_probability(grid,goal,{start},model,frozenset({0})) == pytest.approx(0.2)

def test_history_aware_route_avoids_trigger():
    grid,start,goal,model=trap()
    result=history_astar(grid,start,goal,safe_cells={start},hazard_model=model,
                         config=HistoryAStarConfig(recoverability_weight=4.0))
    assert result.success
    assert len(result.path)-1 == 5
    assert result.activated_hazards == frozenset()
    assert result.final_return_probability == pytest.approx(1.0)

def test_zero_weight_recovers_shortest_choice():
    grid,start,goal,model=trap()
    result=history_astar(grid,start,goal,safe_cells={start},hazard_model=model,
                         config=HistoryAStarConfig(recoverability_weight=0.0))
    assert len(result.path)-1 == 3
    assert result.activated_hazards == frozenset({0})
