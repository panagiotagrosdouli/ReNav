# When Executed Actions Change the Way Home: A Minimal Model of History-Conditioned Return Connectivity

**Working manuscript — 24 September 2026.** This is a research draft, not a submission-ready paper. It records the model and the currently verified analytical construction. The repository does not yet contain the benchmark suite or independent comparative evidence needed for efficacy or generalization claims.

## Abstract

In some navigation problems, traversing a directed transition activates a stochastic change elsewhere in the environment. The change may affect whether a robot can later return to a designated safe set. In such settings, the robot's geometric position alone need not determine its return probability: the set of previously activated transitions can also matter. We formalize this mechanism on finite grid maps with known action triggers and independent Bernoulli closures, define exact safe-return probability by enumeration, and describe an augmented-state planner whose state includes position and executed-trigger history. A small analytic construction in the accompanying reference implementation exhibits two histories ending at the same cell with safe-return probabilities 1 and 0.2. This establishes a representational counterexample to a planner that retains position but discards trigger history under the stated model. It does not establish practical benefit, broad novelty, real-world safety, or superiority over Markov, belief-space, or constrained-planning methods. ReNav is therefore presented as a falsifiable problem formulation and preliminary reference implementation. Comparative synthetic and simulator experiments, broader literature review, and scalability analysis remain necessary before submission.

## 1. Introduction

Mobile-robot planners commonly trade route cost against collision risk, uncertainty, or the probability of satisfying a return constraint. A narrower case arises when a robot's *executed action* activates a stochastic topology change at another location. For example, crossing a one-way trigger could cause a remote corridor to close with some probability. The resulting chance of returning to a safe set may then depend on which trigger transitions the robot has actually executed, even when two trajectories end at the same cell.

This paper isolates that mechanism. It asks whether geometric position and a fixed marginal hazard map are sufficient to represent safe-return connectivity after action-triggered topology changes. We study a deliberately small model so that return probability can be computed exactly and checked against known-answer cases.

The contribution is limited to: (i) a finite-grid formulation that distinguishes executed trigger history from candidate-plan reasoning; (ii) an exact return-connectivity oracle under independent Bernoulli closures; and (iii) an explicit same-position/different-history construction. A reference A* implementation demonstrates how this state can affect route choice. We do not claim that history augmentation, safe-return planning, probabilistic safety, or belief-space planning is new. A richer Markov state can encode the environment's activated-trigger state, and established work already studies safe-return constraints and planning under uncertainty. The unresolved scientific question is whether the specific action-triggered return-connectivity mechanism creates a consequential information gap for useful baseline planners and realistic execution systems.

## 2. Related work and scope

Safe-return constraints have been studied in hierarchical motion planning under probabilistic temporal tasks [1]. Belief-space planning has a long history, including the Belief Roadmap [2]. Probabilistic navigation with uncertain obstacles has also been addressed directly [3]. History-aware navigation has been explored in unknown uneven terrain, including simulation and physical-robot evaluation [4]. These works establish that uncertainty, safety, return behavior, and history can all be relevant to navigation.

The present formulation is narrower than those themes: action execution activates stochastic changes to future topology, and the outcome of interest is connectivity to a designated safe set conditional on the activated-trigger history. This distinction is provisional. The current literature matrix is a seed review rather than a systematic search; any novelty statement must wait for a broader review and strong baseline comparisons.

## 3. Model

Let a finite four-connected grid be (G=(V,E)), with static obstacle set (Osubset V), start/goal cells, and designated safe set (Ssubseteq V). The robot state used by the reference planner is
[
s_t=(x_t,H_t),
]
where (x_tin V\setminus O) is the current cell and (H_t) is the set of trigger indices activated by *executed* transitions up to time (t).

A hazard (i) comprises a directed trigger edge (e_i=(u_i,v_i)in E), a closure cell (c_iin V\setminus O), and a known probability (p_iin[0,1]). Executing (e_i) adds (i) to (H_t); merely considering a candidate path does not. For the exact oracle, each active hazard corresponds to a distinct closure cell and closure events are independent. The current implementation does not model uncertain probabilities, correlations, sensing, robot dynamics, or delayed observations.

For current cell (x) and active set (H), define safe-return probability
[
R(x,H)=\Pr\bigl(\exists\text{ a traversable path from }x\text{ to some }s\in S\mid H\bigr).
]
The oracle enumerates every realization of the active closure cells, computes its Bernoulli probability, and sums the probability mass of realizations in which graph search reaches (S). Its cost is exponential in the number (k) of active closure cells: (O(2^k(|V|+|E|))) for a straightforward implementation.

## 4. Planner

