"""Tests for the physics engine."""

from __future__ import annotations

import numpy as np
import pytest


class TestPhysicsEngine:
    """Tests for vectorized kinematic updates."""

    def test_stationary_agents_stay_still(self, tiny_config) -> None:
        """Agents with zero desired speed should not move."""
        pass

    def test_boundary_bounce(self, tiny_config) -> None:
        """Agents should bounce off world boundaries."""
        pass

    def test_heading_update(self, tiny_config) -> None:
        """Headings should update toward desired heading."""
        pass

    def test_speed_clamped_to_max(self, tiny_config) -> None:
        """Speed should not exceed per-agent max_speed."""
        pass

    def test_external_forces_applied(self, tiny_config) -> None:
        """External forces (wind) should affect positions."""
        pass
