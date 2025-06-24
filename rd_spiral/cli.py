"""Command-line interface."""

import sys
import os
import argparse
from .core import parse_config, ReactionDiffusionSolver


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="rd_spiral: Reaction-diffusion spiral wave solver"
    )
    parser.add_argument('config', help='Configuration file path')
    parser.add_argument('--version', action='version', version='0.1.0')
    
    args = parser.parse_args()
    
    # Check if config exists
    if not os.path.exists(args.config):
        import pkg_resources
        try:
            config_path = pkg_resources.resource_filename('rd_spiral', f'configs/{args.config}')
            if os.path.exists(config_path):
                args.config = config_path
        except:
            pass
    
    try:
        print("="*60)
        print("RD-SPIRAL: Reaction-Diffusion Solver")
        print("="*60)
        
        config = parse_config(args.config)
        print(f"Configuration: {args.config}")
        print(f"Parameters: d1={config['d1']}, d2={config['d2']}, beta={config['beta']}")
        print("-"*60)
        
        solver = ReactionDiffusionSolver(config, config_name=args.config)
        solver.run()
        
        print("\nSuccess! Check rd_outputs/ and rd_logs/ directories.")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
