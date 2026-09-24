# ReNav

Recoverability-aware navigation research for environments where an executed action can activate a stochastic change to future return connectivity.

## Research question

Can two navigation histories that end at the same geometric position imply different probabilities of returning to a designated safe set, because one history has activated stochastic topology hazards?

This repository contains a minimal finite-grid formulation and reference implementation. Its claims are limited to the assumptions and tests described below. It does not establish real-world safety or general planner superiority.

## Current repository contents

- `renav/`: finite grid, action-triggered closure model, exact safe-return probability for small independent hazard sets, and augmented-state A*.
- `experiments/run_mechanistic_sweep.py`: paired Monte Carlo sweep on one deliberately constructed grid, with exact Bernoulli outcome probabilities recorded alongside estimates.
- `experiments/run_heldout_topology_benchmark.py`: 500-map synthetic stress test over one frozen wall-and-gap generator, with common random numbers, raw per-map outcomes, aggregate results, and provenance.
- `tests/`: known-answer and route-choice regressions, including a check of the sweep against exact outcomes.
- `docs/`: research question, provisional gap, seed literature review, experimental protocol, limitations, and DynNav audit.
- `publication/manuscript_draft.md`: working manuscript with both experiments; not ready for submission.
- `publication/heldout_topology_report.md` and `publication/heldout_topology_run_manifest.json`: stress-test results and reproducibility metadata.
- `docs/experimental_protocol_v2.md`: frozen protocol for the 500-map synthetic stress test.
- `.github/workflows/ci.yml`: Python tests and Ruff lint checks.

The repository now contains a 500-map synthetic stress test over one deliberately bottleneck-enriched generator. It is not a sample of natural or real-world maps and does not establish generalization or broad planner superiority. The repository has no ROS/Nav2 or Gazebo packages and no simulator trials.

## Install and test

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check renav tests
```

Run the paired constructed-instance sweep:

```bash
python experiments/run_mechanistic_sweep.py --trials 10000 --seed 20260924 --output results/mechanistic_sweep.csv
```

The runner uses a common Bernoulli draw for every planner at each trial. It reports empirical success, Wilson intervals, exact success probability, path length, and activated hazards across a closure-probability sweep and planner weights. This is a single-map mechanism check; it cannot support a general efficacy claim.

Run the frozen 500-map synthetic stress test:

```bash
python experiments/run_heldout_topology_benchmark.py --maps 500 --first-seed 20261024
python publication/plot_heldout_topology_benchmark.py
```

The protocol in `docs/experimental_protocol_v2.md` predefines critical-bottleneck, harmless-closure, and no-effect regimes. History-conditioned planning improved success over geometry on the critical regime, but the hard-return baseline slightly outperformed the soft objective. The fixed state-only marginal baseline exactly matched geometry on this generator. See `publication/heldout_topology_report.md` for regime-specific estimates, limitations, and checksums. This is synthetic stress-test evidence for one designed generator, not evidence about natural maps or real robots.

## Model

A hazard consists of a directed grid transition, a closure cell, and a Bernoulli closure probability. It becomes active only after the transition is executed. For position `x`, active hazard set `H`, and designated safe set `S`, the reference quantity is

```
R(x, H) = P(a traversable path exists from x to S | H).
```

The current oracle exactly enumerates independent closures and is limited to small hazard sets. The planner searches states that include both position and activated-trigger history. It uses a soft recoverability penalty; it is not a chance-constrained safety guarantee.

## Evidence boundary and next steps

The repository contains an analytic construction, a paired sweep on that constructed map, and a 500-map synthetic stress test from one frozen generator. The latter compares geometric, fixed state-only marginal-risk, history-conditioned, and hard-return policies, with raw outcomes and run metadata committed. The generator deliberately enriches for bottlenecks and does not represent a natural-map distribution. A submission still requires broader topology families, a stronger fully Markovized or belief-space baseline, model-miscalibration and correlated-hazard tests, a broader literature review, and simulator evaluation if real-system claims are intended.
