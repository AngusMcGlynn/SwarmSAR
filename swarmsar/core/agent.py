"""Agent state container for individual drones.

Each agent is a state container. Decision-making is handled by
the algorithm module, not by the agent itself.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from swarmsar.config import SimConfig
from swarmsar.core.observation import AgentRole, AgentStatus

logger = logging.getLogger(__name__)


class Agent:
    """State container for a single drone agent.

    Agents hold their own state but do not make decisions.
    The algorithm module reads observations and produces actions.

    Attributes:
        agent_id: Unique identifier.
        status: Current lifecycle status.
        role: Assigned functional role.
        position: True position (x, y) in meters.
        believed_position: Believed position (equals true when GPS is reliable).
        velocity: Current velocity vector (vx, vy) in m/s.
        heading: Current heading in radians.
        speed: Current scalar speed in m/s.
        battery_level: Remaining battery as fraction [0, 1].
        local_memory: Persistent per-agent memory dict for algorithm use.
    """

    def __init__(self, agent_id: int, config: SimConfig,
                 role: AgentRole = AgentRole.STANDARD) -> None:
        """Initialize an agent.

        Args:
            agent_id: Unique identifier for this agent.
            config: Simulation configuration.
            role: Functional role assignment.
        """
        pass

    def reset(self, base_position: np.ndarray) -> None:
        """Reset agent state for a new run.

        Args:
            base_position: Starting position at base station.
        """
        pass
