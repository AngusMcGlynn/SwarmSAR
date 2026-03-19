"""Observation dataclasses and agent enums.

Defines the data structures that agents receive from the simulation
each tick, including own state, sensor readings, and neighbor info.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

import numpy as np


class AgentStatus(Enum):
    """Lifecycle status of a drone agent."""
    LAUNCHING = auto()
    ACTIVE = auto()
    RETURNING = auto()
    RECHARGING = auto()
    DEAD = auto()


class AgentRole(Enum):
    """Functional role of a drone agent."""
    STANDARD = auto()
    SCOUT = auto()
    SENSOR = auto()
    RELAY = auto()


@dataclass(frozen=True)
class OwnState:
    """Agent's own state as perceived (may differ from true state under GPS denial).

    Attributes:
        believed_position: Agent's believed position (x, y) in meters.
        velocity: Current velocity vector (vx, vy) in m/s.
        heading: Current heading in radians.
        speed: Current scalar speed in m/s.
        battery: Remaining battery as fraction [0, 1].
        status: Current lifecycle status.
        role: Assigned functional role.
    """
    believed_position: np.ndarray
    velocity: np.ndarray
    heading: float
    speed: float
    battery: float
    status: AgentStatus
    role: AgentRole


@dataclass(frozen=True)
class DetectedEntity:
    """A target detected by the agent's sensor.

    Attributes:
        position: Estimated position (x, y) in meters.
        confidence: Detection confidence [0, 1].
        sensor_type: Type of sensor that made the detection.
        target_id: Identifier of the detected target, if known.
    """
    position: np.ndarray
    confidence: float
    sensor_type: str = "thermal"
    target_id: int | None = None


@dataclass(frozen=True)
class NeighborInfo:
    """Information about a neighboring agent within comm range.

    Attributes:
        agent_id: Identifier of the neighbor.
        position: Last known position (x, y) in meters.
        heading: Last known heading in radians.
        speed: Last known speed in m/s.
        role: Neighbor's functional role.
        battery: Neighbor's battery level as fraction.
    """
    agent_id: int
    position: np.ndarray
    heading: float
    speed: float
    role: AgentRole
    battery: float


@dataclass(frozen=True)
class GossipMessage:
    """Message passed between agents via gossip protocol.

    Attributes:
        sender_id: Original sender agent ID.
        content: Message payload (typically target sighting info).
        ttl: Remaining time-to-live (hops).
        timestamp: Simulation tick when message was created.
    """
    sender_id: int
    content: dict[str, Any]
    ttl: int
    timestamp: float


@dataclass(frozen=True)
class Observation:
    """Complete observation delivered to an agent each tick.

    Attributes:
        own_state: Agent's own perceived state.
        sensor_readings: List of detected entities this tick.
        neighbors: List of neighbors within communication range.
        messages: Gossip messages received this tick.
        local_memory: Agent's persistent local memory dict.
        tick: Current simulation tick number.
        dt: Time step duration in seconds.
    """
    own_state: OwnState
    sensor_readings: list[DetectedEntity] = field(default_factory=list)
    neighbors: list[NeighborInfo] = field(default_factory=list)
    messages: list[GossipMessage] = field(default_factory=list)
    local_memory: dict[str, Any] = field(default_factory=dict)
    tick: int = 0
    dt: float = 0.1
