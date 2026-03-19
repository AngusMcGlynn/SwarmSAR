"""Minimap overlay for zoomed-in views.

Renders a small overview map showing the entire world,
agent positions, and the current camera viewport.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


class Minimap:
    """Minimap overlay renderer.

    Shows a scaled-down view of the entire world with agent
    positions and the current camera viewport rectangle.

    Attributes:
        config: Simulation configuration.
        size: Minimap size in pixels.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize the minimap.

        Args:
            config: Simulation configuration.
        """
        pass

    def render(self, surface: Any, positions: np.ndarray,
               active_mask: np.ndarray, camera: Any) -> None:
        """Render the minimap overlay.

        Args:
            surface: Pygame surface to render onto.
            positions: Agent positions, shape (N, 2).
            active_mask: Active agent mask, shape (N,).
            camera: Camera for viewport rectangle display.
        """
        pass
