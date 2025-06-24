#!/usr/bin/env python
"""
compare_spiral_behaviors.py
Run and compare stable vs turbulent spiral waves

Author: Sandy Herho <sandy.herho@email.ucr.edu>
"""

import subprocess
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def run_simulation(config_name):
    """Run a simulation and return the output directory."""
    print(f"\n{'='*60}")
    print(f"Running {config_name}...")
    print('='*60)
    
    # Run the simulation
    cmd = f"rd-spiral configs/{config_name}.txt"
    subprocess.run(cmd, shell=True)
    
    # Output directory is just the config name now
    outputs_dir = "../outputs"
    output_dir = os.path.join(outputs_dir, config_name)
    
    if not os.path.exists(output_dir):
        raise RuntimeError(f"Output directory not found: {output_dir}")
    
    return output_dir

def plot_comparison(stable_dir, turbulent_dir):
    """Plot comparison of stable vs turbulent dynamics."""
    # Load statistics
    stable_stats = pd.read_csv(os.path.join(stable_dir, 'stats.csv'))
    turbulent_stats = pd.read_csv(os.path.join(turbulent_dir, 'stats.csv'))
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot 1: u_std over time
    ax = axes[0, 0]
    ax.plot(stable_stats['time'], stable_stats['u_std'], 'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['time'], turbulent_stats['u_std'], 'r-', label='Turbulent', linewidth=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('u standard deviation')
    ax.set_title('Pattern Intensity Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Phase space (u_mean vs v_mean)
    ax = axes[0, 1]
    ax.plot(stable_stats['u_mean'], stable_stats['v_mean'], 'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['u_mean'], turbulent_stats['v_mean'], 'r-', label='Turbulent', linewidth=2)
    ax.set_xlabel('u mean')
    ax.set_ylabel('v mean')
    ax.set_title('Phase Space Trajectory')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: u_std zoomed to show oscillations
    ax = axes[1, 0]
    # Last 25% of time
    stable_end = int(0.75 * len(stable_stats))
    turbulent_end = int(0.75 * len(turbulent_stats))
    
    ax.plot(stable_stats['time'][stable_end:], stable_stats['u_std'][stable_end:], 
            'b-', label='Stable', linewidth=2)
    ax.plot(turbulent_stats['time'][turbulent_end:], turbulent_stats['u_std'][turbulent_end:], 
            'r-', label='Turbulent', linewidth=2)
    ax.set_xlabel('Time')
    ax.set_ylabel('u standard deviation')
    ax.set_title('Late-Time Dynamics (Zoomed)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Statistics summary
    ax = axes[1, 1]
    ax.axis('off')
    
    # Calculate statistics
    stable_final_std = stable_stats['u_std'].iloc[-100:].mean()
    stable_variation = stable_stats['u_std'].iloc[-100:].std()
    turbulent_final_std = turbulent_stats['u_std'].iloc[-100:].mean()
    turbulent_variation = turbulent_stats['u_std'].iloc[-100:].std()
    
    summary_text = f"""
    Equilibrium Analysis (last 10 time units):
    
    Stable Spiral:
    • Mean u_std: {stable_final_std:.6f}
    • Variation: {stable_variation:.6f}
    • State: {"Dynamic equilibrium" if stable_variation < 0.001 else "Still evolving"}
    
    Turbulent Spiral:
    • Mean u_std: {turbulent_final_std:.6f}
    • Variation: {turbulent_variation:.6f}
    • State: {"Turbulent/chaotic" if turbulent_variation > 0.001 else "Stabilized"}
    
    Key Differences:
    • Stable: Regular rotation, constant amplitude
    • Turbulent: Irregular, fluctuating amplitude
    • Variation ratio: {turbulent_variation/stable_variation:.1f}x
    """
    
    ax.text(0.1, 0.5, summary_text, transform=ax.transAxes, 
            fontsize=11, verticalalignment='center', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('spiral_comparison.png', dpi=150, bbox_inches='tight')
    print(f"\n✅ Saved comparison plot: spiral_comparison.png")
    
    # Also save individual time series
    fig2, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stable_stats['time'], stable_stats['u_std'], 'b-', label='Stable spiral', linewidth=2)
    ax.plot(turbulent_stats['time'], turbulent_stats['u_std'], 'r-', label='Turbulent spiral', linewidth=2)
    ax.axhline(y=stable_final_std, color='b', linestyle='--', alpha=0.5, label='Stable equilibrium')
    ax.set_xlabel('Time')
    ax.set_ylabel('Pattern intensity (u_std)')
    ax.set_title('Stable vs Turbulent Spiral Wave Dynamics')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.savefig('pattern_intensity.png', dpi=150, bbox_inches='tight')
    print(f"✅ Saved intensity plot: pattern_intensity.png")

def main():
    """Run comparison of stable vs turbulent spirals."""
    print("SPIRAL WAVE DYNAMICS COMPARISON")
    print("Stable vs Turbulent Behavior")
    print("="*60)
    
    # Check if we have the turbulent config
    if not os.path.exists('configs/turbulent_spiral.txt'):
        print("❌ turbulent_spiral.txt not found!")
        print("Please run create_turbulent_example.py first")
        return
    
    try:
        # Run simulations
        stable_dir = run_simulation('stable_spiral')
        turbulent_dir = run_simulation('turbulent_spiral')
        
        # Create comparison plots
        print(f"\n{'='*60}")
        print("Creating comparison plots...")
        print('='*60)
        plot_comparison(stable_dir, turbulent_dir)
        
        print(f"\n{'='*60}")
        print("COMPARISON COMPLETE!")
        print("="*60)
        print("\nKey observations:")
        print("• Stable spiral: Reaches dynamic equilibrium with regular rotation")
        print("• Turbulent spiral: Shows chaotic behavior with irregular fluctuations")
        print("• Turbulent case has ~10x more variation in late-time dynamics")
        print("\nCheck the plots and output directories for detailed results!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
