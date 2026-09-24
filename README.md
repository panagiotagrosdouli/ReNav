# ReNav

Recoverability-aware navigation research for environments where an executed action can activate a stochastic change to future return connectivity.

## Research question

Can two navigation histories that end at the same geometric position imply different probabilities of returning to a designated safe set, because one history has activated stochastic topology hazards?

This repository contains a minimal finite-grid formulation and reference implementation. Its claims are limited to the assumptions and tests described below. It does not establish real-world safety or general planner superiority.

## Current repository contents

- `renav/`: finite grid, action-triggered closure model, exact safe-return probability for small independent hazard sets, and augmented-state A*.
- `experiments/run_mechanistic_sweep.py`: paired Monte Carlo sweep on one deliberately constructed grid, with exact Bernoulli outcome probabilities recorded alongside estimates.
- `tests/`: known-answer and route-choice regressions, including a check of the sweep against exact outcomes.
- `docs/`: research question, provisional gap, seed literature review, experimental protocol, limitations, and DynNav audit.
- `publication/manuscript_draft.md`: working manuscript foundation; not ready for submission.
- `.github/workflows/ci.yml`: Python tests and Ruff lint checks.

The default branch does not currently contain held-out-map benchmarks, ROS/Nav2 or Gazebo packages, evidence manifests, or simulator trials. The mechanistic sweep is not evidence of map generalization or broad planner superiority.

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

## Model

A hazard consists of a directed grid transition, a closure cell, and a Bernoulli closure probability. It becomes active only after the transition is executed. For position `x`, active hazard set `H`, and designated safe set `S`, the reference quantity is

```
R(x, H) = P(a traversable path exists from x to S | H).
```

The current oracle exactly enumerates independent closures and is limited to small hazard sets. The planner searches states that include both position and activated-trigger history. It uses a soft recoverability penalty; it is not a chance-constrained safety guarantee.

## Evidence boundary and next steps

The repository contains a small analytic construction and a paired Monte Carlo sweep on that same constructed map. They show the expected mechanism under declared assumptions. They do not measure performance over a held-out environment distribution.

The frozen protocol in `docs/experimental_protocol.md` remains a plan for the broader study. A paper submission requires reproducible held-out topology benchmarks against geometric, state-only marginal-risk, hard safe-return, and scalable-approximation baselines; retained raw trials and run metadata; uncertainty-aware reporting; and a broader literature review. Simulator or hardware claims require corresponding completed experiments.
