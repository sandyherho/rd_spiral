# rd_spiral

Reaction-diffusion spiral wave solver using pseudo-spectral methods.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/sandyherho/rd_spiral.git
```

Or clone for development:

```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e .
```

## Requirements

- Python ≥ 3.8
- numpy ≥ 1.20.0
- scipy ≥ 1.7.0
- pandas ≥ 1.3.0
- xarray ≥ 0.19.0
- netCDF4 ≥ 1.5.7

## Usage

```bash
# Run simulations
rd-spiral configs/stable_spiral.txt
rd-spiral configs/turbulent_spiral.txt

# Python API
from rd_spiral import ReactionDiffusionSolver, parse_config

config = parse_config('configs/stable_spiral.txt')
solver = ReactionDiffusionSolver(config)
solver.run()
```

## Model

Reaction-diffusion system with cubic nonlinearity:

$$\frac{\partial u}{\partial t} = D_1\nabla^2 u + u - u^3 - uv^2 + \beta(u^2v + v^3)$$

$$\frac{\partial v}{\partial t} = D_2\nabla^2 v + v - u^2v - v^3 - \beta(u^3 + uv^2)$$

where $D_1$, $D_2$ are diffusion coefficients and $\beta$ is the reaction parameter.

## Examples

### Stable Spiral
```bash
rd-spiral configs/stable_spiral.txt
```
- Low diffusion (D₁ = D₂ = 0.1)
- Forms rotating spiral wave
- Reaches dynamic equilibrium

### Turbulent Spiral
```bash
rd-spiral configs/turbulent_spiral.txt
```
- Mismatched diffusion (D₁ = 0.05, D₂ = 0.15)
- Shows chaotic dynamics
- Spiral breakup

## Output Structure

```
rd_outputs/             # Results organized by config name
├── stable_spiral/
├── turbulent_spiral/
└── pattern_decay/

rd_logs/                # Simulation logs
```

## Citation

```bibtex
@software{herho2025rdspiral,
  author = {Herho, Sandy H. S.},
  title = {rd_spiral: Reaction-diffusion spiral wave solver},
  year = {2025},
  url = {https://github.com/sandyherho/rd_spiral}
}
```

## Author

Sandy Herho  
University of California, Riverside  
sandy.herho@email.ucr.edu

## License

MIT License
