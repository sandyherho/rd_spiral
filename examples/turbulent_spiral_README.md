# Turbulent Spiral Wave Example

This example demonstrates how parameter choices can lead to turbulent/chaotic behavior in reaction-diffusion systems.

## Key Parameters for Turbulence

1. **Mismatched diffusion coefficients**: 
   - d1 = 0.05 (slow diffusion for u)
   - d2 = 0.15 (fast diffusion for v)
   - The 3:1 ratio creates instabilities

2. **Reaction parameter**: 
   - beta = 0.7 (promotes spiral breakup)

3. **Initial conditions**:
   - 3 spiral arms (more complex initial pattern)

## Expected Behavior

Unlike the stable spiral that reaches a dynamic equilibrium with regular rotation, the turbulent configuration shows:

- **Spiral breakup**: The initial spiral arms break into multiple smaller spirals
- **Irregular dynamics**: No steady state is reached
- **Spatiotemporal chaos**: Complex, aperiodic patterns
- **Large fluctuations**: Pattern intensity varies significantly over time

## Physical Interpretation

This turbulent behavior is analogous to:
- Cardiac arrhythmias (fibrillation)
- Chemical turbulence in BZ reactions
- Ecological pattern formation with predator-prey dynamics

## Running the Example

1. Single run:
   ```bash
   rd-spiral configs/turbulent_spiral.txt
   ```

2. Compare with stable case:
   ```bash
   cd rd_spiral
   python examples/compare_spiral_behaviors.py
   ```

The comparison script will:
- Run both stable and turbulent simulations
- Generate comparison plots
- Analyze the differences in dynamics

## Parameter Exploration

Try varying:
- **Diffusion ratio**: Larger d2/d1 increases turbulence
- **Beta**: Values around 0.6-0.8 often show interesting dynamics
- **Domain size**: Larger domains allow more complex patterns
- **Initial spiral arms**: More arms = more initial complexity
