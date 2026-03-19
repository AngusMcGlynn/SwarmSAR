"""Tests for the metrics recorder."""

from __future__ import annotations

import numpy as np
import pytest


class TestMetricsRecorder:
    """Tests for metrics recording and aggregation."""

    def test_record_tick(self, tiny_config) -> None:
        """Should record a tick without errors."""
        pass

    def test_summary_after_recording(self, tiny_config) -> None:
        """Summary should be available after recording ticks."""
        pass

    def test_export_json(self, tiny_config, tmp_path) -> None:
        """Should export to JSON without errors."""
        pass

    def test_export_csv(self, tiny_config, tmp_path) -> None:
        """Should export to CSV without errors."""
        pass
