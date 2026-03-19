"""Heads-up display for real-time metrics and agent info.

Renders an overlay panel showing simulation statistics,
selected agent details, and control hints.
"""

from __future__ import annotations

import logging
from typing import Any

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


class HUD:
    """Heads-up display overlay.

    Shows real-time simulation metrics, selected agent information,
    and keyboard control hints.

    Attributes:
        config: Simulation configuration.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize the HUD.

        Args:
            config: Simulation configuration.
        """
        pass

    def render(self, surface: Any, state: dict[str, Any]) -> None:
        """Render the HUD overlay.

        Args:
            surface: Pygame surface to render onto.
            state: Current simulation state dictionary.
        """
        pass
