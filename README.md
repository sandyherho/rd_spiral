# rd_spiral

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXX)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/rd-spiral/badge/?version=latest)](https://rd-spiral.readthedocs.io/en/latest/?badge=latest)

A high-performance Python package for simulating reaction-diffusion spiral waves using pseudo-spectral methods.

## Table of Contents

- [Overview](#overview)
- [Mathematical Model](#mathematical-model)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Examples](#examples)
- [Output Structure](#output-structure)
- [Configuration](#configuration)
- [Performance](#performance)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)
- [Author](#author)

## Overview

`rd_spiral` is a specialized solver for reaction-diffusion partial differential equations (PDEs) that exhibit spiral wave dynamics. The package implements state-of-the-art pseudo-spectral methods for high accuracy spatial discretization combined with adaptive time integration. This approach is particularly efficient for studying pattern formation, chemical waves, and biological dynamics on periodic domains.

### Applications

- **Cardiac dynamics**: Modeling electrical spiral waves in heart tissue
- **Chemical reactions**: Belousov-Zhabotinsky and other oscillating reactions  
- **Biological patterns**: Morphogenesis, population dynamics, and ecological systems
- **Materials science**: Phase transitions and crystal growth patterns

## Mathematical Model

### Governing Equations

The package solves the following system of reaction-diffusion PDEs:

```
∂u/∂t = D₁∇²u + f(u,v)
∂v/∂t = D₂∇²v + g(u,v)
```

where `u` and `v` are the two chemical species concentrations, `D₁` and `D₂` are their respective diffusion coefficients, and the reaction terms are:

```
f(u,v) = u - u³ - uv² + β(u²v + v³)
g(u,v) = v - u²v - v³ - β(u³ + uv²)
```

### Nondimensionalization

The equations have been nondimensionalized such that:
- Concentrations `u,v ∈ [-1, 1]` typically
- Length scale is relative to domain size `L`
- Time scale is set by the reaction rates
- The parameter `β` controls the spiral wave dynamics

### Numerical Method

The solver employs a **pseudo-spectral method** which combines:

1. **Spatial discretization**: Fast Fourier Transform (FFT) for spectral accuracy
   - Periodic boundary conditions
   - Exponential convergence for smooth solutions
   - Efficient O(N log N) complexity

2. **Time integration**: Adaptive Runge-Kutta methods
   - Default: RK45 (4th/5th order embedded pair)
   - Automatic error control
   - Efficient for stiff-nondominant systems

### Linear Stability Analysis

The homogeneous steady state (u,v) = (0,0) has eigenvalues λ = 1, indicating instability. This instability, combined with diffusion, leads to pattern formation. The type of pattern depends on:
- Diffusion ratio `D₂/D₁`
- Reaction parameter `β`
- Initial conditions

## Features

- 🚀 **High Performance**: Optimized FFT-based spatial discretization
- 🎯 **Accuracy**: Spectral accuracy in space, adaptive high-order time integration  
- 🔄 **Pattern Detection**: Automatic equilibrium state classification
- 📊 **Comprehensive Output**: Full spatiotemporal data + statistical analysis
- 🛠️ **Flexible Configuration**: Easy parameter adjustment via text files
- 📈 **Real-time Monitoring**: Progress tracking and performance metrics
- 🗂️ **Organized Storage**: Systematic output directory structure

## Installation

### Requirements

- Python 3.8 or higher
- NumPy >= 1.20.0
- SciPy >= 1.7.0  
- pandas >= 1.3.0
- xarray >= 0.19.0
- netCDF4 >= 1.5.7

### Install from PyPI (coming soon)

```bash
pip install rd-spiral
```

### Install from source

```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e .
```

### Development installation

```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e ".[dev]"
```

## Quick Start

1. **Run a stable spiral simulation**:
```bash
rd-spiral configs/stable_spiral.txt
```

2. **Run a turbulent simulation**:
```bash
rd-spiral configs/turbulent_spiral.txt
```

3. **Compare different dynamics**:
```bash
python examples/compare_spiral_behaviors.py
```

## Usage

### Command Line Interface

The primary interface is through the command line:

```bash
rd-spiral <config_file>
```

Where `<config_file>` is a text file specifying simulation parameters.

### Python API

For programmatic use:

```python
from rd_spiral import ReactionDiffusionSolver, parse_config

# Load configuration
config = parse_config('configs/stable_spiral.txt')

# Create and run solver
solver = ReactionDiffusionSolver(config)
solver.run()
```

### Custom configurations

```python
# Define parameters directly
config = {
    'd1': 0.1,          # Diffusion coefficient for u
    'd2': 0.1,          # Diffusion coefficient for v  
    'beta': 1.0,        # Reaction parameter
    'L': 20.0,          # Domain size
    'n': 128,           # Grid points per dimension
    't_start': 0.0,     # Start time
    't_end': 200.0,     # End time
    'dt': 0.1,          # Time step for output
    'num_spiral_arms': 1  # Initial condition
}

solver = ReactionDiffusionSolver(config)
solver.run()
```

## Examples

### 1. Stable Spiral Wave

Forms a rotating spiral that reaches dynamic equilibrium:

```bash
rd-spiral configs/stable_spiral.txt
```

**Parameters**: `D₁ = D₂ = 0.1`, `β = 1.0`  
**Behavior**: Regular rotation with constant amplitude

### 2. Pattern Decay

High diffusion causes pattern to decay to homogeneous state:

```bash
rd-spiral configs/pattern_decay.txt
```

**Parameters**: `D₁ = D₂ = 0.5`, `β = 1.0`  
**Behavior**: Exponential decay to (u,v) = (0,0)

### 3. Turbulent Dynamics

Mismatched diffusion creates spiral breakup and chaos:

```bash
rd-spiral configs/turbulent_spiral.txt
```

**Parameters**: `D₁ = 0.05`, `D₂ = 0.15`, `β = 0.7`  
**Behavior**: Spiral breakup, spatiotemporal chaos

## Output Structure

Results are organized in a clear directory structure:

```
rd_outputs/
├── stable_spiral/
│   ├── solution.nc      # Full spatiotemporal data (NetCDF)
│   ├── stats.csv        # Time series of statistics
│   └── config.txt       # Parameters used
├── turbulent_spiral/
│   └── ...
└── pattern_decay/
    └── ...

rd_logs/
├── stable_spiral/
│   └── simulation.log   # Detailed execution log
└── ...
```

### Output Files

1. **`solution.nc`**: Complete solution data in NetCDF format
   - Variables: `u(x,y,t)`, `v(x,y,t)`
   - Compressed for efficient storage
   - Includes metadata and parameters

2. **`stats.csv`**: Time series statistics
   - Mean, std, min, max for both species
   - Useful for equilibrium detection
   - Easy plotting with pandas

3. **`config.txt`**: Complete configuration record
   - All parameters used
   - Timestamp and version info
   - Reproducibility guaranteed

## Configuration

Configuration files use a simple key-value format:

```ini
# Diffusion coefficients
d1 = 0.1
d2 = 0.1

# Reaction parameter
beta = 1.0

# Domain and discretization
L = 20.0      # Domain size (L × L)
n = 128       # Grid points (n × n)

# Time integration
t_start = 0.0
t_end = 200.0
dt = 0.1      # Output time step

# Numerical parameters
method = RK45
rtol = 1e-6
atol = 1e-9

# Initial conditions
num_spiral_arms = 1

# Output options
save_netcdf = true
```

## Performance

The pseudo-spectral method offers excellent performance:

- **Spatial complexity**: O(N log N) per time step via FFT
- **Temporal complexity**: Adaptive, typically O(T/ε) for accuracy ε  
- **Memory usage**: O(N) for computation, O(NT) for storage
- **Parallel potential**: FFTs are highly optimizable

Typical performance on modern hardware:
- 128×128 grid: ~10-20 time units/second
- 256×256 grid: ~2-5 time units/second
- 512×512 grid: ~0.5-1 time units/second

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development setup

```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e ".[dev]"
pre-commit install
```

### Running tests

```bash
pytest tests/
```

## Citation

If you use this software in your research, please cite:

### Software

```bibtex
@software{herho2025rdspiral,
  author       = {Herho, Sandy H. S.},
  title        = {rd_spiral: A Python package for reaction-diffusion spiral wave simulations},
  month        = jun,
  year         = 2025,
  publisher    = {Zenodo},
  version      = {v0.1.0},
  doi          = {10.5281/zenodo.XXXXXX},
  url          = {https://doi.org/10.5281/zenodo.XXXXXX}
}
```

### Paper (forthcoming)

```bibtex
@article{herho2025spiral,
  author       = {Herho, Sandy H. S.},
  title        = {Efficient pseudo-spectral methods for reaction-diffusion spiral wave dynamics},
  journal      = {Journal of Computational Physics},
  year         = {2025},
  volume       = {XXX},
  pages        = {XXX-XXX},
  doi          = {10.1016/j.jcp.2025.XXXXXX}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Sandy Herho**  
PhD Candidate  
Department of Environmental Sciences  
University of California, Riverside  
Email: sandy.herho@email.ucr.edu  
ORCID: [0000-0002-XXXX-XXXX](https://orcid.org/0000-0002-XXXX-XXXX)

---

<p align="center">
  Made with ❤️ for the scientific community
</p>
