"""
Main solver class for reaction-diffusion simulations.

This module contains the ReactionDiffusionSolver class which orchestrates
the entire simulation process including initialization, time integration,
equilibrium detection, and result storage.

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import os
import shutil
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from .spatial import SpatialGrid, create_initial_conditions
from .integration import integrate_system
from .io import save_results, compute_stats


class ReactionDiffusionSolver:
    """
    Reaction-diffusion solver using pseudo-spectral methods.
    
    This solver implements a high-accuracy pseudo-spectral method for solving
    reaction-diffusion equations on periodic domains. The spatial derivatives
    are computed in Fourier space (spectral accuracy) while the reaction terms
    are evaluated in physical space.
    
    Attributes:
        config (Dict): Configuration parameters
        d1 (float): Diffusion coefficient for species u
        d2 (float): Diffusion coefficient for species v
        beta (float): Reaction parameter controlling spiral dynamics
        experiment_name (str): Name for this simulation run
        output_dir (str): Directory for output files
        log_dir (str): Directory for log files
        grid (SpatialGrid): Spatial discretization object
        logger (logging.Logger): Logger instance
    """
    
    def __init__(self, config: Dict, config_name: Optional[str] = None):
        """
        Initialize the reaction-diffusion solver.
        
        Args:
            config (Dict): Configuration dictionary containing:
                - d1, d2: Diffusion coefficients
                - beta: Reaction parameter
                - L: Domain size
                - n: Grid points per dimension
                - t_start, t_end, dt: Time integration parameters
                - method: Integration method (default: RK45)
                - rtol, atol: Integration tolerances
                - num_spiral_arms: Initial spiral configuration
                - save_netcdf: Whether to save full solution
            config_name (Optional[str]): Name of config file for folder naming
        """
        # Store configuration and extract key parameters
        self.config = config
        self.d1 = config['d1']
        self.d2 = config['d2']
        self.beta = config['beta']
        
        # Determine experiment name from config file or use default
        if config_name:
            # Extract base name without path and extension
            base_name = os.path.splitext(os.path.basename(config_name))[0]
            self.experiment_name = base_name
        else:
            # Fallback for programmatic use without config file
            self.experiment_name = "rd_simulation"
        
        # Setup output directories in rd-outputs and rd-logs at package root
        package_dir = Path(__file__).parent.parent.parent
        parent_dir = package_dir.parent
        
        # Create rd-outputs and rd-logs directories at root level
        outputs_root = parent_dir / 'rd_outputs'
        logs_root = parent_dir / 'rd_logs'
        
        # Create experiment-specific subdirectories
        self.output_dir = outputs_root / self.experiment_name
        self.log_dir = logs_root / self.experiment_name
        
        # Create directories (keeps existing if present)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to string for compatibility with other modules
        self.output_dir = str(self.output_dir)
        self.log_dir = str(self.log_dir)
        
        # Initialize logging system
        self._setup_logging()
        
        # Create spatial discretization grid
        self.grid = SpatialGrid(config['L'], config['n'])
        
        # Log initialization details
        self.logger.info(f"Initialized solver: {self.experiment_name}")
        self.logger.info(f"Parameters: d1={self.d1}, d2={self.d2}, beta={self.beta}")
        self.logger.info(f"Grid: {config['n']}x{config['n']}, L={config['L']}")
        self.logger.info(f"Output directory: {self.output_dir}")
    
    def _setup_logging(self):
        """
        Configure logging system for the simulation.
        
        Sets up both file and console logging with appropriate formatting.
        Previous logger handlers are cleared to avoid duplication.
        """
        log_file = os.path.join(self.log_dir, 'simulation.log')
        
        # Clear any existing handlers to avoid duplicate logs
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Configure logging with both file and console output
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """
        Execute the complete simulation workflow.
        
        This method orchestrates the entire simulation process:
        1. Generate initial conditions
        2. Integrate the PDEs forward in time
        3. Compute statistics and check for equilibrium
        4. Save results to disk
        
        The simulation progress is logged throughout execution.
        """
        self.logger.info("="*60)
        self.logger.info("REACTION-DIFFUSION SPIRAL WAVE SIMULATION")
        self.logger.info("="*60)
        self.logger.info("Starting simulation...")
        
        # Generate initial conditions (spiral wave configuration)
        u0, v0 = create_initial_conditions(self.grid, self.config['num_spiral_arms'])
        self.logger.info(f"Initial conditions: {self.config['num_spiral_arms']}-armed spiral")
        
        # Create time discretization array
        t = np.arange(self.config['t_start'], 
                     self.config['t_end'] + self.config['dt'], 
                     self.config['dt'])
        self.logger.info(f"Time steps: {len(t)} (dt={self.config['dt']})")
        
        # Perform time integration using pseudo-spectral method
        solution = integrate_system(
            u0, v0, t, self.grid,
            self.d1, self.d2, self.beta,
            method=self.config['method'],
            rtol=self.config['rtol'],
            atol=self.config['atol'],
            logger=self.logger
        )
        
        # Compute statistical measures for analysis
        self.logger.info("Computing statistics...")
        stats = compute_stats(solution['u'], solution['v'], solution['t'])
        
        # Analyze equilibrium state (dynamic vs homogeneous)
        self._check_equilibrium(stats)
        
        # Save all results to disk
        save_results(solution, stats, self.config, self.output_dir)
        
        # Final summary
        self.logger.info("="*60)
        self.logger.info(f"Results saved in: {self.output_dir}")
        self.logger.info(f"Log saved in: {self.log_dir}")
        self.logger.info("Simulation completed successfully!")
        self.logger.info("="*60)
    
    def _check_equilibrium(self, stats):
        """
        Analyze the system's equilibrium state.
        
        Examines the variation in pattern statistics over the last 10% of
        the simulation to determine if the system has reached equilibrium
        and what type (dynamic or homogeneous).
        
        Args:
            stats: DataFrame containing time series of statistics
        
        Equilibrium types:
        - Homogeneous: Pattern has decayed to uniform state (u=v=0)
        - Dynamic: Stable rotating spiral with constant amplitude
        - Evolving: System still changing significantly
        """
        # Use last 10% of simulation or minimum 10 time steps
        n_check = max(int(0.1 * len(stats)), 10)
        
        # Calculate variation in standard deviation
        u_std_var = stats['u_std'].iloc[-n_check:].std()
        
        self.logger.info("-"*60)
        self.logger.info(f"Equilibrium check (last {n_check} steps):")
        self.logger.info(f"  u_std variation: {u_std_var:.6f}")
        
        # Classify equilibrium state based on variation and magnitude
        if u_std_var < 0.001:
            if stats['u_std'].iloc[-1] < 0.01:
                self.logger.info("  → HOMOGENEOUS EQUILIBRIUM (pattern decayed)")
            else:
                self.logger.info("  → DYNAMIC EQUILIBRIUM (steady rotation)")
        else:
            self.logger.info("  → Still evolving")
        self.logger.info("-"*60)
