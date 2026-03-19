"""Multi-run comparison and statistical significance testing.

Tools for comparing algorithm performance across multiple
simulation runs with statistical rigor.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RunComparator:
    """Compare results across multiple simulation runs.

    Loads results from multiple runs and computes comparative
    statistics with significance testing.

    Attributes:
        results: List of loaded run results.
    """

    def __init__(self) -> None:
        """Initialize the comparator."""
        pass

    def load_results(self, result_dir: Path) -> None:
        """Load all results from a directory.

        Args:
            result_dir: Directory containing result JSON files.
        """
        pass

    def compare(self, metric: str) -> dict[str, Any]:
        """Compare algorithms on a specific metric.

        Args:
            metric: Name of the metric to compare.

        Returns:
            Dictionary with comparison statistics.
        """
        pass

    def significance_test(self, algorithm_a: str, algorithm_b: str,
                          metric: str) -> dict[str, Any]:
        """Run statistical significance test between two algorithms.

        Args:
            algorithm_a: First algorithm name.
            algorithm_b: Second algorithm name.
            metric: Metric to compare.

        Returns:
            Dictionary with test statistic, p-value, and effect size.
        """
        pass
