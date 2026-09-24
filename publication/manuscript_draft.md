# When Executed Actions Change the Way Home: A Minimal Model of History-Conditioned Return Connectivity

**Working manuscript — 24 September 2026.** This is a research draft, not a submission-ready paper. It records the model and the currently verified analytical construction. The repository includes a paired Monte Carlo sweep on one constructed grid and a 500-map synthetic stress test from one seeded wall-and-gap generator. These results are preliminary evidence under declared synthetic assumptions, not evidence of real-world efficacy or generalization to natural maps.

## Abstract

In some navigation problems, traversing a directed transition activates a stochastic change elsewhere in the environment. The change may affect whether a robot can later return to a designated safe set. In such settings, the robot's geometric position alone need not determine its return probability: the set of previously activated transitions can also matter. We formalize this mechanism on finite grid maps with known action triggers and independent Bernoulli closures, define exact safe-return probability by enumeration, and describe an augmented-state planner whose state includes position and executed-trigger history. A small analytic construction in the accompanying reference implementation exhibits two histories ending at the same cell with safe-return probabilities 1 and 0.2. This establishes a representational counterexample to a planner that retains position but discards trigger history under the stated model. It does not establish practical benefit, broad novelty, real-world safety, or superiority over Markov, belief-space, or constrained-planning methods. On one constructed grid, a paired Monte Carlo sweep with 10,000 common random-number trials per probability showed that a hard return threshold and a soft history-conditioned objective choose the same routes over much of the sweep. At closure probability 0.8, both avoid the trigger and achieve success 1.0000, while geometric shortest path succeeds at 0.2005 (paired gain 0.7995; 95% interval 0.7917–0.8073). The single-map sweep is mechanism evidence. A separate 500-map stress test found a gain on predeclared critical-bottleneck instances, but the generator intentionally enriches for such bottlenecks. Neither experiment establishes generalization to natural maps or real-world efficacy. Stronger Markov/belief baselines, broader topology families, literature review, and simulator evidence remain necessary before submission.

## 1. Introduction

Mobile-robot planners commonly trade route cost against collision risk, uncertainty, or the probability of satisfying a return constraint. A narrower case arises when a robot's *executed action* activates a stochastic topology change at another location. For example, crossing a one-way trigger could cause a remote corridor to close with some probability. The resulting chance of returning to a safe set may then depend on which trigger transitions the robot has actually executed, even when two trajectories end at the same cell.

This paper isolates that mechanism. It asks whether geometric position and a fixed marginal hazard map are sufficient to represent safe-return connectivity after action-triggered topology changes. We study a deliberately small model so that return probability can be computed exactly and checked against known-answer cases.

The contribution is limited to: (i) a finite-grid formulation that distinguishes executed trigger history from candidate-plan reasoning; (ii) an exact return-connectivity oracle under independent Bernoulli closures; and (iii) an explicit same-position/different-history construction. A reference A* implementation demonstrates how this state can affect route choice. We do not claim that history augmentation, safe-return planning, probabilistic safety, or belief-space planning is new. A richer Markov state can encode the environment's activated-trigger state, and established work already studies safe-return constraints and planning under uncertainty. The unresolved scientific question is whether the specific action-triggered return-connectivity mechanism creates a consequential information gap for useful baseline planners and realistic execution systems.

## 2. Related work and scope

Safe-return constraints have been studied in hierarchical motion planning under probabilistic temporal tasks [1]. Belief-space planning has a long history, including the Belief Roadmap [2]. Probabilistic navigation with uncertain obstacles has also been addressed directly [3]. History-aware navigation has been explored in unknown uneven terrain, including simulation and physical-robot evaluation [4]. These works establish that uncertainty, safety, return behavior, and history can all be relevant to navigation.

The present formulation is narrower than those themes: action execution activates stochastic changes to future topology, and the outcome of interest is connectivity to a designated safe set conditional on the activated-trigger history. This distinction is provisional. The current literature matrix is a seed review rather than a systematic search; any novelty statement must wait for a broader review and strong baseline comparisons.

## 3. Model

Let a finite four-connected grid be a graph G=(V,E), with static obstacle set O, start and goal cells, and designated safe set S. The planner state is

```
s_t = (x_t, H_t)
```

where x_t is the current free cell and H_t is the set of trigger indices activated by transitions actually executed up to time t.

Hazard i comprises a directed trigger edge e_i=(u_i,v_i) in E, a closure cell c_i not in O, and a known probability p_i in [0,1]. Executing e_i adds i to H_t; merely considering a candidate plan does not. The exact oracle assumes each active hazard corresponds to a distinct closure cell and closure events are independent. The implementation does not model uncertain probabilities, correlations, sensing, robot dynamics, or delayed observations.

For current cell x and active set H, safe-return probability is

```
R(x, H) = P(a traversable path exists from x to some s in S | H).
```

