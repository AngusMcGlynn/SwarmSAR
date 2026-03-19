"""Tests for swarm algorithms."""

from __future__ import annotations

import pytest

from swarmsar.core.action import Action


class TestAlgorithmInterface:
    """Tests that all algorithms implement the interface correctly."""

    def test_random_walk_returns_action(self, tiny_config) -> None:
        """RandomWalkAlgorithm.decide() should return an Action."""
        pass

    def test_lawnmower_returns_action(self, tiny_config) -> None:
        """LawnmowerAlgorithm.decide() should return an Action."""
        pass

    def test_pheromone_returns_action(self, tiny_config) -> None:
        """PheromoneAlgorithm.decide() should return an Action."""
        pass

    def test_potential_field_returns_action(self, tiny_config) -> None:
        """PotentialFieldAlgorithm.decide() should return an Action."""
        pass

    def test_voronoi_returns_action(self, tiny_config) -> None:
        """VoronoiAlgorithm.decide() should return an Action."""
        pass

    def test_hybrid_returns_action(self, tiny_config) -> None:
        """HybridAlgorithm.decide() should return an Action."""
        pass

    def test_batch_decide(self, tiny_config) -> None:
        """batch_decide should return actions for all agents."""
        pass
