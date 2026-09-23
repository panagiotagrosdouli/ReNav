# Provisional research gap

The literature already covers probabilistic safety, belief-space planning, viability/reachability, recovery policies, safe-return constraints, and history-aware navigation. ReNav therefore does **not** claim novelty for "risk-aware", "recoverability-aware", "safe-return", or "history-aware" planning in isolation.

The candidate gap is narrower: planning when **executed robot actions activate stochastic future degradation of return connectivity**, so that the sufficient planning state must retain action-trigger history and a fixed state-only marginal hazard map can alias histories.

This distinction is provisional. It survives only if a broader systematic review finds no equivalent formulation and if strong baselines cannot represent the same information without explicit history augmentation.

## Reviewer-facing falsification questions
1. Can an MDP/POMDP formulation with an ordinary environment state encode the same mechanism trivially? If yes, ReNav's contribution must be algorithmic/experimental rather than conceptual.
2. Does a hard safe-return constraint match the soft objective across meaningful regimes?
3. Does history matter outside hand-constructed bottlenecks?
4. How sensitive are decisions to closure-probability miscalibration and correlation?
5. Can a scalable sufficient statistic replace the full activated-hazard set?
6. Do execution-level Nav2/Gazebo results reproduce the mechanism after sensing, replanning, and costmap delays?

## Current direction
The strongest next direction is **belief-conditioned action-triggered recoverability**: replace known closure probabilities with calibrated/posterior uncertainty while preserving executed-history semantics, then compare against state-only marginal, hard-safe-return, and belief-space/contingency baselines. This direction is testable and directly attacks the strongest realism limitation without changing the research question.
