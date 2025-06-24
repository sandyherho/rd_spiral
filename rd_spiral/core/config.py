"""Configuration parser."""

import os
from typing import Dict, Any


def parse_config(config_file: str) -> Dict[str, Any]:
    """Parse configuration file."""
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    config = {}
    
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Type conversion
                if key in ['n', 'num_spiral_arms']:
                    config[key] = int(value)
                elif key in ['d1', 'd2', 'beta', 'L', 'dt', 'rtol', 'atol', 't_start', 't_end']:
                    config[key] = float(value)
                elif key in ['save_netcdf']:
                    config[key] = value.lower() in ['true', '1', 'yes']
                else:
                    config[key] = value
    
    # Defaults
    defaults = {
        'method': 'RK45',
        'rtol': 1e-6,
        'atol': 1e-9,
        'num_spiral_arms': 1,
        'save_netcdf': True,
        'output_dir': '../outputs'  # Save outside package
    }
    
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
    
    return config
