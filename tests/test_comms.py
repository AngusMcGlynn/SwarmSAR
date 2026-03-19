"""Tests for the communication graph."""

from __future__ import annotations

import numpy as np
import pytest


class TestCommGraph:
    """Tests for communication and gossip protocol."""

    def test_neighbors_within_range(self, tiny_config) -> None:
        """Agents within comm_radius should be neighbors."""
        pass

    def test_no_neighbors_beyond_range(self, tiny_config) -> None:
        """Agents beyond comm_radius should not be neighbors."""
        pass

    def test_gossip_propagation(self, tiny_config) -> None:
        """Messages should propagate through the network."""
        pass

    def test_packet_loss(self, tiny_config) -> None:
        """Some messages should be lost with packet_loss > 0."""
        pass

    def test_ttl_expiry(self, tiny_config) -> None:
        """Messages should stop propagating when TTL reaches 0."""
        pass
