#!/usr/bin/env python
"""
compare_spiral_behaviors.py
Run and compare stable vs turbulent spiral waves

This script demonstrates how different parameter choices lead to 
fundamentally different dynamics in reaction-diffusion systems.

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def run_simulation(config_name: str) -> str:
    """
    Run a simulation and return the output directory path.
    
    Args:
        config_name: Name of config file (without .txt extension)
    
    Returns:
        Path to output directory containing results
    """
    print(f"\n{'='*60}")
    print(f"Running {config_name}...")
    print('='*60)
    
    # Run the simulation using CLI
    cmd = f"rd-spiral configs/{config_name}.txt"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running simulation: {result.stderr}")
        raise RuntimeError(f"Simulation failed for {config_name}")
    
    # Output directory is in rd_outputs/config_name/
    output_dir = Path("../rd_outputs") / config_name
    
    if not output_dir.exists():
        raise RuntimeError(f"Output directory not found: {output_dir}")
    
    return str(output_dir)


def plot_comparison(stable_dir: str, turbulent_dir: str) -> None:
    """
    Create comparison plots of stable vs turbulent dynamics.
    
    This function generates visualizations that highlight the key
    differences between stable spiral rotation and turbulent/chaotic
    dynamics.
    
    Args:
        stable_dir: Path to stable spiral results
        turbulent_dir: Path to turbulent spiral results
    """
    # Load statistics from both simulations
    stable_stats = pd.read_csv(os.path.join(stable_dir, 'stats.csv'))
    turbulent_stats = pd.read_csv(os.path.join(turbulent_dir, 'stats.csv'))
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Stable vs Turbulent Spiral Wave Dynamics', fontsize=16)
    
    # Plot 1: Pattern intensity (u_std) over time
    ax = axes[0, 0]
    ax.plot(stable_stats['time'], stable_stats['u_std'], 
            'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['time'], turbulent_stats['u_std'], 
            'r-', label='Turbulent', linewidth=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('Pattern Intensity (u std dev)')
    ax.set_title('Temporal Evolution of Pattern Intensity')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Phase space trajectory (u_mean vs v_mean)
    ax = axes[0, 1]
    ax.plot(stable_stats['u_mean'], stable_stats['v_mean'], 
            'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['u_mean'], turbulent_stats['v_mean'], 
            'r-', label='Turbulent', linewidth=2, alpha=0.7)
    ax.set_xlabel('Mean u')
    ax.set_ylabel('Mean v')
    ax.set_title('Phase Space Trajectory')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')
    
    # Plot 3: Late-time dynamics (zoomed)
    ax = axes[1, 0]
    # Show last 25% of simulation time
    stable_end = int(0.75 * len(stable_stats))
    turbulent_end = int(0.75 * len(turbulent_stats))
    
    ax.plot(stable_stats['time'][stable_end:], 
            stable_stats['u_std'][stable_end:], 
            'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['time'][turbulent_end:], 
            turbulent_stats['u_std'][turbulent_end:], 
            'r-', label='Turbulent', linewidth=2, alpha=0.7)
    ax.set_xlabel('Time')
    ax.set_ylabel('Pattern Intensity (u std dev)')
    ax.set_title('Late-Time Dynamics (Equilibrium Behavior)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Quantitative analysis summary
    ax = axes[1, 1]
    ax.axis('off')
    
    # Calculate equilibrium statistics (last 10% of simulation)
    n_eq = int(0.1 * len(stable_stats))
    
    stable_mean_std = stable_stats['u_std'].iloc[-n_eq:].mean()
    stable_var_std = stable_stats['u_std'].iloc[-n_eq:].std()
    turbulent_mean_std = turbulent_stats['u_std'].iloc[-n_eq:].mean()
    turbulent_var_std = turbulent_stats['u_std'].iloc[-n_eq:].std()
    
    # Calculate spectral properties (simplified)
    stable_range = stable_stats['u_std'].iloc[-n_eq:].max() - stable_stats['u_std'].iloc[-n_eq:].min()
    turbulent_range = turbulent_stats['u_std'].iloc[-n_eq:].max() - turbulent_stats['u_std'].iloc[-n_eq:].min()
    
    summary_text = f"""
Equilibrium Analysis (last 10% of simulation):

Stable Spiral:
  • Mean intensity: {stable_mean_std:.6f}
  • Variation: {stable_var_std:.6f}
  • Range: {stable_range:.6f}
  • State: {"Dynamic equilibrium" if stable_var_std < 0.001 else "Evolving"}
  
