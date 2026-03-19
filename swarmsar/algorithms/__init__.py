"""Swarm coordination algorithms.

Registry of available algorithms for plug-and-play selection.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from swarmsar.algorithms.base import SwarmAlgorithm

ALGORITHM_REGISTRY: dict[str, type[SwarmAlgorithm]] = {}


def _register_algorithms() -> None:
    """Lazily register all built-in algorithms."""
    from swarmsar.algorithms.random_walk import RandomWalkAlgorithm
    from swarmsar.algorithms.lawnmower import LawnmowerAlgorithm
    from swarmsar.algorithms.pheromone import PheromoneAlgorithm
    from swarmsar.algorithms.potential_field import PotentialFieldAlgorithm
    from swarmsar.algorithms.voronoi import VoronoiAlgorithm
    from swarmsar.algorithms.hybrid import HybridAlgorithm

    ALGORITHM_REGISTRY.update({
        "random_walk": RandomWalkAlgorithm,
        "lawnmower": LawnmowerAlgorithm,
        "pheromone": PheromoneAlgorithm,
        "potential_field": PotentialFieldAlgorithm,
        "voronoi": VoronoiAlgorithm,
        "hybrid": HybridAlgorithm,
    })


_register_algorithms()
