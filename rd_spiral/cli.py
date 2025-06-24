"""
Command-line interface for rd_spiral package.

This module provides the main entry point for the rd_spiral solver when
used from the command line. It handles argument parsing, configuration
loading, and solver execution.

Usage:
    rd-spiral <config_file>
    rd-spiral --version

Author: Sandy Herho <sandy.herho@email.ucr.edu>
Date: June 2025
"""

import sys
import os
import argparse
from .core import parse_config, ReactionDiffusionSolver


def main():
    """
    Main CLI entry point for rd_spiral.
    
    This function:
    1. Parses command-line arguments
    2. Loads the configuration file
    3. Initializes the solver
    4. Runs the simulation
    5. Handles errors gracefully
    
    The function will look for config files in:
    - The specified path (absolute or relative)
    - The package's configs/ directory (for bundled examples)
    """
    # Setup argument parser with description
    parser = argparse.ArgumentParser(
        description="rd_spiral: Reaction-diffusion spiral wave solver",
        epilog="Output files will be saved in rd_outputs/ and rd_logs/ directories"
    )
    
    # Define command-line arguments
    parser.add_argument('config', 
                       help='Configuration file path (e.g., configs/stable_spiral.txt)')
    parser.add_argument('--version', 
                       action='version', 
                       version='rd_spiral v0.1.0')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Store original config path for solver naming
    original_config = args.config
    
    # Check if config file exists at specified path
    if not os.path.exists(args.config):
        # If not found, try looking in package configs directory
        # This allows users to specify just the filename for bundled configs
        try:
            import pkg_resources
            config_path = pkg_resources.resource_filename('rd_spiral', 
                                                         f'configs/{args.config}')
            if os.path.exists(config_path):
                args.config = config_path
        except:
            # pkg_resources not available or file still not found
            pass
    
    try:
        # Display header
        print("="*60)
        print("RD-SPIRAL: Reaction-Diffusion Solver")
        print("Author: Sandy Herho <sandy.herho@email.ucr.edu>")
        print("="*60)
        
        # Load configuration from file
        config = parse_config(args.config)
        print(f"Configuration: {args.config}")
        print(f"Parameters: d1={config['d1']}, d2={config['d2']}, beta={config['beta']}")
        print("-"*60)
        
        # Initialize solver with config name for output directory naming
        solver = ReactionDiffusionSolver(config, config_name=args.config)
        
        # Run the simulation
        solver.run()
        
        # Success message
        print("")
        print("✅ Success! Check rd_outputs/ and rd_logs/ directories.")
        
    except KeyboardInterrupt:
        # Handle user interruption gracefully
        print("")
        print("")
        print("❌ Interrupted by user")
        sys.exit(1)
        
    except FileNotFoundError as e:
        # Handle missing config file
        print("")
        print(f"❌ Error: Configuration file not found: {args.config}")
        print("Please check the file path and try again.")
        sys.exit(1)
        
    except Exception as e:
        # Handle any other errors
        print("")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
