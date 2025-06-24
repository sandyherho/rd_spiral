"""Time integration."""

import numpy as np
import time
from scipy.fft import fft2, ifft2
from scipy.integrate import solve_ivp
from typing import Dict
import logging


def reaction_diffusion_rhs(t, uv_hat, K2_flat, d1, d2, beta, n, N):
    """RHS of reaction-diffusion system in Fourier space."""
    # Extract and transform to real space
    u_hat = uv_hat[:N].reshape(n, n)
    v_hat = uv_hat[N:].reshape(n, n)
    
    u = np.real(ifft2(u_hat))
    v = np.real(ifft2(v_hat))
    
    # Reaction terms
    u2 = u * u
    v2 = v * v
    u3 = u2 * u
    v3 = v2 * v
    
    f = u - u3 - u*v2 + beta*(u2*v + v3)
    g = v - u2*v - v3 - beta*(u3 + u*v2)
    
    # Transform back and add diffusion
    f_hat = fft2(f).flatten()
    g_hat = fft2(g).flatten()
    
    dudt = -d1 * K2_flat * uv_hat[:N] + f_hat
    dvdt = -d2 * K2_flat * uv_hat[N:] + g_hat
    
    return np.concatenate([dudt, dvdt])


def integrate_system(u0, v0, t_eval, grid, d1, d2, beta, 
                    method='RK45', rtol=1e-6, atol=1e-9, logger=None) -> Dict:
    """Integrate the system with progress updates."""
    # Transform ICs
    u0_hat = fft2(u0).flatten()
    v0_hat = fft2(v0).flatten()
    uv0_hat = np.concatenate([u0_hat, v0_hat])
    
    # Progress tracking
    last_update = time.time()
    last_t = t_eval[0]
    
    def progress_wrapper(t, y):
        nonlocal last_update, last_t
        now = time.time()
        if now - last_update > 5.0 and logger:  # Update every 5 seconds
            progress = (t - t_eval[0]) / (t_eval[-1] - t_eval[0]) * 100
            rate = (t - last_t) / (now - last_update)
            logger.info(f"  Progress: {progress:5.1f}% | t = {t:7.2f} | "
                       f"Rate: {rate:5.2f} time units/sec")
            last_update = now
            last_t = t
        return reaction_diffusion_rhs(t, y, grid.K2_flat, d1, d2, beta, grid.n, grid.N)
    
    # Solve
    if logger:
        logger.info("Integrating equations...")
    
    sol = solve_ivp(
        progress_wrapper,
        [t_eval[0], t_eval[-1]],
        uv0_hat,
        t_eval=t_eval,
        method=method,
        rtol=rtol,
        atol=atol
    )
    
    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")
    
    # Transform back
    if logger:
        logger.info("Transforming solution to real space...")
    
    n_times = len(t_eval)
    u = np.zeros((grid.n, grid.n, n_times))
    v = np.zeros((grid.n, grid.n, n_times))
    
    for i in range(n_times):
        u_hat = sol.y[:grid.N, i].reshape(grid.n, grid.n)
        v_hat = sol.y[grid.N:, i].reshape(grid.n, grid.n)
        u[:, :, i] = np.real(ifft2(u_hat))
        v[:, :, i] = np.real(ifft2(v_hat))
    
    return {'u': u, 'v': v, 't': t_eval}
