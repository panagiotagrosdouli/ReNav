# DynNav audit for ReNav

Audit date: 2026-09-23. Source commit: `77c2e2dc327b7722fbdf8e1c6dd920855f885e6a`.

## Canonical dependency graph retained
The smallest directly relevant chain is:

`grid_map -> action-triggered hazard model -> exact safe-return oracle -> augmented-state planner -> paired experiment/statistics`.

DynNav already contains this chain in `dynnav/planners/grid_map.py`, `dynnav/commitment_hazard.py`, `dynnav/recoverability_belief.py`, and `dynnav/planners/commitment_aware_astar.py`, with known-answer tests. ReNav ports the minimal semantics rather than the surrounding exploratory repository.

## Evidence classification
Implemented and unit-tested: same-state/different-history mechanism; exact independent-Bernoulli safe-return enumeration for bounded hazard sets; augmented-state A* semantics.

Reported synthetic evidence in DynNav: repeated-module and frozen geometric studies, paired common-random-number evaluation, hard-safe-return comparisons, and approximation counterexamples. These are inherited evidence until independently reproduced in ReNav.

Simulation: DynNav contains ROS 2/Nav2 and Gazebo infrastructure, but its own publication boundary states that history-conditioned Gazebo efficacy is not yet established.

Real-world/public-data and physical hardware: no retained evidence supports an efficacy claim.

## Excluded from the foundational port
Dashboards/web apps, unrelated learned planning, cybersecurity/IDS, photogrammetry, multi-robot work, generic belief-risk experiments, obsolete prototypes, and unrelated contribution folders are not dependencies of the core representation claim and are not migrated.

## Scientific risks
The exact oracle assumes independent closures and known probabilities; the exact state space grows with activated hazards; a hard safe-return constraint can match the soft objective; constructed topology families may overstate practical effect size; and the novelty boundary must be tested against safe-return, belief-space, contingency, viability, and history-dependent planning literature.
