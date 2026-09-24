# Experimental protocol v2: held-out action-trigger topology family

**Frozen before running the map-family benchmark.** This is a synthetic stress test, not a simulator or physical-robot protocol.

## Question and hypothesis

Across independently generated grid worlds with one action-triggered closure, does retaining executed-trigger history improve mission-and-return success over geometric shortest path and a fixed state-only marginal-risk planner, and what is its path-cost trade-off against a hard return threshold?

The representation hypothesis predicts an information gap only in critical-hazard worlds. It predicts no benefit in the no-effect and harmless-closure controls. No universal superiority claim is tested.

## Generator

Generate 500 maps using independent random.Random(seed) instances with seeds 20261024 through 20261523. For each map:

- Sample grid width uniformly from 6–9 and height from 5–8.
- Place a vertical wall at x = width // 2 with one randomly selected gap; add independent within-half obstacles at probability 0.12, then reject worlds without start-goal connectivity.
- Choose start on the left boundary and goal on the right boundary.
- Find a shortest start-goal path and a directed edge on its right-side suffix whose removal still leaves a route to the goal. This edge is the trigger; the baseline shortest route executes it.
- Assign regimes deterministically by map index: 60% critical closure at the wall gap, 20% no-effect closure with p=0, and 20% harmless closure at a previously traversed non-articulation cell.
- In nonzero regimes, sample p uniformly from [0.3, 0.9].
- Reject and regenerate a map if a valid bypassed trigger or required harmless cell cannot be found.

The wall-and-gap construction intentionally enriches for return bottlenecks while randomizing dimensions, gap placement, obstacle layout, start/goal rows, trigger location, and probability. It does not approximate a natural or real-world map distribution.

## Policies and metrics

Compare (1) geometric shortest path, (2) a state-only planner that treats each hazard's marginal probability as present at every position and uses the same soft cost weight 4, (3) exact history-conditioned A* with weight 4, and (4) an exact hard return threshold of 0.8. The one-hazard-per-map model makes exact return probabilities tractable.

For each map, all policies share a single uniform latent draw. A closure is realized only if its trigger was executed. The primary outcome is successful goal arrival and return to the safe start after that realization. Secondary outcomes are exact route-level success probability, path length, trigger activation, and regime-specific paired success differences. Report map-level paired normal-approximation 95% intervals with sample standard error, and retain all per-map outcomes.

## Falsification and reporting rules

Report all 500 maps, all three regimes, failed/rejected generator counts, and exact code/seed. Do not omit negative controls or select maps after outcome inspection. Do not label the Monte Carlo map outcomes as real-world safety rates. Compare the soft objective with the hard threshold directly; if they choose the same paths and perform the same, report that result.

The script, raw per-map file, aggregate table, and map-family figure must be generated from one command on a pinned commit. A later change to this protocol requires a new version and an explicit rationale.