The reference planner runs A* on augmented states ((x,H)). For each legal move (x\to x'), it updates (H') only when that directed transition is executed in the search path, then evaluates (R(x',H')). The implemented edge cost is
[
c((x,H),(x',H'))=c_{\mathrm{step}}+\lambda\bigl(1-R(x',H')\bigr),
]
with nonnegative (c_{\mathrm{step}}) and (lambda). A Manhattan-distance heuristic is used on the unit-cost grid. The objective is a soft recoverability penalty; it is not a chance constraint or a safety guarantee. The repository's protocol identifies geometric shortest path, fixed state-only marginal-risk, hard safe-return, and scalable-approximation planners as required experimental comparators. Only the geometric and augmented-state reference planners are present in the current minimal code tree.

## 5. Analytical construction

**Proposition (position is not sufficient under the stated model).** There exist a grid, safe set, trigger model, and two executed histories that end at the same cell (x) but have different safe-return probabilities.

**Construction.** In the (4\times3) grid used by the reference test, cells ((1,0)) and ((1,2)) are static obstacles. The safe set is the start cell ((0,1)). A directed transition ((2,1)\to(3,1)) activates a closure at ((1,1)) with probability (0.8). From (x=(3,1)), every route to the safe set passes through ((1,1)). If the trigger has not been executed, no stochastic closure is active and (R(x,\varnothing)=1). If it has been executed, the return path exists exactly when the closure does not occur, giving (R(x,\{i\})=1-0.8=0.2). Thus identical position with distinct executed history yields distinct return probabilities.

This is an analytic counterexample for the specified finite model. The repository tests also check that, for one declared penalty weight, the reference planner chooses a longer route that avoids the trigger, while zero recoverability weight yields a shortest route that activates it. These tests demonstrate expected behavior on a constructed instance; they are not a comparative evaluation over a sampled environment distribution.

## 6. Evidence and reproducibility status

The public repository currently contains the finite-grid model, exact independent-closure return oracle, augmented-state A*, a small unit-test suite, a research protocol, and a CI workflow. On 24 September 2026, the follow-up core-contract PR passed GitHub Actions and was merged. These checks establish software-level regressions only.

The repository README describes larger experiments, simulator infrastructure, manifests, and retained results, but those paths are not present in the current default-branch tree. The README's empirical-status statements therefore cannot be independently verified from the current checkout and are not used as evidence in this draft. Before submission, the project must either restore the scripts, raw trials, run manifests, analysis, and artifacts it refers to, or revise the README to match the available material.

The frozen protocol calls for common latent hazard draws across planners; geometric, state-only marginal-risk, exact-history, hard-safe-return, and scalable-approximation baselines; paired outcomes and confidence intervals; held-out topology families; no-effect and miscalibration regimes; and preservation of negative results. Required outcomes include post-invalidation recovery-infeasible failure, mission success, return probability, path length, planning latency, activated hazards, and realized closures. No quantitative comparative result is claimed here.

## 7. Limitations and open tests

The model assumes a known static grid, known trigger semantics, known closure probabilities, independent closure events, a known safe set, and exact enumeration over a bounded number of hazards. It abstracts away continuous dynamics, localization and perception uncertainty, trigger observability, execution failures, and the timing of replanning. The construction is intentionally hand-designed and cannot establish map generalization.

The strongest baseline may encode the activation state in a Markov or belief state without calling it history. The soft objective may be matched or exceeded by a hard return constraint. Results may be sensitive to probability calibration and event correlation. Exact enumeration scales exponentially. Finally, the proposed distinction may be covered by prior work not yet captured in the seed literature matrix. These are central falsification questions, not peripheral caveats.

## 8. Conclusion

We formalized a minimal finite-grid setting in which executed actions activate stochastic closures that affect return connectivity. An exact construction proves that position alone can alias two histories with different safe-return probabilities. The reference implementation makes this distinction executable and testable. Whether this mechanism supports a useful algorithmic contribution remains an empirical question. The present manuscript is a starting point for that evaluation, not evidence of efficacy or a submission-ready account.

## References

1. M. Guo et al. “Hierarchical Motion Planning Under Probabilistic Temporal Tasks and Safe-Return Constraints.” *IEEE Transactions on Automatic Control*, 2023. https://doi.org/10.1109/TAC.2023.3244884
2. S. Prentice and N. Roy. “The Belief Roadmap: Efficient Planning in Belief Space by Factoring the Covariance.” *The International Journal of Robotics Research*, 28(11–12):1448–1465, 2009. https://doi.org/10.1177/0278364909341659
3. B. Axelrod, L. P. Kaelbling, and T. Lozano-Pérez. “Provably Safe Robot Navigation with Obstacle Uncertainty.” *The International Journal of Robotics Research*, 37(2–3), 2018. https://doi.org/10.1177/0278364918778338
4. Y. Wang et al. “History-Aware Planning for Risk-free Autonomous Navigation on Unknown Uneven Terrain.” *2024 IEEE International Conference on Robotics and Automation (ICRA)*, 2024. https://doi.org/10.1109/ICRA57147.2024.10610488
