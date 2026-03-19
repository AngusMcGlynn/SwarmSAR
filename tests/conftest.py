"""Shared pytest fixtures for SwarmSAR tests.

Provides pre-configured SimConfig instances and mock objects
for fast, isolated unit testing.
"""

from __future__ import annotations

import pytest

from swarmsar.config import SimConfig
from swarmsar.core.action import Action
from swarmsar.core.observation import Observation


@pytest.fixture
def tiny_config() -> SimConfig:
    """Minimal config for fast unit tests.

    100x100 world, 2 drones, 1 target, 60s max time.
    """
    return SimConfig(
        world_width=100.0,
        world_height=100.0,
        num_drones=2,
        num_targets=1,
        num_obstacles=0,
        num_dense_zones=0,
        max_mission_time=60.0,
        seed=1,
        fleet_composition={"standard": 2},
    )


@pytest.fixture
def small_config() -> SimConfig:
    """Small config for integration tests.

    500x500 world, 10 drones, 3 targets, 120s max time.
    """
    return SimConfig(
        world_width=500.0,
        world_height=500.0,
        num_drones=10,
        num_targets=3,
        num_obstacles=3,
        num_dense_zones=1,
        max_mission_time=120.0,
        seed=2,
        fleet_composition={"standard": 10},
    )


@pytest.fixture
def default_config() -> SimConfig:
    """Full default SimConfig."""
    return SimConfig()


class MockAlgorithm:
    """Mock algorithm that always returns idle actions.

    Used for testing simulation infrastructure without
    algorithm logic.
    """

    name = "mock"

    def setup(self, config: SimConfig, world_info: dict) -> None:
        """No-op setup."""
        pass

    def decide(self, agent_id: int, observation: Observation) -> Action:
        """Always return idle."""
        return Action.idle()

    def batch_decide(self, observations: dict[int, Observation]) -> dict[int, Action]:
        """Return idle for all agents."""
        return {aid: Action.idle() for aid in observations}

    def on_detection(self, agent_id: int, target_id: int,
                     position: tuple[float, float]) -> None:
        """No-op."""
        pass

    def on_agent_lost(self, agent_id: int) -> None:
        """No-op."""
        pass

    def on_agent_launched(self, agent_id: int) -> None:
        """No-op."""
        pass

    def reset(self) -> None:
        """No-op."""
        pass


@pytest.fixture
def mock_algorithm() -> MockAlgorithm:
    """A mock algorithm that always returns Action.idle()."""
    return MockAlgorithm()