The oracle enumerates every realization of the active closure cells, computes its Bernoulli probability, and sums the probability mass of realizations in which graph search reaches S. A straightforward implementation costs O(2^k (|V|+|E|)) for k active closure cells.

## 4. Planner

The reference planner runs A* on augmented states (x,H). For each legal move x to x', it updates H' only when the directed transition is traversed by that candidate route, then evaluates R(x',H'). The implemented edge cost is

```
c((x,H),(x',H')) = c_step + lambda * (1 - R(x',H'))
```

with nonnegative c_step and lambda. The heuristic is Manhattan distance on the unit-cost grid. The objective is a soft recoverability penalty; it is not a chance constraint or safety guarantee.

The preregistered comparator set includes geometric shortest path, a state-only marginal-risk planner, a hard safe-return constraint, and a scalable approximation. These baselines are not all implemented yet. The current paired sweep compares the geometric path, the exact-history planner over several penalty weights, and a hard-return-threshold planner on the canonical map.

## 5. Analytical construction

**Proposition (position is not sufficient under the stated model).** There exist a grid, safe set, trigger model, and two executed histories that end at the same cell (x) but have different safe-return probabilities.

**Construction.** In the (4\times3) grid used by the reference test, cells ((1,0)) and ((1,2)) are static obstacles. The safe set is the start cell ((0,1)). A directed transition ((2,1)\to(3,1)) activates a closure at ((1,1)) with probability (0.8). From (x=(3,1)), every route to the safe set passes through ((1,1)). If the trigger has not been executed, no stochastic closure is active and (R(x,\varnothing)=1). If it has been executed, the return path exists exactly when the closure does not occur, giving (R(x,\{i\})=1-0.8=0.2). Thus identical position with distinct executed history yields distinct return probabilities.

This is an analytic counterexample for the specified finite model. The repository tests also check that, for one declared penalty weight, the reference planner chooses a longer route that avoids the trigger, while zero recoverability weight yields a shortest route that activates it. These tests demonstrate expected behavior on a constructed instance; they are not a comparative evaluation over a sampled environment distribution.

## 6. Paired synthetic experiment

We evaluated the canonical 4-by-3 trap map at closure probabilities 0.1, 0.2, 0.4, 0.6, 0.8, and 0.9. The planners were geometric shortest path, a hard return-probability threshold of 0.8, and history-conditioned A* with recoverability weights 0, 1, 2, 4, and 8. For each probability, every planner was evaluated against the same 10,000 uniform random draws (seed 20260924). A draw realizes a closure only for planners that execute its trigger. The outcome is successful goal arrival followed by successful return to the safe set. The runner records raw paired outcomes, route length, activated hazards, empirical success, Wilson 95% intervals, exact route-level success probabilities, and paired differences versus geometry with Wald intervals.

### Results

The direct geometric path has length 3 and activates the trigger; the avoiding route has length 5. At closure probabilities 0.1 and 0.2, all evaluated policies take the direct path. At 0.4, the hard threshold and weight-8 history planner take the detour while weight 4 still takes the direct path. At 0.6, 0.8, and 0.9, the hard threshold and history planner at weights 4 and 8 take the detour.

At p=0.8, geometric success was 0.2005 (Wilson 95% CI 0.1928–0.2085). The hard-return planner and history A* with weight 4 each succeeded in all 10,000 trials (Wilson 95% CI 0.9996–1.0000). The paired success gain of the hard-return planner over geometry was 0.7995 (paired Wald 95% CI 0.7917–0.8073). At p=0.4, the weight-4 planner retained the direct path and matched geometric success at 0.6007; the hard-return planner took the detour, with paired gain 0.3993 (95% CI 0.3897–0.4089).

These results show a route-cost/risk trade-off on the declared map. They also show a negative result for any superiority claim: in regimes where the hard threshold and soft objective select the same route, the hard planner matches the soft planner's success. The exact probabilities are determined by the route and the Bernoulli model; repeated trials quantify Monte Carlo variability and are not independent environment instances.

The complete summary table is in `results/mechanistic_sweep.csv`; a detailed description is in `publication/mechanistic_sweep_report.md`; and Figure 1 is `publication/figures/mechanistic_sweep.svg`.



## 7. Randomized-topology stress test

We ran the frozen protocol in `docs/experimental_protocol_v2.md` on 500 seeded maps generated by one wall-and-gap procedure (seeds 20261024–20261523): 300 critical closures at a return bottleneck, 100 harmless closures, and 100 no-effect controls (p=0). The generator rejected 187 candidates before producing the 500 valid maps. Policies were geometric shortest path, a fixed state-only marginal-risk planner, exact history-conditioned A* (weight 4), and a hard return threshold (0.8). Within each map, policies shared the same latent uniform draw. The primary outcome was successful goal arrival and return to the start. Intervals below are map-level Wilson 95% intervals; paired differences use normal-approximation intervals.

