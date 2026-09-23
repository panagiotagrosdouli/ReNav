# Experimental protocol v1

Freeze this protocol before comparative outcome inspection.

Primary mechanism test: same geometric endpoint, different activated histories, exact return probability known analytically.

Primary execution comparison: shortest path, state-only marginal return-risk, exact history-conditioned planner, hard safe-return constraint, and a declared scalable approximation. Use identical maps and common latent hazard draws across planners; a draw only realizes when that planner executed its trigger.

Primary outcome: post-invalidation recovery-infeasible failure. Secondary outcomes: mission success, safe-return probability, path length, planning/replanning latency, activated hazards, and realized closures.

Required falsification regimes: p=0 no-effect, harmless triggers, necessary-risk routes, parallel/correlated cuts, probability miscalibration, delayed observation, increasing hazard count, and held-out topology families.

Report paired effect sizes and confidence intervals. Do not select seeds, maps, thresholds, or weights after viewing final comparative outcomes. Preserve negative results, especially regimes where hard safe-return equals or exceeds the soft objective.

Evidence labels must remain distinct: unit test; analytic construction; synthetic execution; simulator execution; public recorded data; physical hardware.
