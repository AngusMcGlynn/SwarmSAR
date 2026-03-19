"""World environment: terrain, obstacles, targets, and base station.

Manages the static and semi-static environment that agents operate in.
Generates terrain features, places targets, and defines the base station.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


@dataclass
class Obstacle:
    """A circular obstacle in the world.

    Attributes:
        position: Center position (x, y) in meters.
        radius: Obstacle radius in meters.
    """
    position: np.ndarray
    radius: float


@dataclass
class DenseZone:
    """A zone with reduced sensor effectiveness (e.g., dense vegetation).

    Attributes:
        position: Center position (x, y) in meters.
        radius: Zone radius in meters.
        penalty: Sensor effectiveness multiplier in this zone.
    """
    position: np.ndarray
    radius: float
    penalty: float


@dataclass
class Target:
    """A search target to be found by the swarm.

    Attributes:
        target_id: Unique identifier.
        position: Position (x, y) in meters.
        detectability: Base detectability factor [0, 1].
        found: Whether this target has been detected.
        found_tick: Tick at which target was found, if any.
        found_by: Agent ID that found this target, if any.
    """
    target_id: int
    position: np.ndarray
    detectability: float
    found: bool = False
    found_tick: int | None = None
    found_by: int | None = None


class World:
    """The simulation environment.

    Manages terrain features, obstacles, targets, and the base station.
    Generated procedurally from config and seed.

    Attributes:
        config: Simulation configuration.
        width: World width in meters.
        height: World height in meters.
        base_position: Base station position (x, y).
        obstacles: List of circular obstacles.
        dense_zones: List of dense vegetation zones.
        targets: List of search targets.
    """

    def __init__(self, config: SimConfig, rng: np.random.Generator) -> None:
        """Initialize the world.

        Args:
            config: Simulation configuration.
            rng: Numpy random generator for reproducible placement.
        """
        pass

    def generate_obstacles(self, rng: np.random.Generator) -> list[Obstacle]:
        """Generate random circular obstacles.

        Args:
            rng: Random generator.

        Returns:
            List of generated obstacles.
        """
        pass

    def generate_dense_zones(self, rng: np.random.Generator) -> list[DenseZone]:
        """Generate random dense vegetation zones.

        Args:
            rng: Random generator.

        Returns:
            List of generated dense zones.
        """
        pass

    def generate_targets(self, rng: np.random.Generator) -> list[Target]:
        """Generate random search targets.

        Args:
            rng: Random generator.

        Returns:
            List of generated targets.
        """
        pass

    def check_line_of_sight(self, pos_a: np.ndarray, pos_b: np.ndarray) -> bool:
        """Check if there is clear line of sight between two positions.

        Args:
            pos_a: First position (x, y).
            pos_b: Second position (x, y).

        Returns:
            True if line of sight is clear (no obstacles blocking).
        """
        pass

    def is_in_dense_zone(self, position: np.ndarray) -> tuple[bool, float]:
        """Check if a position is within a dense zone.

        Args:
            position: Position (x, y) to check.

        Returns:
            Tuple of (is_in_zone, penalty_factor).
        """
        pass

    def get_world_info(self) -> dict:
        """Get world information safe to share with algorithms.

        Does NOT include target positions. Algorithms must discover targets.

        Returns:
            Dictionary with world dimensions, obstacles, dense zones, base position.
        """
        pass
