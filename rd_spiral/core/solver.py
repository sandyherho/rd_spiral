"""Main solver class for reaction-diffusion simulations."""

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
    """Reaction-diffusion solver using pseudo-spectral methods."""
    
    def __init__(self, config: Dict, config_name: Optional[str] = None):
        """Initialize solver with configuration."""
        self.config = config
        self.d1 = config['d1']
        self.d2 = config['d2']
        self.beta = config['beta']
        
        # Set experiment name from config file
        if config_name:
            base_name = os.path.splitext(os.path.basename(config_name))[0]
            self.experiment_name = base_name
        else:
            self.experiment_name = "rd_simulation"
        
        # Setup output directories
        package_dir = Path(__file__).parent.parent.parent
        parent_dir = package_dir.parent
        
        outputs_root = parent_dir / 'rd_outputs'
        logs_root = parent_dir / 'rd_logs'
        
        self.output_dir = outputs_root / self.experiment_name
        self.log_dir = logs_root / self.experiment_name
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = str(self.output_dir)
        self.log_dir = str(self.log_dir)
        
        self._setup_logging()
        
        # Create spatial grid
        self.grid = SpatialGrid(config['L'], config['n'])
        
        self.logger.info(f"Initialized solver: {self.experiment_name}")
        self.logger.info(f"Parameters: d1={self.d1}, d2={self.d2}, beta={self.beta}")
        self.logger.info(f"Output directory: {self.output_dir}")
    
    def _setup_logging(self):
        """Setup logging."""
        log_file = os.path.join(self.log_dir, 'simulation.log')
        
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
