"""SimConfig dataclass containing all simulation parameters.

Single source of truth for every tunable parameter in SwarmSAR.
All modules receive config rather than hardcoding values.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class SimConfig:
    """Complete simulation configuration.

    Every tunable parameter lives here. Grouped by subsystem.
    All defaults are research-validated starting points.
    """

    # --- World ---
    world_width: float = 2000.0
    world_height: float = 2000.0
    num_targets: int = 8
    target_detectability_min: float = 0.6
    target_detectability_max: float = 0.95
    num_obstacles: int = 15
    obstacle_radius_min: float = 20.0
    obstacle_radius_max: float = 80.0
    num_dense_zones: int = 5
    dense_zone_radius_min: float = 50.0
    dense_zone_radius_max: float = 150.0
    dense_zone_penalty: float = 0.4
    base_position: tuple[float, float] | None = None  # None = center-bottom

    # --- Agents ---
    num_drones: int = 100
    max_speed: float = 12.0
    min_speed: float = 1.0
    max_turn_rate: float = 3.0
    acceleration: float = 8.0
    sensor_radius: float = 40.0
    comm_radius: float = 200.0
    launch_spacing: float = 0.5
    fleet_composition: dict[str, int] = field(
        default_factory=lambda: {"standard": 100}
    )
    role_modifiers: dict[str, dict[str, float]] = field(
        default_factory=lambda: {
            "scout": {"max_speed": 1.3, "sensor_radius": 0.7, "battery_capacity": 0.8},
            "sensor": {"max_speed": 0.8, "sensor_radius": 1.5, "battery_capacity": 0.9},
            "relay": {"max_speed": 1.0, "comm_radius": 2.0, "battery_capacity": 1.1},
        }
    )

    # --- Battery ---
    battery_capacity: float = 600.0
    battery_drain_rate: float = 1.0
    battery_hover_multiplier: float = 0.5
    battery_return_threshold: float = 0.20
    battery_recharge_time: float = 120.0

    # --- Sensor ---
    base_detection_probability: float = 0.85
    sensor_distance_falloff: float = 2.0
    sensor_dense_penalty: float = 0.4
    sensor_cooldown: float = 2.0
    sensor_cumulative: bool = True

    # --- Communication ---
    comm_line_of_sight: bool = True
    comm_packet_loss: float = 0.02
    comm_gossip_ttl: int = 5
    comm_message_max_age: float = 30.0

    # --- Algorithm: Pheromone ---
    pheromone_deposit_rate: float = 1.0
    pheromone_evaporation_rate: float = 0.05
    pheromone_grid_resolution: float = 10.0
    pheromone_repulsion_strength: float = 2.0
    pheromone_attraction_strength: float = 0.5

    # --- Algorithm: Potential Field ---
    potential_field_agent_repulsion: float = 50.0
    potential_field_obstacle_repulsion: float = 100.0
    potential_field_frontier_attraction: float = 30.0
    potential_field_base_attraction: float = 10.0
    potential_field_decay: float = 2.0

    # --- Algorithm: Voronoi ---
    voronoi_update_interval: float = 5.0
    voronoi_overlap_margin: float = 0.1
    voronoi_rebalance_threshold: float = 0.3

    # --- Simulation ---
    tick_dt: float = 0.1
    max_mission_time: float = 1800.0
    seed: int = 42
    stagger_launch: bool = True

    # --- Environment (all disabled by default) ---
    enable_wind: bool = False
    wind_base_speed: float = 4.0
    enable_gps_denial: bool = False
    gps_drift_rate: float = 0.5
    enable_comm_jamming: bool = False
    enable_sensor_noise: bool = False
    sensor_false_positive_rate: float = 0.0

    # --- Rendering ---
    window_width: int = 1400
    window_height: int = 900
    render_fps: int = 60
    show_comm_links: bool = False
    show_heatmap: bool = True
    show_trails: bool = True
    trail_length: int = 50
    show_sensor_radius: bool = False
    camera_zoom_speed: float = 0.1
    minimap_size: int = 200

    def to_dict(self) -> dict:
        """Serialize config to a plain dictionary.

        Returns:
            Dictionary of all config parameters.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> SimConfig:
        """Create a SimConfig from a dictionary.

        Args:
            data: Dictionary of config parameters. Unknown keys are ignored.

        Returns:
            New SimConfig instance with values from the dictionary.
        """
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    def validate(self) -> list[str]:
        """Validate config for nonsensical parameter combinations.

        Raises:
            ValueError: If any critical validation fails.

        Returns:
            List of warning messages for non-critical issues.
        """
        warnings: list[str] = []

        # Critical errors
        if self.num_drones < 1:
            raise ValueError("num_drones must be >= 1")
        if self.battery_return_threshold > 1.0:
            raise ValueError("battery_return_threshold must be <= 1.0")
        if self.battery_return_threshold < 0.0:
            raise ValueError("battery_return_threshold must be >= 0.0")
        if self.tick_dt <= 0:
            raise ValueError("tick_dt must be > 0")
        if self.max_mission_time <= 0:
            raise ValueError("max_mission_time must be > 0")
        if self.world_width <= 0 or self.world_height <= 0:
            raise ValueError("World dimensions must be > 0")
        if self.num_targets < 0:
            raise ValueError("num_targets must be >= 0")
        if self.battery_capacity <= 0:
            raise ValueError("battery_capacity must be > 0")
        if self.max_speed <= 0:
            raise ValueError("max_speed must be > 0")
        if self.comm_packet_loss < 0 or self.comm_packet_loss > 1:
            raise ValueError("comm_packet_loss must be between 0 and 1")

        # Warnings
        if self.sensor_radius > self.comm_radius:
            msg = (
                f"sensor_radius ({self.sensor_radius}) > comm_radius "
                f"({self.comm_radius}): agents can detect targets they "
                f"cannot report to neighbors"
            )
            warnings.append(msg)
            logger.warning(msg)

        if self.battery_return_threshold < 0.1:
            msg = (
                f"battery_return_threshold ({self.battery_return_threshold}) "
                f"is very low: agents may not make it back to base"
            )
            warnings.append(msg)
            logger.warning(msg)

        if self.num_drones > 500:
            msg = (
                f"num_drones ({self.num_drones}) is very high: "
                f"may impact rendering performance"
            )
            warnings.append(msg)
            logger.warning(msg)

        total_fleet = sum(self.fleet_composition.values())
        if total_fleet != self.num_drones:
            msg = (
                f"fleet_composition total ({total_fleet}) does not match "
                f"num_drones ({self.num_drones})"
            )
            warnings.append(msg)
            logger.warning(msg)

        return warnings
