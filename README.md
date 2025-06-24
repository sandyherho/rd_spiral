# rd_spiral

Simple and efficient reaction-diffusion spiral wave solver using spectral methods.

## Features

- Fast spectral methods (FFT-based)
- Automatic equilibrium detection  
- Organized output structure
- Real-time progress updates
- Minimal dependencies

## Installation

```bash
pip install rd_spiral
```

For development:
```bash
git clone https://github.com/sandyherho/rd_spiral.git
cd rd_spiral
pip install -e .
```

## Quick Start

1. Run a stable spiral to equilibrium:
```bash
rd-spiral configs/stable_spiral.txt
```

2. Run pattern decay example:
```bash
rd-spiral configs/pattern_decay.txt
```

## Model

Reaction-diffusion system with cubic nonlinearity:
```
∂u/∂t = D₁∇²u + u - u³ - uv² + β(u²v + v³)
∂v/∂t = D₂∇²v + v - u²v - v³ - β(u³ + uv²)
```

## Examples

### Stable Spiral (Dynamic Equilibrium)
- Low diffusion (D₁ = D₂ = 0.1)
- Forms rotating spiral wave
- Statistics reach steady state

### Pattern Decay (Homogeneous Equilibrium)  
- High diffusion (D₁ = D₂ = 0.5)
- Pattern decays to uniform state
- Final state: u = v = 0

## Output Structure

Output files are saved in your current working directory:

```
outputs/
└── experiment_name_timestamp/
    ├── solution.nc    # Full spatiotemporal data
    ├── stats.csv      # Time series statistics
    └── config.txt     # Configuration used

logs/
└── experiment_name_timestamp/
    └── simulation.log # Detailed progress log
```

## Author

Sandy Herho <sandy.herho@email.ucr.edu>

## License

MIT License - see LICENSE file
