"""Enhanced configuration parser with support for new solver features."""

import os
from typing import Dict, Any


def parse_config(config_file: str) -> Dict[str, Any]:
    """
    Parse enhanced configuration file with support for:
    - Equilibrium analysis control
    - Checkpoint saving options
    - Extended simulation parameters
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    config = {}
    
    with open(config_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                # Remove inline comments
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Type conversion with enhanced options
                    if key in ['n', 'num_spiral_arms']:
                        config[key] = int(value)
                    elif key in ['d1', 'd2', 'beta', 'L', 'dt', 'rtol', 'atol', 
                               't_start', 't_end', 'checkpoint_interval']:
                        config[key] = float(value)
                    elif key in ['save_netcdf', 'check_equilibrium', 'save_checkpoints']:
                        config[key] = value.lower() in ['true', '1', 'yes', 'on']
                    else:
                        config[key] = value
                        
                except ValueError as e:
                    print(f"Warning: Error parsing line {line_num}: {line}")
                    print(f"  Error: {e}")
                    continue
    
    # Enhanced defaults with new features
    defaults = {
        # Standard parameters
        'method': 'RK45',
        'rtol': 1e-6,
        'atol': 1e-9,
        'num_spiral_arms': 1,
        'save_netcdf': True,
        'output_dir': 'rd_outputs',
        
        # New enhanced features
        'check_equilibrium': True,  # Can be disabled for known non-equilibrium systems
        'save_checkpoints': False,  # Enable for long simulations
        'checkpoint_interval': 50.0,  # Time units between checkpoints
    }
    
    # Apply defaults
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    # Validate configuration
    required_params = ['d1', 'd2', 'beta', 'L', 'n', 't_start', 't_end', 'dt']
    missing = [p for p in required_params if p not in config]
    
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    # Validate numerical parameters
    if config['dt'] <= 0:
        raise ValueError(f"Time step dt must be positive, got {config['dt']}")
    
    if config['t_end'] <= config['t_start']:
        raise ValueError(f"t_end ({config['t_end']}) must be greater than t_start ({config['t_start']})")
    
    if config['n'] < 32:
        print(f"Warning: Grid size n={config['n']} is very small. Consider n≥64 for accuracy.")
    
    if config['save_checkpoints'] and config['checkpoint_interval'] <= 0:
        raise ValueError(f"checkpoint_interval must be positive when save_checkpoints=true")
    
    return config


def create_config_template(filename: str = "config_template.txt"):
    """
    Create a template configuration file with all available options documented.
    """
    template = """# Reaction-Diffusion Spiral Wave Simulation Configuration
# ======================================================
# This template includes all available configuration options
# with detailed explanations for each parameter.

# Physical Parameters
# -------------------
# Diffusion coefficients for species u and v
d1 = 0.1    # Diffusion coefficient for u (typically 0.01-1.0)
d2 = 0.1    # Diffusion coefficient for v (typically 0.01-1.0)

# Reaction parameter controlling spiral dynamics
beta = 1.0  # Reaction coupling (typically 0.5-2.0)
            # Lower values: stable spirals
            # Higher values: complex dynamics

# Spatial Domain
# --------------
L = 20.0    # Domain size: [-L/2, L/2] × [-L/2, L/2]
n = 128     # Grid points per dimension (powers of 2 recommended)
            # Minimum: 64 for basic patterns
            # Recommended: 128-256 for detailed dynamics

# Time Integration
# ----------------
t_start = 0.0   # Start time
t_end = 200.0   # End time (adjust based on dynamics)
dt = 0.1        # Time step (stability: dt < dx²/4D_max)

# Numerical Methods
# -----------------
method = RK45   # Integration method: RK45, RK23, DOP853, BDF
rtol = 1e-6     # Relative tolerance
atol = 1e-9     # Absolute tolerance

# Initial Conditions
# ------------------
num_spiral_arms = 1  # Number of spiral arms (1-5 typical)

# Output Options
# --------------
save_netcdf = true   # Save full spatiotemporal data

# Enhanced Features (New)
# ----------------------
# Equilibrium analysis
check_equilibrium = true  # Analyze equilibrium state at end
                         # Set to false for known chaotic systems

# Checkpoint saving for long simulations
save_checkpoints = false      # Enable intermediate saves
checkpoint_interval = 50.0    # Time units between checkpoints

# Example Parameter Sets
# =====================
# 1. Stable spiral: d1=d2=0.1, beta=1.0
# 2. Turbulent: d1=0.05, d2=0.15, beta=0.7
# 3. Pattern decay: d1=d2=0.5, beta=1.0
# 4. Multi-armed: num_spiral_arms=3, d1=d2=0.08
"""
    
    with open(filename, 'w') as f:
        f.write(template)
    
    print(f"Created configuration template: {filename}")
    print("Edit this file to set your simulation parameters.")
