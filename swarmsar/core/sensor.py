"""Sensor models for target detection.

Defines the SensorModel ABC and ThermalSensorModel implementation.
Detection is probabilistic, cumulative, and respects line-of-sight.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

import numpy as np

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


class SensorModel(ABC):
    """Abstract base class for sensor models.

    Sensor models compute detection probabilities based on
    range, environment, and sensor characteristics.
    """

    @abstractmethod
    def detection_probability(self, distance: float, detectability: float,
                              in_dense_zone: bool, dense_penalty: float) -> float:
        """Compute probability of detecting a target.

        Args:
            distance: Distance to target in meters.
            detectability: Target's base detectability factor.
            in_dense_zone: Whether target is in a dense zone.
            dense_penalty: Sensor penalty in dense zones.

        Returns:
            Detection probability [0, 1].
        """
        pass


class ThermalSensorModel(SensorModel):
    """Thermal infrared sensor model.

    Models a FLIR-style thermal sensor with distance falloff
    and environmental penalties.

    Attributes:
        config: Simulation configuration.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize the thermal sensor model.

        Args:
            config: Simulation configuration.
        """
        pass

    def detection_probability(self, distance: float, detectability: float,
                              in_dense_zone: bool, dense_penalty: float) -> float:
        """Compute thermal detection probability.

        Args:
            distance: Distance to target in meters.
            detectability: Target's base detectability factor.
            in_dense_zone: Whether target is in a dense zone.
            dense_penalty: Sensor penalty in dense zones.

        Returns:
            Detection probability [0, 1].
        """
        pass

    def check_detections(self, agent_positions: np.ndarray,
                         sensor_radii: np.ndarray,
                         target_positions: np.ndarray,
                         active_mask: np.ndarray) -> list[tuple[int, int, float]]:
        """Check for detections between agents and targets.

        Args:
            agent_positions: Agent positions, shape (N, 2).
            sensor_radii: Per-agent sensor radii, shape (N,).
            target_positions: Target positions, shape (M, 2).
            active_mask: Boolean mask of active agents, shape (N,).

        Returns:
            List of (agent_id, target_id, confidence) tuples.
        """
        pass
