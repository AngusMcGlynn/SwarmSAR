"""CLI entry point for SwarmSAR simulations.

Usage:
    python -m swarmsar.run --algorithm pheromone
    python -m swarmsar.run --algorithm hybrid --headless --seed 42
    python -m swarmsar.run --batch 10 --output-dir results/benchmark
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)

ALGORITHM_CHOICES = [
    "random_walk",
    "lawnmower",
    "pheromone",
    "potential_field",
    "voronoi",
    "hybrid",
]


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="swarmsar",
        description="SwarmSAR: drone swarm coordination simulator",
    )
    parser.add_argument(
        "--algorithm",
        choices=ALGORITHM_CHOICES,
        default="pheromone",
        help="Swarm coordination algorithm to use (default: pheromone)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (default: from config)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without pygame renderer",
    )
    parser.add_argument(
        "--num-drones",
        type=int,
        default=None,
        help="Override number of drones",
    )
    parser.add_argument(
        "--num-targets",
        type=int,
        default=None,
        help="Override number of targets",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=None,
        help="Override max mission time in seconds",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=None,
        help="Number of runs for batch mode (implies headless)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save results",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to JSON config override file",
    )
    return parser


def build_config(args: argparse.Namespace) -> SimConfig:
    """Build a SimConfig from CLI arguments and optional config file.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Configured SimConfig instance.
    """
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error("Config file not found: %s", args.config)
            sys.exit(1)
        with open(config_path) as f:
            config_data = json.load(f)
        config = SimConfig.from_dict(config_data)
    else:
        config = SimConfig()

    # Apply CLI overrides
    if args.seed is not None:
        config.seed = args.seed
    if args.num_drones is not None:
        config.num_drones = args.num_drones
        config.fleet_composition = {"standard": args.num_drones}
    if args.num_targets is not None:
        config.num_targets = args.num_targets
    if args.max_time is not None:
        config.max_mission_time = args.max_time

    config.validate()
    return config


def get_algorithm_class(name: str):
    """Get the algorithm class by name.

    Args:
        name: Algorithm name matching one of ALGORITHM_CHOICES.

    Returns:
        The algorithm class (not an instance).
    """
    from swarmsar.algorithms import ALGORITHM_REGISTRY
    return ALGORITHM_REGISTRY[name]


def run_single(config: SimConfig, algorithm_name: str, headless: bool,
               output_dir: Path | None = None, run_index: int | None = None) -> dict:
    """Execute a single simulation run.

    Args:
        config: Simulation configuration.
        algorithm_name: Name of the algorithm to use.
        headless: Whether to run without rendering.
        output_dir: Optional directory to save results.
        run_index: Optional run index for batch mode.

    Returns:
        Dictionary of run results/metrics.
    """
    from swarmsar.core.simulation import Simulation

    algorithm_cls = get_algorithm_class(algorithm_name)
    algorithm = algorithm_cls()

    sim = Simulation(config=config, algorithm=algorithm, headless=headless)

    label = f"Run {run_index}" if run_index is not None else "Run"
    logger.info("%s: algorithm=%s, seed=%d, drones=%d, targets=%d",
                label, algorithm_name, config.seed, config.num_drones,
                config.num_targets)

    results = sim.run()

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"_{run_index}" if run_index is not None else ""
        result_path = output_dir / f"{algorithm_name}{suffix}.json"
        with open(result_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        logger.info("Results saved to %s", result_path)

    return results


def main() -> None:
    """Main entry point for the SwarmSAR CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)

    output_dir = Path(args.output_dir) if args.output_dir else None
    headless = args.headless or args.batch is not None

    try:
        if args.batch is not None:
            logger.info("Batch mode: %d runs with algorithm=%s",
                        args.batch, args.algorithm)
            all_results = []
            for i in range(args.batch):
                run_config = SimConfig.from_dict(config.to_dict())
                run_config.seed = config.seed + i
                results = run_single(
                    run_config, args.algorithm, headless=True,
                    output_dir=output_dir, run_index=i,
                )
                all_results.append(results)
            logger.info("Batch complete: %d runs finished", len(all_results))
        else:
            run_single(config, args.algorithm, headless=headless,
                        output_dir=output_dir)
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Shutting down gracefully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
