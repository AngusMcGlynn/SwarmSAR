"""Environmental effects: wind, GPS denial, and communication jamming.

All effects are disabled by default and have zero overhead when disabled.
This module is a stub for future implementation.
"""

from __future__ import annotations

import logging

import numpy as np

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


class EnvironmentEffects:
    """Manager for environmental effects on the simulation.

    Handles wind forces, GPS denial zones, communication jamming,
    and sensor noise. All effects are disabled by default.

    Attributes:
        config: Simulation configuration.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize environmental effects.

        Args:
            config: Simulation configuration.
        """
        pass

    def get_wind_forces(self, positions: np.ndarray) -> np.ndarray | None:
        """Compute wind forces at given positions.

        Args:
            positions: Agent positions, shape (N, 2).

        Returns:
            Wind force vectors, shape (N, 2), or None if wind disabled.
        """
        pass

    def get_gps_drift(self, positions: np.ndarray) -> np.ndarray | None:
        """Compute GPS position drift for agents.

        Args:
            positions: True agent positions, shape (N, 2).

        Returns:
            Position drift vectors, shape (N, 2), or None if GPS denial disabled.
        """
        pass

    def get_effective_comm_radii(self, base_radii: np.ndarray,
                                  positions: np.ndarray) -> np.ndarray:
        """Compute effective comm radii accounting for jamming.

        Args:
            base_radii: Base communication radii, shape (N,).
            positions: Agent positions, shape (N, 2).

        Returns:
            Effective communication radii, shape (N,).
        """
        pass

    def get_speed_penalty(self, positions: np.ndarray) -> np.ndarray | None:
        """Compute speed penalty from wind for battery drain.

        Args:
            positions: Agent positions, shape (N, 2).

        Returns:
            Speed penalty factors, shape (N,), or None if wind disabled.
        """
        pass
