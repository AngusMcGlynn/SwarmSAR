"""Lawnmower systematic scan algorithm.

Single-drone baseline that scans the world in a systematic
back-and-forth pattern. Demonstrates optimal coverage for a
single agent but does not scale with swarm size.
"""

from __future__ import annotations

from swarmsar.algorithms.base import SwarmAlgorithm
from swarmsar.config import SimConfig
from swarmsar.core.action import Action
from swarmsar.core.observation import Observation


class LawnmowerAlgorithm(SwarmAlgorithm):
    """Systematic back-and-forth scan pattern.

    Divides the world into horizontal strips and assigns agents
    to scan them sequentially.

    Attributes:
        name: Algorithm identifier.
    """

    name: str = "lawnmower"

    def setup(self, config: SimConfig, world_info: dict) -> None:
        """Initialize lawnmower scan parameters.

        Args:
            config: Simulation configuration.
            world_info: World information dict.
        """
        pass

    def decide(self, agent_id: int, observation: Observation) -> Action:
        """Compute next lawnmower waypoint action.

        Args:
            agent_id: The agent's unique identifier.
            observation: The agent's current observation.

        Returns:
            Action toward next waypoint in scan pattern.
        """
        pass
