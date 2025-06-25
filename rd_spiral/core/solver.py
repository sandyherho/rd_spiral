"""Enhanced solver class for reaction-diffusion simulations with robust output handling."""

import os
import shutil
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import traceback

from .spatial import SpatialGrid, create_initial_conditions
from .integration import integrate_system
from .io import save_results, compute_stats


class ReactionDiffusionSolver:
    """
    Enhanced reaction-diffusion solver using pseudo-spectral methods.
    
    Key enhancements:
    - Robust output preservation for non-equilibrium states
    - Checkpoint saving for long simulations
    - Optional equilibrium analysis
    - Enhanced error handling with partial result preservation
    """
    
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
        
        # Checkpoint directory for intermediate saves
        self.checkpoint_dir = os.path.join(self.output_dir, 'checkpoints')
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        
        self._setup_logging()
        
        # Create spatial grid
        self.grid = SpatialGrid(config['L'], config['n'])
        
        # Optional features (with defaults)
        self.check_equilibrium = config.get('check_equilibrium', True)
        self.save_checkpoints = config.get('save_checkpoints', False)
        self.checkpoint_interval = config.get('checkpoint_interval', 50.0)  # time units
        
        self.logger.info(f"Initialized enhanced solver: {self.experiment_name}")
        self.logger.info(f"Parameters: d1={self.d1}, d2={self.d2}, beta={self.beta}")
        self.logger.info(f"Output directory: {self.output_dir}")
        self.logger.info(f"Features: equilibrium_check={self.check_equilibrium}, "
                        f"checkpoints={self.save_checkpoints}")
    
    def _setup_logging(self):
        """Setup logging with enhanced formatting."""
        log_file = os.path.join(self.log_dir, 'simulation.log')
        
        logger = logging.getLogger()
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run(self):
        """
        Run simulation with robust error handling and output preservation.
        
        This method ensures that:
        1. Partial results are saved if simulation is interrupted
        2. Outputs are preserved regardless of equilibrium state
        3. Clear status reporting throughout the simulation
        """
        self.logger.info("="*60)
        self.logger.info("REACTION-DIFFUSION SPIRAL WAVE SIMULATION")
        self.logger.info("Enhanced solver with robust output handling")
        self.logger.info("="*60)
        
        solution = None
        stats = None
        simulation_status = "INCOMPLETE"
        
        try:
            self.logger.info("Phase 1: Initialization")
            self.logger.info("-"*40)
            
            # Initial conditions
            u0, v0 = create_initial_conditions(self.grid, self.config['num_spiral_arms'])
            self.logger.info(f"✓ Initial conditions: {self.config['num_spiral_arms']}-armed spiral")
            
            # Time array
            t = np.arange(self.config['t_start'], 
                         self.config['t_end'] + self.config['dt'], 
                         self.config['dt'])
            self.logger.info(f"✓ Time discretization: {len(t)} steps (dt={self.config['dt']})")
            self.logger.info(f"  Time range: [{self.config['t_start']}, {self.config['t_end']}]")
            
            # Save initial state
            self._save_initial_state(u0, v0)
            
            self.logger.info("\nPhase 2: Time Integration")
            self.logger.info("-"*40)
            
            # Integrate with checkpoint support
            if self.save_checkpoints:
                solution = self._integrate_with_checkpoints(u0, v0, t)
            else:
                solution = integrate_system(
                    u0, v0, t, self.grid,
                    self.d1, self.d2, self.beta,
                    method=self.config['method'],
                    rtol=self.config['rtol'],
                    atol=self.config['atol'],
                    logger=self.logger
                )
            
            self.logger.info("✓ Integration completed successfully")
            
            # Compute statistics
            self.logger.info("\nPhase 3: Analysis")
            self.logger.info("-"*40)
            self.logger.info("Computing spatiotemporal statistics...")
            stats = compute_stats(solution['u'], solution['v'], solution['t'])
            self.logger.info("✓ Statistics computed")
            
            # Optional equilibrium analysis
            if self.check_equilibrium:
                equilibrium_state = self._analyze_equilibrium(stats)
                simulation_status = f"COMPLETE - {equilibrium_state}"
            else:
                simulation_status = "COMPLETE - No equilibrium analysis requested"
                self.logger.info("Equilibrium analysis skipped (disabled in config)")
            
        except KeyboardInterrupt:
            self.logger.warning("\nSimulation interrupted by user!")
            simulation_status = "INTERRUPTED"
            # Will save partial results below
            
        except Exception as e:
            self.logger.error(f"\nError during simulation: {str(e)}")
            self.logger.error(traceback.format_exc())
            simulation_status = f"ERROR: {str(e)}"
            # Will save partial results if available
            
        finally:
            # Always attempt to save whatever results we have
            self.logger.info("\nPhase 4: Output Preservation")
            self.logger.info("-"*40)
            
            self._save_all_results(solution, stats, simulation_status)
            
            self.logger.info("\n" + "="*60)
            self.logger.info("SIMULATION SUMMARY")
            self.logger.info("="*60)
            self.logger.info(f"Status: {simulation_status}")
            self.logger.info(f"Results directory: {self.output_dir}")
            self.logger.info(f"Log directory: {self.log_dir}")
            
            if solution is not None:
                final_time = solution['t'][-1]
                self.logger.info(f"Final simulation time: {final_time:.2f}")
            
            self.logger.info("="*60)
    
    def _save_initial_state(self, u0: np.ndarray, v0: np.ndarray):
        """Save initial conditions for reference."""
        ic_file = os.path.join(self.output_dir, 'initial_conditions.npz')
        np.savez_compressed(ic_file, u0=u0, v0=v0, x=self.grid.x, y=self.grid.y)
        self.logger.info(f"✓ Saved initial conditions")
    
    def _integrate_with_checkpoints(self, u0, v0, t_full):
        """Integration with checkpoint saving."""
        self.logger.info(f"Checkpoint saving enabled (interval: {self.checkpoint_interval} time units)")
        
        # Determine checkpoint times
        checkpoint_times = np.arange(
            t_full[0] + self.checkpoint_interval,
            t_full[-1],
            self.checkpoint_interval
        )
        
        # Add final time if not included
        if checkpoint_times[-1] < t_full[-1]:
            checkpoint_times = np.append(checkpoint_times, t_full[-1])
        
        # Initialize storage
        all_u = []
        all_v = []
        all_t = []
        
        u_current = u0
        v_current = v0
        t_start = t_full[0]
        
        for i, t_checkpoint in enumerate(checkpoint_times):
            self.logger.info(f"\nIntegrating to checkpoint {i+1}/{len(checkpoint_times)} "
                           f"(t={t_checkpoint:.1f})")
            
            # Time array for this segment
            t_segment = t_full[(t_full >= t_start) & (t_full <= t_checkpoint)]
            
            if len(t_segment) == 0:
                continue
            
            # Integrate segment
            sol_segment = integrate_system(
                u_current, v_current, t_segment, self.grid,
                self.d1, self.d2, self.beta,
                method=self.config['method'],
                rtol=self.config['rtol'],
                atol=self.config['atol'],
                logger=self.logger
            )
            
            # Save checkpoint
            checkpoint_file = os.path.join(
                self.checkpoint_dir, 
                f'checkpoint_t{t_checkpoint:.0f}.npz'
            )
            np.savez_compressed(
                checkpoint_file,
                u=sol_segment['u'][:, :, -1],
                v=sol_segment['v'][:, :, -1],
                t=t_checkpoint
            )
            self.logger.info(f"✓ Saved checkpoint: {os.path.basename(checkpoint_file)}")
            
            # Store results (excluding first point except for first segment)
            start_idx = 0 if i == 0 else 1
            all_u.append(sol_segment['u'][:, :, start_idx:])
            all_v.append(sol_segment['v'][:, :, start_idx:])
            all_t.append(sol_segment['t'][start_idx:])
            
            # Update for next segment
            u_current = sol_segment['u'][:, :, -1]
            v_current = sol_segment['v'][:, :, -1]
            t_start = t_checkpoint
        
        # Combine all segments
        u_combined = np.concatenate(all_u, axis=2)
        v_combined = np.concatenate(all_v, axis=2)
        t_combined = np.concatenate(all_t)
        
        return {'u': u_combined, 'v': v_combined, 't': t_combined}
    
    def _analyze_equilibrium(self, stats):
        """
        Analyze equilibrium state with enhanced categorization.
        
        Returns a descriptive string of the system state.
        """
        n_check = max(int(0.1 * len(stats)), 10)
        u_std_var = stats['u_std'].iloc[-n_check:].std()
        u_std_mean = stats['u_std'].iloc[-n_check:].mean()
        
        # Calculate additional metrics
        u_range = stats['u_std'].iloc[-n_check:].max() - stats['u_std'].iloc[-n_check:].min()
        rel_variation = u_std_var / (u_std_mean + 1e-10)
        
        self.logger.info("\nEquilibrium Analysis")
        self.logger.info("-"*30)
        self.logger.info(f"Analysis window: last {n_check} time steps")
        self.logger.info(f"Pattern intensity (mean): {u_std_mean:.6f}")
        self.logger.info(f"Pattern variation (std): {u_std_var:.6f}")
        self.logger.info(f"Pattern range: {u_range:.6f}")
        self.logger.info(f"Relative variation: {rel_variation:.6f}")
        
        # Categorize state
        if u_std_mean < 0.01:
            state = "HOMOGENEOUS (pattern decayed)"
        elif u_std_var < 0.0001:
            state = "STATIC EQUILIBRIUM"
        elif u_std_var < 0.001:
            state = "DYNAMIC EQUILIBRIUM (steady rotation)"
        elif u_std_var < 0.01:
            state = "QUASI-PERIODIC"
        else:
            state = "NON-EQUILIBRIUM (chaotic/turbulent)"
        
        self.logger.info(f"\nSystem state: {state}")
        return state
    
    def _save_all_results(self, solution, stats, status):
        """Save all available results with status information."""
        try:
            # Save status file
            status_file = os.path.join(self.output_dir, 'simulation_status.txt')
            with open(status_file, 'w') as f:
                f.write(f"Simulation Status: {status}\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Configuration: {self.experiment_name}\n")
                
                if solution is not None:
                    f.write(f"\nSimulation Progress:\n")
                    f.write(f"  Final time reached: {solution['t'][-1]:.2f}\n")
                    f.write(f"  Target time: {self.config['t_end']:.2f}\n")
                    f.write(f"  Completion: {100*solution['t'][-1]/self.config['t_end']:.1f}%\n")
            
            self.logger.info(f"✓ Saved simulation status")
            
            # Save results if available
            if solution is not None and stats is not None:
                save_results(solution, stats, self.config, self.output_dir)
                self.logger.info("✓ All results saved successfully")
            elif solution is not None:
                # Save partial solution without stats
                self.logger.warning("Statistics unavailable - saving solution data only")
                np.savez_compressed(
                    os.path.join(self.output_dir, 'partial_solution.npz'),
                    u=solution['u'],
                    v=solution['v'],
                    t=solution['t']
                )
                self.logger.info("✓ Saved partial solution data")
            else:
                self.logger.warning("No solution data available to save")
                
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            # Create emergency save
            emergency_file = os.path.join(self.output_dir, 'emergency_save.txt')
            with open(emergency_file, 'w') as f:
                f.write(f"Emergency save - simulation failed\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Status: {status}\n")
