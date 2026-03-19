"""SwarmAlgorithm abstract base class.

All swarm coordination algorithms must implement this interface.
The algorithm receives observations and returns actions, with no
direct access to global simulation state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from swarmsar.config import SimConfig
from swarmsar.core.action import Action
from swarmsar.core.observation import Observation


class SwarmAlgorithm(ABC):
    """Abstract base class for swarm coordination algorithms.

    Algorithms receive per-agent observations and return actions.
    They must not access global state directly.

    Attributes:
        name: Human-readable algorithm name.
    """

    name: str = "base"

    @abstractmethod
    def setup(self, config: SimConfig, world_info: dict) -> None:
        """Initialize the algorithm with config and world info.

        Args:
            config: Simulation configuration.
            world_info: World information dict (NO target positions).
        """
        pass

    @abstractmethod
    def decide(self, agent_id: int, observation: Observation) -> Action:
        """Decide an action for a single agent.

        Args:
            agent_id: The agent's unique identifier.
            observation: The agent's current observation.

        Returns:
            Action to execute this tick.
        """
        pass

    def batch_decide(self, observations: dict[int, Observation]) -> dict[int, Action]:
        """Decide actions for multiple agents at once.

        Default implementation loops over decide(). Override for
        algorithms that benefit from batch processing.

        Args:
            observations: Mapping of agent_id to observation.

        Returns:
            Mapping of agent_id to action.
        """
        return {aid: self.decide(aid, obs) for aid, obs in observations.items()}

    def on_detection(self, agent_id: int, target_id: int,
                     position: tuple[float, float]) -> None:
        """Called when an agent detects a target.

        Args:
            agent_id: The detecting agent's ID.
            target_id: The detected target's ID.
            position: The target's position.
        """
        pass

    def on_agent_lost(self, agent_id: int) -> None:
        """Called when an agent is lost (battery dead).

        Args:
            agent_id: The lost agent's ID.
        """
        pass

    def on_agent_launched(self, agent_id: int) -> None:
        """Called when an agent launches from base.

        Args:
            agent_id: The launched agent's ID.
        """
        pass

    def reset(self) -> None:
        """Reset algorithm state for a new run."""
        pass
