"""Pan/zoom camera system for the renderer.

Handles world-to-screen coordinate transforms, smooth pan
and zoom, and keyboard/mouse camera controls.
"""

from __future__ import annotations

import numpy as np

from swarmsar.config import SimConfig


class Camera:
    """2D camera with pan and zoom.

    Transforms between world coordinates (meters) and screen
    coordinates (pixels). Supports smooth zoom and pan via
    keyboard and mouse input.

    Attributes:
        config: Simulation configuration.
        offset: Camera offset in world coordinates.
        zoom: Current zoom level.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize the camera.

        Args:
            config: Simulation configuration.
        """
        pass

    def world_to_screen(self, world_pos: np.ndarray) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates.

        Args:
            world_pos: Position in world coordinates (x, y).

        Returns:
            Screen coordinates (px, py).
        """
        pass

    def screen_to_world(self, screen_pos: tuple[int, int]) -> np.ndarray:
        """Convert screen coordinates to world coordinates.

        Args:
            screen_pos: Screen coordinates (px, py).

        Returns:
            World coordinates (x, y).
        """
        pass

    def pan(self, dx: float, dy: float) -> None:
        """Pan the camera.

        Args:
            dx: Horizontal pan in world units.
            dy: Vertical pan in world units.
        """
        pass

    def zoom_in(self, factor: float, center: tuple[int, int] | None = None) -> None:
        """Zoom in on a point.

        Args:
            factor: Zoom factor (> 1 to zoom in).
            center: Screen coordinates to zoom toward.
        """
        pass

    def zoom_out(self, factor: float, center: tuple[int, int] | None = None) -> None:
        """Zoom out from a point.

        Args:
            factor: Zoom factor (> 1 to zoom out).
            center: Screen coordinates to zoom from.
        """
        pass
