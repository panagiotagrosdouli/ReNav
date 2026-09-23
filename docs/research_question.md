# Research question

## Problem
ReNav studies navigation in which an **executed directed action** can activate a stochastic future change in environment topology. Consequently, geometric position alone need not be a sufficient planning state.

## Reference state
The minimal Markov state used by the exact reference planner is
[
s_t=(x_t,H_t),
]
where (x_t) is the robot cell and (H_t) is the set of hazards activated by executed transitions up to time (t).

## Recoverability
For safe set (S), grid (G), and activated history (H),
[
R(x,H)=P(\exists\text{ traversable path from }x\text{ to }S\mid H).
]
The current implementation assumes known trigger semantics and independent Bernoulli closure events.

## Central falsifiable hypothesis
There exist action-triggered topology processes for which two histories ending at the same (x) induce different (R(x,H)); therefore a planner whose state is only (x) and whose hazard representation is a fixed marginal map aliases decision-relevant information.

This is a representation claim, not a universal performance or safety claim. A stronger empirical hypothesis is that retaining (H) reduces post-invalidation recovery-infeasible failures at acceptable path/runtime cost in declared environment families. That claim requires paired execution evidence.

## Failure modes
The hypothesis has no practical advantage when triggers have no effect, when all candidate histories activate equivalent hazards, when a hard safe-return constraint already selects the same route, or when the assumed closure distribution is badly misspecified. Exact enumeration also scales exponentially in the number of unresolved hazards.
