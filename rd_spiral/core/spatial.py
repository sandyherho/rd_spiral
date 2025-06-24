"""
Spatial discretization module.

This module handles the spatial grid setup for the pseudo-spectral method,
including both physical space coordinates and Fourier space wavenumbers.
It also provides functions for generating initial conditions.

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import numpy as np
from typing import Tuple


class SpatialGrid:
    """
    Spatial discretization grid for pseudo-spectral methods.
    
    This class sets up both physical space and Fourier space grids needed
    for the pseudo-spectral method. The domain is assumed to be square and
    periodic in both directions.
    
    Attributes:
        L (float): Physical domain size (L × L)
        n (int): Number of grid points per dimension
        N (int): Total number of grid points (n²)
        x, y (ndarray): 1D coordinate arrays
        X, Y (ndarray): 2D meshgrid coordinates
        kx, ky (ndarray): 1D wavenumber arrays
        KX, KY (ndarray): 2D meshgrid wavenumbers
        K2 (ndarray): Squared wavenumber magnitude (KX² + KY²)
        K2_flat (ndarray): Flattened K2 for efficient computation
    """
    
    def __init__(self, L: float, n: int):
        """
        Initialize spatial grid.
        
        Args:
            L: Domain size (creates domain [-L/2, L/2] × [-L/2, L/2])
            n: Number of grid points per dimension
        
        Note:
            The grid uses n points but due to periodicity, the last point
            is equivalent to the first, so we use n+1 points and drop the last.
        """
        self.L = L
        self.n = n
        self.N = n * n  # Total grid points
        
        # Physical space coordinates
        # Create evenly spaced points from -L/2 to L/2
        # Drop the last point due to periodicity
        x = np.linspace(-L/2, L/2, n+1)[:-1]
        self.x = x
        self.y = x  # Square domain
        
        # Create 2D meshgrid for easy evaluation
        self.X, self.Y = np.meshgrid(x, x)
        
        # Fourier space wavenumbers
        # For FFT, wavenumbers are ordered as [0, 1, ..., n/2-1, -n/2, ..., -1]
        # This ensures proper alignment with numpy's FFT convention
        kx = (2*np.pi/L) * np.concatenate([np.arange(0, n//2), 
                                          np.arange(-n//2, 0)])
        self.kx = kx
        self.ky = kx  # Isotropic discretization
        
        # 2D wavenumber grids
        self.KX, self.KY = np.meshgrid(kx, kx)
        
        # Squared wavenumber magnitude (used for Laplacian)
        # In Fourier space: ∇²û = -k²û where k² = kx² + ky²
        self.K2 = self.KX**2 + self.KY**2
        
        # Flattened version for efficient use in ODE solver
        self.K2_flat = self.K2.flatten()


def create_initial_conditions(grid: SpatialGrid, m: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create spiral wave initial conditions.
    
    This function generates initial conditions that evolve into spiral waves.
    The initial state is designed to break symmetry and seed spiral formation.
    
    The functional form is:
        u₀(r,θ) = tanh(r) × cos(mθ - r)
        v₀(r,θ) = tanh(r) × sin(mθ - r)
    
    where (r,θ) are polar coordinates and m is the number of spiral arms.
    
    Args:
        grid: SpatialGrid object containing coordinate arrays
        m: Number of spiral arms (topological charge)
           m=1: Single spiral
           m=2: Double spiral (spiral pair)
           m=3: Triple spiral
           etc.
    
    Returns:
        Tuple of (u0, v0) initial condition arrays
    
    Physical interpretation:
        - tanh(r): Smooth transition from core (r=0) to boundary
        - cos/sin(mθ - r): Phase that creates spiral structure
        - The -r term creates outward propagating waves
    """
    # Convert to polar coordinates
    r = np.sqrt(grid.X**2 + grid.Y**2)
    theta = np.angle(grid.X + 1j*grid.Y)
    
    # Generate spiral initial conditions
    # tanh(r) provides smooth radial profile
    # m*theta creates m-armed spiral
    # -r phase creates outward propagation
    u0 = np.tanh(r) * np.cos(m * theta - r)
    v0 = np.tanh(r) * np.sin(m * theta - r)
    
    return u0, v0
