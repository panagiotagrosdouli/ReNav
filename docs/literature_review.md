# Literature review: first verified pass

This is a seed matrix, not a completed systematic review.

| Work | Venue/year | Relevance | Boundary vs ReNav |
|---|---|---|---|
| Guo et al., *Hierarchical Motion Planning under Probabilistic Temporal Tasks and Safe-Return Constraints* | 2023 | Explicit high-probability return policies in an MDP | Safe return is established prior art; ReNav must distinguish action-triggered return-topology state/history. |
| Indelman, Carlone & Dellaert, *Planning in the continuous domain: A generalized belief space approach for autonomous navigation in unknown environments* | IJRR 2015 | Joint state/environment belief for planning | Belief-space state augmentation is established; ReNav cannot claim state augmentation itself as novel. |
| Prentice & Roy, *The Belief Roadmap* | IJRR 2009 | Efficient belief-space planning | Establishes long-standing planning over uncertainty. |
| Axelrod, Kaelbling & Lozano-Pérez, *Provably Safe Robot Navigation with Obstacle Uncertainty* | 2017 | Probabilistic trajectory/policy safety under uncertain obstacles | Safety under uncertain maps is not the gap. |
| Liniger & Van Gool, *Safe Motion Planning for Autonomous Driving using an Adversarial Road Model* | RSS 2020 | Viability/safe sets as planning constraints | Viability/reachability is a strong conceptual baseline. |
| Thananjeyan et al., *Recovery RL: Safe Reinforcement Learning With Learned Recovery Zones* | RA-L 2021 | Learned recovery policy/regions | Recovery-aware decision making is prior art; ReNav differs in explicit return-connectivity consequences of executed triggers. |
| *History-Aware Planning for Risk-free Autonomous Navigation on Unknown Uneven Terrain* | ICRA 2024 | Maintains exploration history in global graph | "History-aware navigation" terminology is already occupied; novelty wording must be narrower. |
| de Groot et al., *Scenario-based motion planning with bounded probability of collision* | IJRR 2025 | Joint chance-constrained motion planning | Strong modern comparator for uncertainty/risk methodology, but focuses collision probability rather than action-triggered return connectivity. |

## Synthesis
The defensible question is not whether history, uncertainty, safety, or return policies matter; all are established. The unresolved point to test is whether an explicit executed-action-triggered topology process creates a practically important information gap for state-only marginal return-risk planners, and whether that gap can be handled scalably under uncertain model parameters.
