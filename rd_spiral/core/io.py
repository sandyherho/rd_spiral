"""
Input/output functions for rd_spiral.

This module handles all file I/O operations including:
- Computing time series statistics from solution data
- Saving results in various formats (NetCDF, CSV, text)
- Configuration file management

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
import logging


def compute_stats(u: np.ndarray, v: np.ndarray, t: np.ndarray) -> pd.DataFrame:
    """
    Compute time series statistics from solution data.
    
    This function calculates various statistical measures at each time step
    which are useful for:
    - Monitoring simulation progress
    - Detecting equilibrium states
    - Analyzing pattern dynamics
    - Validating results
    
    Args:
        u: Solution array for species u with shape (nx, ny, nt)
        v: Solution array for species v with shape (nx, ny, nt)
        t: Time array with shape (nt,)
    
    Returns:
        pandas DataFrame with columns:
        - time: Time values
        - u_mean, v_mean: Spatial averages
        - u_std, v_std: Spatial standard deviations
        - u_min, u_max: Spatial extrema for u
        - v_min, v_max: Spatial extrema for v
    
    Notes:
        The standard deviation is particularly useful for detecting:
        - Pattern formation (std > 0)
        - Homogeneous states (std ≈ 0)
        - Dynamic equilibrium (constant std)
    """
    n_times = len(t)
    
    # Pre-allocate arrays for efficiency
    stats = {
        'time': t,
        'u_mean': np.zeros(n_times),
        'v_mean': np.zeros(n_times),
        'u_std': np.zeros(n_times),
        'v_std': np.zeros(n_times),
        'u_min': np.zeros(n_times),
        'u_max': np.zeros(n_times),
        'v_min': np.zeros(n_times),
        'v_max': np.zeros(n_times),
    }
    
    # Compute statistics for each time step
    for i in range(n_times):
        # Extract spatial slice at time i
        u_slice = u[:, :, i]
        v_slice = v[:, :, i]
        
        # Compute spatial statistics
        stats['u_mean'][i] = np.mean(u_slice)
        stats['v_mean'][i] = np.mean(v_slice)
        stats['u_std'][i] = np.std(u_slice)
        stats['v_std'][i] = np.std(v_slice)
        stats['u_min'][i] = np.min(u_slice)
        stats['u_max'][i] = np.max(u_slice)
        stats['v_min'][i] = np.min(v_slice)
        stats['v_max'][i] = np.max(v_slice)
    
    # Return as pandas DataFrame for easy analysis
    return pd.DataFrame(stats)


def save_results(solution: dict, stats: pd.DataFrame, config: dict, 
                output_dir: str) -> None:
    """
    Save simulation results to disk in multiple formats.
    
    This function saves:
    1. Full spatiotemporal solution data (NetCDF format)
    2. Time series statistics (CSV format)
    3. Configuration record (text format)
    
    Args:
        solution: Dictionary with keys 'u', 'v', 't' containing solution arrays
        stats: DataFrame of time series statistics
        config: Dictionary of configuration parameters
        output_dir: Directory path for saving results
    
    File formats:
        - NetCDF: Self-describing, compressed, includes metadata
        - CSV: Human-readable statistics, easy to plot
        - TXT: Complete configuration for reproducibility
    """
    logger = logging.getLogger(__name__)
    
    # Save statistics as CSV
    stats_file = os.path.join(output_dir, 'stats.csv')
    stats.to_csv(stats_file, index=False)
    logger.info(f"Saved statistics: stats.csv")
    
    # Save configuration with metadata
    config_file = os.path.join(output_dir, 'config.txt')
    with open(config_file, 'w') as f:
        # Header with metadata
        f.write(f"# Configuration saved at {datetime.now()}\n")
        f.write(f"# Author: Sandy Herho <sandy.herho@email.ucr.edu>\n")
        f.write(f"# rd_spiral version: 0.1.0\n")
        f.write(f"#\n")
        f.write(f"# Reaction-Diffusion Spiral Wave Simulation\n")
        f.write(f"#\n\n")
        
        # Write all parameters sorted by key
        for key, value in sorted(config.items()):
            f.write(f"{key} = {value}\n")
    logger.info(f"Saved configuration: config.txt")
    
    # Save full solution data as NetCDF if requested
    if config.get('save_netcdf', True):
        # Create xarray Dataset with proper coordinates and metadata
        ds = xr.Dataset(
            # Data variables
            {
                'u': (['x', 'y', 'time'], solution['u']),
                'v': (['x', 'y', 'time'], solution['v'])
            },
            # Coordinates
            coords={
                'time': solution['t']
            },
            # Global attributes for metadata
            attrs={
                # Physical parameters
                'd1': config['d1'],
                'd2': config['d2'],
                'beta': config['beta'],
                
                # Numerical parameters
                'L': config['L'],
                'n': config['n'],
                'method': config.get('method', 'RK45'),
                'rtol': config.get('rtol', 1e-6),
                'atol': config.get('atol', 1e-9),
                
                # Metadata
                'author': 'Sandy Herho <sandy.herho@email.ucr.edu>',
                'institution': 'University of California, Riverside',
                'source': 'rd_spiral v0.1.0',
                'created': datetime.now().isoformat(),
                
                # Physical description
                'title': 'Reaction-Diffusion Spiral Wave Simulation',
                'description': 'Solution of reaction-diffusion PDEs using pseudo-spectral method',
                'equations': '∂u/∂t = D₁∇²u + f(u,v), ∂v/∂t = D₂∇²v + g(u,v)',
                'reactions': 'f(u,v) = u - u³ - uv² + β(u²v + v³)',
            }
        )
        
        # Set up compression for efficient storage
        # Level 4 provides good compression with reasonable speed
        encoding = {
            var: {
                'zlib': True,      # Enable compression
                'complevel': 4,    # Compression level (1-9)
                'chunksizes': (ds[var].shape[0], ds[var].shape[1], 1)  # Chunk by time
            } 
            for var in ds.data_vars
        }
        
        # Save to NetCDF file
        nc_file = os.path.join(output_dir, 'solution.nc')
        ds.to_netcdf(nc_file, encoding=encoding)
        logger.info(f"Saved solution: solution.nc")
        
        # Log file size for user information
        size_mb = os.path.getsize(nc_file) / (1024 * 1024)
        logger.info(f"  File size: {size_mb:.1f} MB")
