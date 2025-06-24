"""Main solver class."""

import os
import shutil
import logging
import numpy as np
from datetime import datetime
from typing import Dict
from pathlib import Path

from .spatial import SpatialGrid, create_initial_conditions
from .integration import integrate_system
from .io import save_results, compute_stats


class ReactionDiffusionSolver:
    """Reaction-diffusion solver using spectral methods."""
    
    def __init__(self, config: Dict, config_name: str = None):
        """Initialize solver."""
        self.config = config
        self.d1 = config['d1']
        self.d2 = config['d2']
        self.beta = config['beta']
        
        # Create experiment name based on config file name (NO timestamp)
        if config_name:
            # Extract base name without path and extension
            base_name = os.path.splitext(os.path.basename(config_name))[0]
            self.experiment_name = base_name
        else:
            # Fallback to generic name for programmatic use
            self.experiment_name = "rd_simulation"
        
        # Get parent directory (outside package)
        package_dir = Path(__file__).parent.parent.parent
        parent_dir = package_dir.parent
        
        # Setup directories outside package
        self.output_dir = parent_dir / 'outputs' / self.experiment_name
        self.log_dir = parent_dir / 'logs' / self.experiment_name
        
        # Clean up previous runs (delete if exists)
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print(f"  → Removed previous output: {self.output_dir}")
        if self.log_dir.exists():
            shutil.rmtree(self.log_dir)
            print(f"  → Removed previous log: {self.log_dir}")
        
        # Create fresh directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Convert to string for compatibility
        self.output_dir = str(self.output_dir)
        self.log_dir = str(self.log_dir)
        
        # Setup logging
        self._setup_logging()
        
        # Create grid
        self.grid = SpatialGrid(config['L'], config['n'])
        
        self.logger.info(f"Initialized solver: {self.experiment_name}")
        self.logger.info(f"Parameters: d1={self.d1}, d2={self.d2}, beta={self.beta}")
        self.logger.info(f"Output directory: {self.output_dir}")
    
    def _setup_logging(self):
        """Setup logging."""
        log_file = os.path.join(self.log_dir, 'simulation.log')
        
        # Clear any existing handlers
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
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
        """Run simulation."""
        self.logger.info("="*60)
        self.logger.info("REACTION-DIFFUSION SPIRAL WAVE SIMULATION")
        self.logger.info("="*60)
        self.logger.info("Starting simulation...")
        
        # Initial conditions
        u0, v0 = create_initial_conditions(self.grid, self.config['num_spiral_arms'])
        self.logger.info(f"Initial conditions: {self.config['num_spiral_arms']}-armed spiral")
        
        # Time array
        t = np.arange(self.config['t_start'], 
                     self.config['t_end'] + self.config['dt'], 
                     self.config['dt'])
        self.logger.info(f"Time steps: {len(t)} (dt={self.config['dt']})")
        
        # Integrate
        solution = integrate_system(
            u0, v0, t, self.grid,
            self.d1, self.d2, self.beta,
            method=self.config['method'],
            rtol=self.config['rtol'],
            atol=self.config['atol'],
            logger=self.logger
        )
        
        # Compute statistics
        self.logger.info("Computing statistics...")
        stats = compute_stats(solution['u'], solution['v'], solution['t'])
        
        # Check equilibrium
        self._check_equilibrium(stats)
        
        # Save results
        save_results(solution, stats, self.config, self.output_dir)
        
        self.logger.info("="*60)
        self.logger.info(f"Results saved in: {self.output_dir}")
        self.logger.info(f"Log saved in: {self.log_dir}")
        self.logger.info("Simulation completed successfully!")
        self.logger.info("="*60)
    
    def _check_equilibrium(self, stats):
        """Check if equilibrium reached."""
        n_check = max(int(0.1 * len(stats)), 10)
        u_std_var = stats['u_std'].iloc[-n_check:].std()
        
        self.logger.info("-"*60)
        self.logger.info(f"Equilibrium check (last {n_check} steps):")
        self.logger.info(f"  u_std variation: {u_std_var:.6f}")
        
        if u_std_var < 0.001:
            if stats['u_std'].iloc[-1] < 0.01:
                self.logger.info("  → HOMOGENEOUS EQUILIBRIUM (pattern decayed)")
            else:
                self.logger.info("  → DYNAMIC EQUILIBRIUM (steady rotation)")
        else:
            self.logger.info("  → Still evolving")
        self.logger.info("-"*60)