Turbulent Spiral:
  • Mean intensity: {turbulent_mean_std:.6f}
  • Variation: {turbulent_var_std:.6f}
  • Range: {turbulent_range:.6f}
  • State: {"Chaotic/turbulent" if turbulent_var_std > 0.001 else "Stabilized"}

Key Metrics:
  • Variation ratio: {turbulent_var_std/stable_var_std:.1f}x
  • Range ratio: {turbulent_range/stable_range:.1f}x
  • Chaos indicator: {turbulent_var_std/turbulent_mean_std:.3f}
"""
    
    ax.text(0.05, 0.5, summary_text, transform=ax.transAxes, 
            fontsize=10, verticalalignment='center', 
            fontfamily='monospace')
    
    plt.tight_layout()
    
    # Save figure
    output_path = 'spiral_comparison.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✅ Saved comparison plot: {output_path}")
    
    # Create additional detailed plot
    fig2, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Top: Full time series
    ax1.plot(stable_stats['time'], stable_stats['u_std'], 
             'b-', label='Stable spiral', linewidth=2)
    ax1.plot(turbulent_stats['time'], turbulent_stats['u_std'], 
             'r-', label='Turbulent spiral', linewidth=2, alpha=0.7)
    ax1.set_ylabel('Pattern Intensity')
    ax1.set_title('Pattern Evolution: Stable vs Turbulent Dynamics')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Bottom: Difference plot
    # Interpolate to common time grid if needed
    min_len = min(len(stable_stats), len(turbulent_stats))
    diff = np.abs(stable_stats['u_std'][:min_len].values - 
                  turbulent_stats['u_std'][:min_len].values)
    ax2.plot(stable_stats['time'][:min_len], diff, 'k-', linewidth=2)
    ax2.set_xlabel('Time')
    ax2.set_ylabel('|Difference|')
    ax2.set_title('Absolute Difference in Pattern Intensity')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('pattern_intensity_detailed.png', dpi=150, bbox_inches='tight')
    print(f"✅ Saved detailed plot: pattern_intensity_detailed.png")
    
    plt.close('all')


def main():
    """
    Main function to run comparison between stable and turbulent spirals.
    
    This demonstrates how parameter choices dramatically affect the
    long-term behavior of reaction-diffusion systems.
    """
    print("="*60)
    print("SPIRAL WAVE DYNAMICS COMPARISON")
    print("Stable vs Turbulent Behavior Analysis")
    print("="*60)
    
    # Check for required config files
    required_configs = ['configs/stable_spiral.txt', 'configs/turbulent_spiral.txt']
    for config in required_configs:
        if not os.path.exists(config):
            print(f"❌ Required config not found: {config}")
            print("Please ensure you're running from the rd_spiral directory")
            return
    
    try:
        # Run both simulations
        print("\n📊 Running simulations...")
        stable_dir = run_simulation('stable_spiral')
        turbulent_dir = run_simulation('turbulent_spiral')
        
        # Generate comparison plots
        print(f"\n📈 Creating comparison plots...")
        plot_comparison(stable_dir, turbulent_dir)
        
        # Print summary
        print(f"\n{'='*60}")
        print("COMPARISON COMPLETE!")
        print("="*60)
        
        print("\n🔍 Key Observations:")
        print("\n1. STABLE SPIRAL (D₁=D₂=0.1, β=1.0):")
        print("   • Reaches dynamic equilibrium")
        print("   • Regular, periodic rotation")
        print("   • Constant pattern intensity")
        print("   • Predictable long-term behavior")
        
        print("\n2. TURBULENT SPIRAL (D₁=0.05, D₂=0.15, β=0.7):")
        print("   • Never reaches equilibrium")
        print("   • Chaotic, irregular dynamics")
        print("   • Fluctuating pattern intensity")
        print("   • Spiral breakup and reformation")
        
        print("\n3. PHYSICAL INTERPRETATION:")
        print("   • Stable: Like regular heartbeat")
        print("   • Turbulent: Like cardiac fibrillation")
        print("   • Parameter space exhibits bifurcations")
        
        print("\n📁 Results saved in:")
        print(f"   • {stable_dir}")
        print(f"   • {turbulent_dir}")
        print("   • ./spiral_comparison.png")
        print("   • ./pattern_intensity_detailed.png")
        
    except Exception as e:
        print(f"\n❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check for matplotlib
    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
    except ImportError:
        print("❌ Error: matplotlib is required for plotting")
        print("Install with: pip install matplotlib")
        exit(1)
    
    main()
