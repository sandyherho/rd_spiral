#!/usr/bin/env python
"""Simple example of running rd_spiral."""

from rd_spiral import parse_config, ReactionDiffusionSolver

# Create simple config dict
config = {
    'd1': 0.1,
    'd2': 0.1,
    'beta': 1.0,
    'L': 20.0,
    'n': 64,
    't_start': 0.0,
    't_end': 50.0,
    'dt': 0.1,
    'num_spiral_arms': 1
}

# Run simulation
solver = ReactionDiffusionSolver(config)
solver.run()

print("Done! Check ../outputs/ folder (outside package directory)")
