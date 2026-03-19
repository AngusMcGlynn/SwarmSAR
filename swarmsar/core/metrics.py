"""Metrics recording, aggregation, and export.

Records per-tick simulation data and computes aggregate metrics
for algorithm comparison and analysis.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from swarmsar.config import SimConfig

logger = logging.getLogger(__name__)


@dataclass
class TickRecord:
    """Data recorded at each simulation tick.

    Attributes:
        tick: Tick number.
        time: Simulation time in seconds.
        targets_found: Cumulative count of found targets.
        coverage_percent: Percentage of area covered.
        active_agents: Number of active agents.
        mean_battery: Mean battery level of active agents.
        mean_speed: Mean speed of active agents.
    """
    tick: int
    time: float
    targets_found: int
    coverage_percent: float
    active_agents: int
    mean_battery: float
    mean_speed: float


class MetricsRecorder:
    """Records and aggregates simulation metrics.

    Attributes:
        config: Simulation configuration.
        records: List of per-tick records.
    """

    def __init__(self, config: SimConfig) -> None:
        """Initialize the metrics recorder.

        Args:
            config: Simulation configuration.
        """
        pass

    def record_tick(self, tick: int, time: float,
                    targets_found: int, coverage_percent: float,
                    active_agents: int, battery_levels: np.ndarray,
                    speeds: np.ndarray, active_mask: np.ndarray) -> None:
        """Record data for one simulation tick.

        Args:
            tick: Current tick number.
            time: Current simulation time.
            targets_found: Cumulative targets found.
            coverage_percent: Current coverage percentage.
            active_agents: Number of active agents.
            battery_levels: All battery levels, shape (N,).
            speeds: All speeds, shape (N,).
            active_mask: Active agent mask, shape (N,).
        """
        pass

    def get_summary(self) -> dict[str, Any]:
        """Compute aggregate summary metrics.

        Returns:
            Dictionary of summary statistics.
        """
        pass

    def export_json(self, path: Path) -> None:
        """Export metrics to a JSON file.

        Args:
            path: Output file path.
        """
        pass

    def export_csv(self, path: Path) -> None:
        """Export per-tick records to a CSV file.

        Args:
            path: Output file path.
        """
        pass
