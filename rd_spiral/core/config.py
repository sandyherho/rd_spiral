"""
Configuration parser for rd_spiral.

This module handles parsing of configuration files which use a simple
key-value format. The parser supports comments, type conversion, and
default values for optional parameters.

Configuration file format:
    # Comments start with #
    key = value
    d1 = 0.1  # Inline comments also supported

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import os
from typing import Dict, Any


def parse_config(config_file: str) -> Dict[str, Any]:
    """
    Parse configuration file into parameter dictionary.
    
    This function reads a text configuration file and extracts parameters
    for the simulation. It handles:
    - Comment lines (starting with #)
    - Inline comments (after #)
    - Type conversion (int, float, bool, string)
    - Default values for optional parameters
    
    Args:
        config_file: Path to configuration file
    
    Returns:
        Dictionary of configuration parameters with appropriate types
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required parameters are missing
    
    Example config file:
        # Diffusion coefficients
        d1 = 0.1
        d2 = 0.1
        
        # Reaction parameter
        beta = 1.0
        
        # Domain settings
        L = 20.0    # Domain size
        n = 128     # Grid points
    """
    # Check if file exists
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    config = {}
    
    # Read and parse the configuration file
    with open(config_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            # Remove leading/trailing whitespace
            line = line.strip()
            
            # Skip empty lines and comment lines
            if not line or line.startswith('#'):
                continue
            
            # Check if line contains key=value pair
            if '=' in line:
                # Handle inline comments
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                # Split into key and value
                try:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                except ValueError:
                    print(f"Warning: Invalid line {line_num} in config file: {line}")
                    continue
                
                # Type conversion based on parameter name
                # Integer parameters
                if key in ['n', 'num_spiral_arms']:
                    try:
                        config[key] = int(value)
                    except ValueError:
                        raise ValueError(f"Parameter '{key}' must be an integer, got: {value}")
                
                # Float parameters
                elif key in ['d1', 'd2', 'beta', 'L', 'dt', 'rtol', 'atol', 't_start', 't_end']:
                    try:
                        config[key] = float(value)
                    except ValueError:
                        raise ValueError(f"Parameter '{key}' must be a number, got: {value}")
                
                # Boolean parameters
                elif key in ['save_netcdf']:
                    config[key] = value.lower() in ['true', '1', 'yes', 'on']
                
                # String parameters (no conversion needed)
                else:
                    config[key] = value
    
    # Define default values for optional parameters
    defaults = {
        'method': 'RK45',           # Time integration method
        'rtol': 1e-6,              # Relative tolerance
        'atol': 1e-9,              # Absolute tolerance
        'num_spiral_arms': 1,       # Single spiral by default
        'save_netcdf': True,        # Save full solution by default
        'output_dir': 'rd_outputs'  # Output directory
    }
    
    # Apply defaults for missing parameters
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
    
    # Validate required parameters
    required = ['d1', 'd2', 'beta', 'L', 'n', 't_start', 't_end', 'dt']
    missing = [key for key in required if key not in config]
    
    if missing:
        raise ValueError(f"Missing required parameters: {', '.join(missing)}")
    
    # Validate parameter ranges
    if config['n'] < 16:
        raise ValueError(f"Grid size n must be at least 16, got {config['n']}")
    
    if config['L'] <= 0:
        raise ValueError(f"Domain size L must be positive, got {config['L']}")
    
    if config['dt'] <= 0:
        raise ValueError(f"Time step dt must be positive, got {config['dt']}")
    
    if config['t_end'] <= config['t_start']:
        raise ValueError(f"End time must be greater than start time")
    
    # Log successful parsing
    print(f"Successfully parsed {len(config)} parameters from {config_file}")
    
    return config
