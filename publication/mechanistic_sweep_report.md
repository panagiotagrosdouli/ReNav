# Canonical mechanism sweep: results and provenance

## Scope

This is a single constructed 4-by-3 grid. It tests the intended mechanism and route-level trade-off; it does not sample maps and cannot support a map-generalization or real-world efficacy claim.

The outbound start is (0,1), the goal is (3,1), and the safe set is {(0,1)}. Static obstacles are (1,0) and (1,2). Traversing the directed edge (2,1)->(3,1) activates a Bernoulli closure of (1,1). The direct route has length 3 and activates the hazard; a length-5 route avoids it. Closing (1,1) makes return to the safe set impossible.

## Protocol and retained data

- Command: `python experiments/run_mechanistic_sweep.py --trials 10000 --seed 20260924`
- Closure probabilities: 0.1, 0.2, 0.4, 0.6, 0.8, 0.9.
- Planners: geometric shortest path; hard return threshold 0.8; history-conditioned A* with weights 0, 1, 2, 4, and 8.
- Pairing: all planners share the same uniform variate for each trial at each closure probability.
- Outcomes: mission-and-return success, route length, activated hazards, exact success probability, Wilson 95% intervals, and paired success difference versus geometric with a paired Wald 95% interval.
- Summary table: [`results/mechanistic_sweep.csv`](../results/mechanistic_sweep.csv).
- Figure: [`publication/figures/mechanistic_sweep.svg`](figures/mechanistic_sweep.svg).
- Raw trials: GitHub Actions artifact from run [35979953475](https://github.com/panagiotagrosdouli/ReNav/actions/runs/35979953475), artifact ID `10799716911`, 60,000 rows. The ZIP artifact SHA-256 is `7c1f5d003140f1ba68f6fd51249d1cc7f7e1081873c691988b27539c28d7936a`. The artifact expires on 2026-12-23; archive the raw CSV in a permanent repository release or DOI-backed archive before submission.

## Selected results

Success is the probability of reaching the goal and then returning to the safe set. Values are empirical over 10,000 paired draws; intervals in parentheses are Wilson 95% intervals. The paired difference is the change in success rate against geometric and uses a paired Wald 95% interval.

| Closure probability | Geometric success | Hard threshold 0.8 | History A*, weight 4 | Paired gain, hard vs geometric |
|---:|---:|---:|---:|---:|
| 0.1 | 0.9004 (0.8944–0.9061) | 0.9004 (0.8944–0.9061) | 0.9004 (0.8944–0.9061) | 0.0000 |
| 0.2 | 0.8012 (0.7933–0.8089) | 0.8012 (0.7933–0.8089) | 0.8012 (0.7933–0.8089) | 0.0000 |
| 0.4 | 0.6007 (0.5911–0.6103) | 1.0000 (0.9996–1.0000) | 0.6007 (0.5911–0.6103) | 0.3993 (0.3897–0.4089) |
| 0.6 | 0.3993 (0.3897–0.4089) | 1.0000 (0.9996–1.0000) | 1.0000 (0.9996–1.0000) | 0.6007 (0.5911–0.6103) |
| 0.8 | 0.2005 (0.1928–0.2085) | 1.0000 (0.9996–1.0000) | 1.0000 (0.9996–1.0000) | 0.7995 (0.7917–0.8073) |
| 0.9 | 0.1000 (0.0943–0.1060) | 1.0000 (0.9996–1.0000) | 1.0000 (0.9996–1.0000) | 0.9000 (0.8941–0.9059) |

At p=0.4, the weight-4 planner keeps the short route while the hard threshold selects the longer route. At p≥0.6, weight 4 and the hard threshold select the same safe detour. At p≤0.2, both keep the short route. This is evidence that a hard constraint can match the soft objective in the constructed regimes; it is also a direct limit on any claim that the soft objective is superior.

The empirical success rates closely match the exact route-level probabilities for this fixed map. Repeated Bernoulli draws quantify simulation noise; they do not create 10,000 independent environments. The six closure probabilities and the planner weights were evaluated on one map.

## Reproducibility

The CSV includes the seed, trial count, route selected, exact success probability, empirical success, confidence limits, and paired effect. The raw artifact stores every common random draw and every planner's binary outcome. Re-run from the repository root with the command above. The figure is regenerated with:

```bash
python -m pip install -e '.[plots]'
python publication/plot_mechanistic_sweep.py
```

The benchmark implementation, analysis fields, summary, and figure are versioned in this PR. The raw artifact should be transferred to a durable release or data repository before a journal submission.
