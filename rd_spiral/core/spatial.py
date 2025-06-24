"""Spatial discretization module."""

import numpy as np
from typing import Tuple


class SpatialGrid:
    """Spatial grid for spectral methods."""
    
    def __init__(self, L: float, n: int):
        """Initialize grid."""
        self.L = L
        self.n = n
        self.N = n * n
        
        # Real space
        x = np.linspace(-L/2, L/2, n+1)[:-1]
        self.x = x
        self.y = x
        self.X, self.Y = np.meshgrid(x, x)
        
        # Fourier space
        kx = (2*np.pi/L) * np.concatenate([np.arange(0, n//2), 
                                          np.arange(-n//2, 0)])
        self.kx = kx
        self.ky = kx
        self.KX, self.KY = np.meshgrid(kx, kx)
        self.K2 = self.KX**2 + self.KY**2
        self.K2_flat = self.K2.flatten()


def create_initial_conditions(grid: SpatialGrid, m: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """Create spiral wave initial conditions."""
    r = np.sqrt(grid.X**2 + grid.Y**2)
    theta = np.angle(grid.X + 1j*grid.Y)
    
    u0 = np.tanh(r) * np.cos(m * theta - r)
    v0 = np.tanh(r) * np.sin(m * theta - r)
    
    return u0, v0
