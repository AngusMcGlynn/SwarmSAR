"""Random walk baseline algorithm.

No coordination between agents. Each agent moves in a random
direction, changing heading periodically. Serves as the simplest
baseline for comparison.
"""

from __future__ import annotations

import numpy as np

from swarmsar.algorithms.base import SwarmAlgorithm
from swarmsar.config import SimConfig
from swarmsar.core.action import Action
from swarmsar.core.observation import Observation


class RandomWalkAlgorithm(SwarmAlgorithm):
    """Random walk with no inter-agent coordination.

    Each agent picks a random heading and maintains it for a
    random duration before choosing a new heading.

    Attributes:
        name: Algorithm identifier.
    """

    name: str = "random_walk"

    def setup(self, config: SimConfig, world_info: dict) -> None:
        """Initialize random walk parameters.

        Args:
            config: Simulation configuration.
            world_info: World information dict.
        """
        pass

    def decide(self, agent_id: int, observation: Observation) -> Action:
        """Choose a random action.

        Args:
            agent_id: The agent's unique identifier.
            observation: The agent's current observation.

        Returns:
            Action with random heading.
        """
        pass
