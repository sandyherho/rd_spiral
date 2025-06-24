"""Input/output functions."""

import os
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime
import logging


def compute_stats(u: np.ndarray, v: np.ndarray, t: np.ndarray) -> pd.DataFrame:
    """Compute time series statistics."""
    n_times = len(t)
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
    
    for i in range(n_times):
        stats['u_mean'][i] = np.mean(u[:, :, i])
        stats['v_mean'][i] = np.mean(v[:, :, i])
        stats['u_std'][i] = np.std(u[:, :, i])
        stats['v_std'][i] = np.std(v[:, :, i])
        stats['u_min'][i] = np.min(u[:, :, i])
        stats['u_max'][i] = np.max(u[:, :, i])
        stats['v_min'][i] = np.min(v[:, :, i])
        stats['v_max'][i] = np.max(v[:, :, i])
    
    return pd.DataFrame(stats)


def save_results(solution: dict, stats: pd.DataFrame, config: dict, output_dir: str) -> None:
    """Save results to disk."""
    logger = logging.getLogger(__name__)
    
    # Save stats
    stats_file = os.path.join(output_dir, 'stats.csv')
    stats.to_csv(stats_file, index=False)
    logger.info(f"Saved statistics: stats.csv")
    
    # Save config
    config_file = os.path.join(output_dir, 'config.txt')
    with open(config_file, 'w') as f:
        f.write(f"# Configuration saved at {datetime.now()}\n")
        f.write(f"# rd_spiral simulation\n\n")
        for key, value in sorted(config.items()):
            f.write(f"{key} = {value}\n")
    logger.info(f"Saved configuration: config.txt")
    
    # Save NetCDF if requested
    if config.get('save_netcdf', True):
        ds = xr.Dataset(
            {
                'u': (['x', 'y', 'time'], solution['u']),
                'v': (['x', 'y', 'time'], solution['v'])
            },
            coords={
                'time': solution['t']
            },
            attrs={
                'd1': config['d1'],
                'd2': config['d2'],
                'beta': config['beta'],
                'L': config['L'],
                'n': config['n'],
                'created': datetime.now().isoformat()
            }
        )
        
        encoding = {var: {'zlib': True, 'complevel': 4} for var in ds.data_vars}
        nc_file = os.path.join(output_dir, 'solution.nc')
        ds.to_netcdf(nc_file, encoding=encoding)
        logger.info(f"Saved solution: solution.nc")
