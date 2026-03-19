"""Tests for sensor models."""

from __future__ import annotations

import numpy as np
import pytest


class TestThermalSensorModel:
    """Tests for the thermal sensor model."""

    def test_detection_probability_decreases_with_distance(self, tiny_config) -> None:
        """Detection probability should decrease with distance."""
        pass

    def test_dense_zone_reduces_detection(self, tiny_config) -> None:
        """Dense zones should reduce detection probability."""
        pass

    def test_no_detection_beyond_radius(self, tiny_config) -> None:
        """Targets beyond sensor radius should not be detected."""
        pass

    def test_cumulative_detection(self, tiny_config) -> None:
        """Multiple passes should increase detection probability."""
        pass
