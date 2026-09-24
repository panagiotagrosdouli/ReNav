# ReNav

Recoverability-aware navigation research for environments where an executed action can activate a stochastic change to future return connectivity.

## Research question

Can two navigation histories that end at the same geometric position imply different probabilities of returning to a designated safe set, because one history has activated stochastic topology hazards?

This repository contains a minimal finite-grid formulation and reference implementation. Its claims are limited to the assumptions and tests described below. It does not establish real-world safety or general planner superiority.

## Current repository contents

- `renav/`: finite grid, action-triggered closure model, exact safe-return probability for small independent hazard sets, and augmented-state A*.
- `tests/`: known-answer and route-choice regression tests.
- `docs/`: research question, provisional gap, seed literature review, experimental protocol, limitations, and DynNav audit.
- `publication/manuscript_draft.md`: working manuscript foundation; not ready for submission.
- `.github/workflows/ci.yml`: Python tests and Ruff lint checks.

The default branch does not currently contain the benchmark runners, ROS/Nav2 or Gazebo packages, evidence manifests, retained trial data, or analysis scripts mentioned in earlier versions of this README. No comparative experiment results are claimed here.

## Install and test

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
ruff check renav tests
```

## Model

A hazard consists of a directed grid transition, a closure cell, and a Bernoulli closure probability. It becomes active only after the transition is executed. For position (x), active hazard set (H), and designated safe set (S), the reference quantity is

```
R(x, H) = P(a traversable path exists from x to S | H).
```

The current oracle exactly enumerates independent closures and is limited to small hazard sets. The planner searches states that include both position and activated-trigger history. It uses a soft recoverability penalty; it is not a chance-constrained safety guarantee.

## Evidence boundary and next steps

The repository contains a small analytic construction and software regression tests. They show that, under the stated model, histories ending at one position can have different return probabilities. They do not measure performance over a sampled environment distribution.

The frozen protocol in `docs/experimental_protocol.md` is a plan, not a report of completed experiments. A paper submission requires implemented and reproducible paired benchmarks against geometric, state-only marginal-risk, hard safe-return, and scalable-approximation baselines; retained raw trials and run metadata; uncertainty-aware reporting; and a broader literature review. Simulator or hardware claims require corresponding completed experiments.
