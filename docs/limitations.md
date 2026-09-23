# Limitations

The foundational model is deliberately narrow: static 4-connected grids; known directed trigger transitions; known safe set; independent Bernoulli future closures; exact enumeration only for small unresolved hazard sets; no robot dynamics, localization uncertainty, perception model, or learned calibration.

Therefore current results cannot establish real-world safety, general map performance, physical-robot efficacy, calibrated probabilities, or universal superiority. A state-only baseline is only meaningful if its information restriction is stated precisely; a richer Markov state or POMDP can encode history through environment state.

The central novelty claim remains provisional pending a broader verified literature review. The most important engineering validation still missing is execution-level reproduction with Nav2/Gazebo under sensing and replanning delays.
