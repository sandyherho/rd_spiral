"""
Time integration module for reaction-diffusion systems.

This module implements the pseudo-spectral method for solving reaction-diffusion
PDEs. The key idea is to compute spatial derivatives in Fourier space (where
they become simple multiplications) while evaluating nonlinear reaction terms
in physical space.

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import numpy as np
import time
from scipy.fft import fft2, ifft2
from scipy.integrate import solve_ivp
from typing import Dict, Optional
import logging


def reaction_diffusion_rhs(t: float, uv_hat: np.ndarray, K2_flat: np.ndarray, 
                          d1: float, d2: float, beta: float, n: int, N: int) -> np.ndarray:
    """
    Compute right-hand side of reaction-diffusion system in Fourier space.
    
    This function implements the pseudo-spectral method where:
    1. Linear diffusion terms are computed in Fourier space
    2. Nonlinear reaction terms are computed in physical space
    3. The reaction terms are then transformed to Fourier space
    
    The reaction-diffusion system is:
        ∂u/∂t = D₁∇²u + f(u,v)
        ∂v/∂t = D₂∇²v + g(u,v)
    
    where the reaction terms are:
        f(u,v) = u - u³ - uv² + β(u²v + v³)
        g(u,v) = v - u²v - v³ - β(u³ + uv²)
    
    Args:
        t: Current time (for compatibility with solve_ivp)
        uv_hat: Fourier coefficients of [u, v] concatenated
        K2_flat: Squared wavenumbers (k²) flattened
        d1, d2: Diffusion coefficients
        beta: Reaction parameter
        n: Grid size per dimension
        N: Total grid points (n²)
    
    Returns:
        Time derivatives of Fourier coefficients [du/dt, dv/dt]
    """
    # Extract Fourier coefficients and reshape to 2D arrays
    u_hat = uv_hat[:N].reshape(n, n)
    v_hat = uv_hat[N:].reshape(n, n)
    
    # Transform to physical space for reaction term evaluation
    # np.real() removes negligible imaginary parts from numerical errors
    u = np.real(ifft2(u_hat))
    v = np.real(ifft2(v_hat))
    
    # Precompute powers to avoid redundant calculations
    u2 = u * u
    v2 = v * v
    u3 = u2 * u
    v3 = v2 * v
    
    # Evaluate reaction terms in physical space
    # These represent the nonlinear kinetics of the system
    f = u - u3 - u*v2 + beta*(u2*v + v3)
    g = v - u2*v - v3 - beta*(u3 + u*v2)
    
    # Transform reaction terms to Fourier space and flatten
    f_hat = fft2(f).flatten()
    g_hat = fft2(g).flatten()
    
    # Combine diffusion (in Fourier space) with reaction terms
    # In Fourier space: ∇²û = -k²û
    dudt = -d1 * K2_flat * uv_hat[:N] + f_hat
    dvdt = -d2 * K2_flat * uv_hat[N:] + g_hat
    
    return np.concatenate([dudt, dvdt])


def integrate_system(u0: np.ndarray, v0: np.ndarray, t_eval: np.ndarray, 
                    grid, d1: float, d2: float, beta: float, 
                    method: str = 'RK45', rtol: float = 1e-6, 
                    atol: float = 1e-9, logger: Optional[logging.Logger] = None) -> Dict:
    """
    Integrate the reaction-diffusion system using pseudo-spectral method.
    
    This function performs time integration of the reaction-diffusion PDEs
    using an adaptive ODE solver (default: Runge-Kutta 4/5) applied to the
    Fourier-transformed system.
    
    The integration includes:
    - Progress monitoring with rate estimation
    - Automatic error control via adaptive timesteps
    - Efficient spectral differentiation
    
    Args:
        u0, v0: Initial conditions for species u and v
        t_eval: Time points where solution is requested
        grid: SpatialGrid object containing discretization info
        d1, d2: Diffusion coefficients
        beta: Reaction parameter
        method: ODE solver method (default: 'RK45')
        rtol, atol: Relative and absolute tolerances
        logger: Optional logger for progress updates
    
    Returns:
        Dictionary containing:
            'u': Solution for species u [nx, ny, nt]
            'v': Solution for species v [nx, ny, nt]
            't': Time array
    
    Raises:
        RuntimeError: If integration fails
    """
    # Transform initial conditions to Fourier space
    u0_hat = fft2(u0).flatten()
    v0_hat = fft2(v0).flatten()
    uv0_hat = np.concatenate([u0_hat, v0_hat])
    
    # Setup progress tracking for long simulations
    last_update = time.time()
    last_t = t_eval[0]
    
    def progress_wrapper(t, y):
        """Wrapper to add progress logging to RHS function."""
        nonlocal last_update, last_t
        now = time.time()
        
        # Update progress every 5 seconds of wall time
        if now - last_update > 5.0 and logger:
            progress = (t - t_eval[0]) / (t_eval[-1] - t_eval[0]) * 100
            rate = (t - last_t) / (now - last_update)
            logger.info(f"  Progress: {progress:5.1f}% | t = {t:7.2f} | "
                       f"Rate: {rate:5.2f} time units/sec")
            last_update = now
            last_t = t
            
        # Call actual RHS function
        return reaction_diffusion_rhs(t, y, grid.K2_flat, d1, d2, beta, grid.n, grid.N)
    
    # Perform time integration
    if logger:
        logger.info("Integrating equations...")
    
    # Use scipy's adaptive ODE solver
    sol = solve_ivp(
        progress_wrapper,
        [t_eval[0], t_eval[-1]],
        uv0_hat,
        t_eval=t_eval,
        method=method,
        rtol=rtol,
        atol=atol
    )
    
    # Check if integration was successful
    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")
    
    # Transform solution back to physical space
    if logger:
        logger.info("Transforming solution to real space...")
    
    n_times = len(t_eval)
    u = np.zeros((grid.n, grid.n, n_times))
    v = np.zeros((grid.n, grid.n, n_times))
    
    # Process each time step
    for i in range(n_times):
        # Extract and reshape Fourier coefficients
        u_hat = sol.y[:grid.N, i].reshape(grid.n, grid.n)
        v_hat = sol.y[grid.N:, i].reshape(grid.n, grid.n)
        
        # Transform to physical space
        u[:, :, i] = np.real(ifft2(u_hat))
        v[:, :, i] = np.real(ifft2(v_hat))
    
    return {'u': u, 'v': v, 't': t_eval}
