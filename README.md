# rd-spiral: An open-source Python library for learning 2D reaction-diffusion dynamics through pseudo-spectral method

[![DOI](https://zenodo.org/badge/1007472234.svg)](https://doi.org/10.5281/zenodo.15727991)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**rd-spiral**: An open-source Python library for investigating 2D reaction-diffusion dynamics through pseudo-spectral methods

## Overview

rd-spiral implements a mathematically rigorous framework for simulating spiral wave dynamics in reaction-diffusion systems. The library bridges theoretical formulations with practical implementation, providing transparent algorithms suitable for both educational exploration and research-quality investigations of pattern formation phenomena.

### Key Features

- **Pseudo-spectral spatial discretization** with exponential convergence for smooth solutions
- **Adaptive time integration** (Dormand-Prince RK5(4)) handling stiffness ratios exceeding 6:1
- **Comprehensive statistical analysis** framework for quantifying dynamical regimes
- **Information-theoretic measures** for pattern complexity characterization
- **Robust output preservation** with checkpoint mechanisms for extended simulations

## Scientific Background

The library implements the dimensionless reaction-diffusion system:

$$\frac{\partial u}{\partial t} = D_1\nabla^2 u + u - u^3 - uv^2 + \beta(u^2v + v^3)$$

$$\frac{\partial v}{\partial t} = D_2\nabla^2 v + v - u^2v - v^3 - \beta(u^3 + uv^2)$$

where $D_1$, $D_2$ are diffusion coefficients and $\beta$ is the coupling parameter controlling non-equilibrium dynamics.

## Installation

### Requirements

- Python ≥ 3.8
- NumPy ≥ 1.20.0
- SciPy ≥ 1.7.0
- pandas ≥ 1.3.0
- xarray ≥ 0.19.0
- netCDF4 ≥ 1.5.7

### Install from GitHub

```bash
pip install git+https://github.com/sandyherho/rd_spiral.git
```

### Development Installation

```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Execute pre-configured simulations
rd-spiral configs/stable_spiral.txt      # Stable rotating spiral
rd-spiral configs/turbulent_spiral.txt   # Spatiotemporal chaos
rd-spiral configs/pattern_decay.txt      # Diffusion-dominated decay
```

### Python API

```python
from rd_spiral import ReactionDiffusionSolver, parse_config

# Load configuration
config = parse_config('configs/stable_spiral.txt')

# Initialize and run solver
solver = ReactionDiffusionSolver(config)
solver.run()
```

## Parameter Regimes

The library includes three validated parameter configurations demonstrating distinct dynamical behaviors:

| Configuration | D₁ | D₂ | β | Behavior |
|--------------|----|----|---|----------|
| Stable Spiral | 0.1 | 0.1 | 1.0 | Coherent rotation, dynamic equilibrium |
| Turbulent | 0.03 | 0.20 | 0.65 | Spiral breakup, persistent chaos |
| Pattern Decay | 0.5 | 0.5 | 1.0 | Homogeneous state, exponential decay |

## Output Structure

```
rd_outputs/
├── stable_spiral/
│   ├── solution.nc          # Full spatiotemporal data (NetCDF4)
│   ├── stats.csv           # Time series statistics
│   ├── config.txt          # Simulation parameters
│   └── initial_conditions.npz
└── turbulent_spiral/
    ├── solution.nc
    ├── stats.csv
    ├── checkpoints/        # Intermediate states for long runs
    └── simulation_status.txt
```

## Scientific Applications

This implementation has been validated for investigating:
- Spiral wave stability and bifurcations in excitable media
- Defect-mediated turbulence in pattern-forming systems
- Information-theoretic characterization of spatiotemporal chaos
- Non-Gaussian statistics in deterministic dynamical systems

## Citation

If you use rd-spiral in your research, please cite:

```bibtex
@article{herho2025rdspiral,
  author = {Herho, S. H. S. and Anwar, I. P. and Suwarman, R.},
  title = {{rd-spiral: An open-source Python library for learning 
           2D reaction-diffusion dynamics through pseudo-spectral methods}},
  journal = {[xxxx]},
  year = {202x},
  volume = {XX},
  pages = {XX--XX},
  doi = {10.XXXX/XXXXXXX}
}
```

## Contributing

We welcome contributions that maintain the library's emphasis on pedagogical clarity and mathematical rigor. Please ensure all code follows PEP 8 standards and includes comprehensive documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This work was supported by the Dean's Distinguished Fellowship from CNAS at UC Riverside (2023) and ITB Research, Community Service and Innovation Program (PPMI-ITB) in 2025.