| Regime | n | Geometry | Fixed marginal | History A*, w=4 | Hard return, 0.8 |
|---|---:|---:|---:|---:|---:|
| Critical closure | 300 | 0.380 (0.327–0.436) | 0.380 (0.327–0.436) | 0.980 (0.957–0.991) | 1.000 (0.987–1.000) |
| Harmless closure | 100 | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) |
| No effect, p=0 | 100 | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) |

On critical maps, history A* improved success over geometry by 0.600 (paired 95% CI 0.544–0.656), while the hard threshold improved it by 0.620 (0.565–0.675). The hard method exceeded the soft objective by 0.020 (0.004–0.036) with a mean route-length increase of 0.100 cells. Thus, this experiment does not support soft-objective superiority. The static marginal planner chose exactly the geometric paths on all 500 maps. All methods matched each other in the two control regimes, as predicted.

This test is deliberately enriched for bottleneck topology and for maps with a trigger bypass. Its effect sizes characterize this generator only. The fixed marginal baseline is not a fully Markovized environment-state or belief-space planner. The raw per-map results, aggregate summary, figure, protocol, and run manifest are versioned in the repository; detailed provenance and checksums are in `publication/heldout_topology_report.md` and `publication/heldout_topology_run_manifest.json`.

## 8. Evidence and reproducibility

The raw paired trial file was generated by GitHub Actions run [35979953475](https://github.com/panagiotagrosdouli/ReNav/actions/runs/35979953475) from commit `e9b64d7f89ac7d309517ee1af26d95526843c8b8`, using `python experiments/run_mechanistic_sweep.py --trials 10000 --seed 20260924`. The run retained 60,000 rows in the Actions artifact (artifact ID `10799716911`). Its ZIP SHA-256 is `7c1f5d003140f1ba68f6fd51249d1cc7f7e1081873c691988b27539c28d7936a`. The aggregate CSV is committed in the repository. The Actions artifact expires on 23 December 2026, so the raw trial file still needs durable archiving before submission. A future claim must cite the final archived data DOI or an immutable repository release.

Reproduce the sweep with:

```bash
python -m pip install -e '.[dev,plots]'
python experiments/run_mechanistic_sweep.py --trials 10000 --seed 20260924
python publication/plot_mechanistic_sweep.py
pytest -q
ruff check renav tests experiments publication
```

The CI workflow runs the test suite and Ruff, generates both experiments and figures, and uploads output artifacts. The committed raw CSVs and code provide the durable record. The topology results concern one deliberately constructed synthetic generator; they do not establish performance on a natural-map distribution.

## 9. Limitations and open tests

The model assumes a known static grid, known trigger semantics, known closure probabilities, independent closure events, a known safe set, and exact enumeration over a bounded number of hazards. It abstracts away continuous dynamics, localization and perception uncertainty, trigger observability, execution failures, and replanning delays. The current experiment uses one hand-designed map; 60,000 paired rows across six probabilities do not substitute for independent maps.

The study now includes one randomized synthetic topology family and a fixed state-only marginal-risk baseline. It still lacks broader topology families, a strong fully Markovized environment-state or belief-space baseline, model-miscalibration and correlated-hazard regimes, and simulator evaluation. A richer Markov or belief state can encode trigger activation. The hard-return comparator matched or exceeded the soft objective in the tested regimes. These points constrain novelty and algorithmic claims and are central tests for the next study.

## 10. Conclusion

We formalized a minimal finite-grid setting in which executed actions activate stochastic closures that affect return connectivity. An exact construction proves that position alone can alias two histories with different safe-return probabilities. The reference implementation makes this distinction executable and testable. Whether this mechanism supports a useful algorithmic contribution remains an empirical question. The present manuscript is a starting point for that evaluation, not evidence of efficacy or a submission-ready account.

## References

1. M. Guo et al. “Hierarchical Motion Planning Under Probabilistic Temporal Tasks and Safe-Return Constraints.” *IEEE Transactions on Automatic Control*, 2023. https://doi.org/10.1109/TAC.2023.3244884
2. S. Prentice and N. Roy. “The Belief Roadmap: Efficient Planning in Belief Space by Factoring the Covariance.” *The International Journal of Robotics Research*, 28(11–12):1448–1465, 2009. https://doi.org/10.1177/0278364909341659
3. B. Axelrod, L. P. Kaelbling, and T. Lozano-Pérez. “Provably Safe Robot Navigation with Obstacle Uncertainty.” *The International Journal of Robotics Research*, 37(2–3), 2018. https://doi.org/10.1177/0278364918778338
4. Y. Wang et al. “History-Aware Planning for Risk-free Autonomous Navigation on Unknown Uneven Terrain.” *2024 IEEE International Conference on Robotics and Automation (ICRA)*, 2024. https://doi.org/10.1109/ICRA57147.2024.10610488
