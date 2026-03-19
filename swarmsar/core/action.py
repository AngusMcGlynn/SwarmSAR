"""Action dataclass for agent decisions.

Defines the action space that algorithms output each tick.
Includes static factory methods for common actions.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from swarmsar.core.observation import GossipMessage


@dataclass(frozen=True)
class Action:
    """Action output from an algorithm's decide() call.

    Attributes:
        desired_heading: Target heading in radians.
        desired_speed: Target speed in m/s.
        broadcast: Optional gossip message to send to neighbors.
    """
    desired_heading: float = 0.0
    desired_speed: float = 0.0
    broadcast: GossipMessage | None = None

    @staticmethod
    def idle() -> Action:
        """Create an idle action (hover in place).

        Returns:
            Action with zero speed.
        """
        return Action(desired_heading=0.0, desired_speed=0.0)

    @staticmethod
    def toward(from_pos: tuple[float, float], to_pos: tuple[float, float],
               speed: float) -> Action:
        """Create an action moving toward a target position.

        Args:
            from_pos: Current position (x, y).
            to_pos: Target position (x, y).
            speed: Desired speed in m/s.

        Returns:
            Action heading toward the target position.
        """
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        heading = math.atan2(dy, dx)
        return Action(desired_heading=heading, desired_speed=speed)

    @staticmethod
    def flee_from(from_pos: tuple[float, float], threat_pos: tuple[float, float],
                  speed: float) -> Action:
        """Create an action fleeing from a threat position.

        Args:
            from_pos: Current position (x, y).
            threat_pos: Threat position (x, y).
            speed: Desired speed in m/s.

        Returns:
            Action heading away from the threat.
        """
        dx = from_pos[0] - threat_pos[0]
        dy = from_pos[1] - threat_pos[1]
        heading = math.atan2(dy, dx)
        return Action(desired_heading=heading, desired_speed=speed)

    @staticmethod
    def random(speed: float) -> Action:
        """Create an action with a random heading.

        Args:
            speed: Desired speed in m/s.

        Returns:
            Action with random heading.
        """
        heading = random.uniform(0, 2 * math.pi)
        return Action(desired_heading=heading, desired_speed=speed)
