# Held-out topology stress test: results and provenance

## Scope and protocol

This is a synthetic stress test over one seeded wall-and-gap generator, not a sample of natural or real-world navigation maps. The generator was frozen in `docs/experimental_protocol_v2.md` before the benchmark runner was added. It samples 500 maps from seeds 20261024–20261523 and includes three predeclared regimes: 300 critical closures at a return bottleneck, 100 harmless closures at previously traversed non-articulation cells, and 100 no-effect closures with p=0. The generator rejected 187 candidate maps before obtaining the 500 valid instances.

The policies were geometric shortest path, a state-only fixed marginal-risk planner, history-conditioned A* with recoverability weight 4, and a hard return threshold of 0.8. Every policy used the same latent uniform draw within a map. A closure was realized only when that policy executed the trigger. The primary outcome was successful goal arrival and return to the start. The paired normal intervals below use map-level standard errors; success-rate intervals are Wilson 95% intervals.

## Results by regime

| Regime | Maps | Geometric success | Static marginal success | History A*, weight 4 | Hard return 0.8 | Hard minus history (paired 95% CI) |
|---|---:|---:|---:|---:|---:|---:|
| Critical closure | 300 | 0.380 (0.327–0.436) | 0.380 (0.327–0.436) | 0.980 (0.957–0.991) | 1.000 (0.987–1.000) | +0.020 (+0.004–+0.036) |
| Harmless closure | 100 | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 0.000 |
| No effect, p=0 | 100 | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 1.000 (0.963–1.000) | 0.000 |

On the 300 critical maps, the exact mean route-level success probabilities were 0.392 for geometric and static marginal, 0.982 for history A*, and 1.000 for hard return. The observed geometric, static, history, and hard trigger-activation rates were 1.000, 1.000, 0.040, and 0.000. Mean path lengths were 10.187, 10.187, 10.747, and 10.847 cells, respectively.

On the critical maps, history A* improved success over geometry by 0.600 (paired 95% CI 0.544–0.656). The hard threshold improved it by 0.620 (0.565–0.675). The hard planner therefore exceeded the soft objective by 0.020 on this family, while using a route only 0.100 cells longer on average. This is a negative result for any claim that the soft history objective is superior to a hard return constraint.

The state-only fixed-marginal planner chose exactly the geometric paths in all 500 maps. In the no-effect and harmless controls, all four methods had identical success. These controls match the protocol predictions and bound the interpretation of the critical-regime gain.

The experiment deliberately enriches for bottleneck topology and guarantees a trigger bypass. Its effect sizes must not be generalized beyond the declared generator. The static marginal baseline is one fixed-map formulation and does not replace a fully Markovized environment-state or belief-space comparator.

## Reproducibility and files

The complete 500-row raw CSV is versioned at [`results/heldout_topology_trials.csv`](../results/heldout_topology_trials.csv). The aggregate table is [`results/heldout_topology_summary.csv`](../results/heldout_topology_summary.csv); the generated figure is [`publication/figures/heldout_topology.svg`](figures/heldout_topology.svg).

- Workflow run: [35982098729](https://github.com/panagiotagrosdouli/ReNav/actions/runs/35982098729)
- Benchmark code commit: `b24647b7114320a251a75ddfb8586a8fad103e4a`
- Command: `python experiments/run_heldout_topology_benchmark.py --maps 500 --first-seed 20261024`
- Protocol: `docs/experimental_protocol_v2.md`
- Raw-trial CSV SHA-256: `b7c6380b8bf66e45e81b3769ae1ea6f98303e4233af795f55947c83964e825f7`
- Summary CSV SHA-256: `d5eac0c7c78d723a7d828189f71b1b8be7b9ef7cc09ea9bffb5fa9057d14ef7d`
- Figure SVG SHA-256: `47d8cf2a55ecc0c392b35188443e6578da60412893b576779702b4bf5cb0e75c`

The CI artifact also contains the outputs and has ZIP SHA-256 `5b2c3489ce036430738ef79d6c7e34f19232ea4591eca55741bc5caf53aa1733`; it expires on 23 December 2026. The raw CSV, aggregate table, script, protocol, and figure are committed to the repository, so the artifact is supplementary.
