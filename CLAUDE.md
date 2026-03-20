# Swarm Search Simulator

## What This Is

A research-grade 2D drone swarm simulation framework. 100+ autonomous agents perform coordinated area search to locate hidden targets (missing persons, wildlife, survivors in disaster zones). This is the software foundation for a physical drone swarm system that will eventually:

1. Transfer to NVIDIA Isaac Sim for 3D physics, realistic sensors, and GPU-accelerated MARL training
2. Deploy trained policies onto custom 3-inch (~150g) drone hardware
3. Operate in real-world SAR, wildlife survey, and disaster response scenarios

Every architectural decision must serve that path. This is not a toy. It is research infrastructure.

## Core Design Principles

1. **Decentralized intelligence.** No agent has global state. No central controller. Intelligence emerges from local observations, local decisions, and neighbor communication. Any algorithm that peeks at global state is wrong.

2. **Algorithm-Agent separation.** Agents observe and act. Algorithms decide. The Algorithm is a pluggable module with a clean interface. Swapping algorithms requires zero changes to Agent, Swarm, World, or Simulation code.

3. **Renderer-Simulation separation.** The simulation runs at its own tick rate. The renderer reads state snapshots. The sim can run headless at maximum speed for batch evaluation or with a pygame renderer attached for interactive development. The renderer never affects simulation state.

4. **Single config source of truth.** Every tunable parameter lives in config.py as a typed dataclass. No magic numbers anywhere in the codebase. Every module receives config, never hardcodes values.

5. **Metrics are first-class citizens.** Every run produces structured, serializable data. Comparing algorithm performance across hundreds of runs must be trivial. Metrics drive research; they are not an afterthought.

6. **Numpy-vectorized computation.** 100 agents must run at 60+ fps in real-time mode and thousands of ticks/second headless. All per-agent math (physics, sensors, communication distance, battery) operates on numpy arrays, not Python loops. The only per-agent Python iteration should be algorithm decide() calls, and even those should support batch mode.

7. **Reproducibility.** Every run is seeded. Same seed + same config + same algorithm = identical results. This is non-negotiable for research.

## Architecture

### Module Map

```
swarm-sim/
  CLAUDE.md                     # This file
  config.py                     # SimConfig dataclass, all parameters
  run.py                        # CLI entry point
  core/
    __init__.py
    world.py                    # Environment: terrain, obstacles, targets, base
    agent.py                    # Single drone: state container + physics applicator
    swarm.py                    # Fleet manager: parallel arrays, tick orchestration
    simulation.py               # Main loop: world tick, swarm tick, detection, metrics, termination
    observation.py              # Observation/Action dataclasses
    action.py                   # Action dataclass
    comms.py                    # Communication graph, message passing, gossip protocol
    sensor.py                   # Probabilistic detection model, LOS checks, sensor type abstraction
    physics.py                  # Kinematic model, vectorized position/velocity updates
    battery.py                  # Drain model, recharge logic
    metrics.py                  # Per-tick recording, aggregates, export
    environment.py              # Environmental effects: wind, GPS denial, jamming (all disabled by default, stubs for future)
  algorithms/
    __init__.py
    base.py                     # SwarmAlgorithm ABC
    random_walk.py              # Baseline: no coordination
    lawnmower.py                # Baseline: single drone systematic scan
    pheromone.py                # Ant colony inspired: virtual pheromone trails
    potential_field.py          # Physics inspired: virtual forces
    voronoi.py                  # Dynamic area decomposition
    hybrid.py                   # Combines potential field macro + pheromone micro
  rendering/
    __init__.py
    pygame_renderer.py          # Main renderer: terrain, agents, targets, overlays
    camera.py                   # Pan/zoom camera system
    colors.py                   # Color palette constants
    hud.py                      # Heads-up display: metrics panel, agent info
    effects.py                  # Visual effects: trails, detection flashes, scan pulses
    minimap.py                  # Minimap overlay for zoomed-in views
  analysis/
    __init__.py
    compare.py                  # Multi-run comparison, statistical significance
    plots.py                    # Publication-quality matplotlib figures
    export.py                   # JSON/CSV/Parquet export
    replay.py                   # Load and replay recorded runs
  tests/
    __init__.py
    test_physics.py
    test_battery.py
    test_sensor.py
    test_comms.py
    test_world.py
    test_swarm.py
    test_simulation.py
    test_algorithms.py
    test_metrics.py
    conftest.py                 # Shared fixtures: default config, small world, mock algorithm
```

### config.py -- SimConfig Dataclass

Every parameter with its default. Grouped logically.

**World:**
- world_width: 2000.0 (meters)
- world_height: 2000.0
- num_targets: 8
- target_detectability_range: (0.6, 0.95) -- targets have varying difficulty
- num_obstacles: 15
- obstacle_radius_range: (20.0, 80.0)
- num_dense_zones: 5
- dense_zone_radius_range: (50.0, 150.0)
- dense_zone_sensor_penalty: 0.4 -- detection multiplier in dense terrain
- base_station_position: None -- defaults to (world_width/2, world_height * 0.05) i.e. center-bottom

**Agents:**
- num_drones: 100
- max_speed: 12.0 (m/s, ~43 km/h, realistic for 3-inch quad)
- min_speed: 1.0 (m/s, minimum forward speed when moving)
- max_turn_rate: 3.0 (rad/s, ~170 deg/s, realistic for micro quad)
- acceleration: 8.0 (m/s^2, how quickly speed changes)
- sensor_radius: 40.0 (meters, thermal detection effective range)
- comm_radius: 200.0 (meters, mesh radio effective range)
- launch_spacing: 0.5 (seconds between sequential drone launches at mission start, they do not all launch simultaneously)

**Agent Roles (future-proofing for heterogeneous swarms):**
- AgentRole enum: STANDARD, SCOUT, SENSOR, RELAY (defined in observation.py)
- fleet_composition: {"standard": 100} (default: all standard. Future: {"scout": 20, "sensor": 30, "relay": 10, "standard": 40})
- Role stat modifiers (multipliers applied to base config values):
  - STANDARD: all 1.0 (no modification)
  - SCOUT: speed 1.3, sensor_radius 0.6, battery_capacity 0.7, comm_radius 1.0
  - SENSOR: speed 0.7, sensor_radius 1.5, battery_capacity 1.2, comm_radius 1.0
  - RELAY: speed 1.0, sensor_radius 0.0 (no detection), battery_capacity 1.3, comm_radius 2.0
- For the base build, fleet_composition is all STANDARD and modifiers are all 1.0, but the per-agent stat arrays (max_speeds, sensor_radii, comm_radii, battery_capacities) exist from day one as Nx1 numpy arrays in Swarm rather than scalar config values. This means physics, sensor, comms, and battery functions all accept per-agent arrays, not scalars. When roles are enabled later, the arrays simply get different values per agent with zero refactoring.

**Battery:**
- battery_capacity: 600.0 (seconds of flight at max speed, ~10 min)
- battery_drain_rate: 1.0 (drain per second at max speed)
- battery_hover_drain_multiplier: 0.5 (hovering uses less energy)
- battery_return_threshold: 0.20 (return when 20% remaining)
- recharge_time: 120.0 (seconds to full recharge at base)

**Sensor:**
- base_detection_probability: 0.85 (at distance 0, perfect conditions)
- detection_distance_falloff: 2.0 (exponent for distance-based probability decay)
- dense_zone_detection_penalty: 0.4 (multiplier in dense terrain)
- detection_cooldown: 2.0 (seconds before same agent can re-check same target)
- cumulative_detection: True (multiple passes increase probability)

**Communication:**
- comm_line_of_sight: True (obstacles block comms)
- packet_loss_rate: 0.02 (2% message drop probability)
- gossip_ttl: 5 (max hops for message propagation)
- message_max_age: 30.0 (seconds before gossip messages expire)

**Pheromone Algorithm:**
- pheromone_grid_resolution: 10.0 (meters per cell)
- pheromone_deposit_rate: 1.0
- explored_pheromone_decay_halflife: 120.0 (seconds)
- alert_pheromone_decay_halflife: 30.0
- pheromone_separation_weight: 1.5
- pheromone_exploration_weight: 1.0
- pheromone_alert_weight: 2.0
- pheromone_noise_weight: 0.3

**Potential Field Algorithm:**
- pf_separation_radius: 30.0 (meters)
- pf_separation_strength: 2.0
- pf_frontier_attraction: 1.0
- pf_detection_attraction: 3.0
- pf_exploration_grid_resolution: 10.0
- pf_random_perturbation: 0.2

**Voronoi Algorithm:**
- voronoi_local_only: True (compute from known neighbors, not global)
- voronoi_coverage_speed: 0.8 (fraction of max speed during cell coverage)
- voronoi_frontier_bias: 1.5 (preference for cells near unexplored territory)

**Simulation:**
- tick_dt: 0.1 (seconds per simulation tick)
- max_mission_time: 1800.0 (30 minutes max)
- random_seed: 42
- stagger_launch: True (drones launch sequentially, not all at once)

**Environment Effects (all disabled by default, stubs for frontier upgrades):**
- enable_wind: False
- wind_base_speed: 4.0 (m/s, only used if enable_wind is True)
- enable_gps_denial: False
- gps_denial_zones: 0
- gps_drift_rate: 0.5 (m/s of position error accumulation in denial zones)
- enable_comm_jamming: False
- enable_sensor_noise: False
- sensor_false_positive_rate: 0.0 (probability of phantom detection per tick per agent)
When all enable_* flags are False, the environment module has zero overhead. These exist so the config schema does not change when frontier features are activated.

**Rendering:**
- window_width: 1400
- window_height: 900
- target_fps: 60
- show_comm_links: False (toggle with C)
- show_heatmap: True (toggle with H)
- show_trails: True
- trail_length: 50 (ticks of trail history)
- show_sensor_radius: False (toggle with S, showing 100 circles is noisy)
- camera_zoom_speed: 0.1
- minimap_size: 200

### core/world.py -- World

Continuous 2D space. No grid for movement (agents use float positions). Contains:

**Terrain Features:**
- Obstacles: list of Circle(center: vec2, radius: float). Block movement, block sensor LOS, block communication LOS. Agents cannot path through obstacles.
- Dense Zones: list of Circle(center: vec2, radius: float). Reduce sensor detection probability by dense_zone_sensor_penalty multiplier. Do NOT block movement or LOS.
- Open Ground: everything else. Full sensor effectiveness.

**Targets:**
- list of Target(id, position: vec2, detectability: float, is_found: bool, found_by: int, found_at_tick: int, found_at_time: float)
- detectability varies per target within target_detectability_range
- Placed using Poisson disk sampling for spatial distribution, with optional clustering (some scenarios have targets near each other, simulating a group of lost hikers)

**Base Station:**
- Single point. Drones launch from here and return here to recharge.
- Has a small "landing zone" radius. Multiple drones can recharge simultaneously (no queue for MVP).

**Procedural Generation:**
- Seeded RNG for reproducibility
- Obstacles placed with Poisson disk sampling (min distance = largest radius * 2)
- Dense zones can overlap obstacles (vegetation around rocks is realistic)
- Targets never placed inside obstacles
- One "corridor" guaranteed between base and far end of map (agents can always reach the full area)
- World generates a terrain_grid (discretized at sensor resolution) on init for efficient terrain lookups

**Spatial Queries (all numpy vectorized):**
- get_terrain_at(positions: Nx2) -> N terrain types
- get_detection_modifier(positions: Nx2) -> N float multipliers
- check_los(from_pos: 2, to_pos: 2) -> bool (ray-circle intersection)
- check_los_batch(from_pos: Nx2, to_pos: Mx2) -> NxM bool matrix
- check_collision(positions: Nx2) -> N bool (inside any obstacle?)
- get_obstacles_near(position: 2, radius: float) -> list of obstacles

### core/agent.py -- Agent

State container for a single drone. All per-agent state is stored BOTH on the Agent object AND in the Swarm's parallel numpy arrays (the Agent holds an index into those arrays for efficient access).

**State:**
- id: int
- role: AgentRole (default STANDARD, from fleet_composition assignment)
- position: vec2 (true position, reference into swarm array)
- believed_position: vec2 (what the agent thinks its position is. Equals true position when GPS is available. Diverges in GPS denial zones. Observations use believed_position, NOT true position. For the base build with GPS denial disabled, believed_position always equals position.)
- velocity: vec2
- heading: float (radians, 0 = east/right, pi/2 = north/up)
- speed: float
- battery_level: float
- status: enum (LAUNCHING, ACTIVE, RETURNING, RECHARGING, DEAD)
- local_memory: LocalMemory

**LocalMemory:**
- visited_grid: discretized bool grid of where this agent has been (resolution = sensor_radius)
- personal_detections: list of (target_id, position, tick, confidence)
- relayed_detections: list of (target_id, position, tick, confidence, source_agent, hops)
- neighbor_coverage: sparse representation of what coverage data neighbors have shared

**Behavior:**
- apply_action(action, dt): delegate to physics module, update battery, update local memory
- check_status(): transition logic (ACTIVE -> RETURNING if battery low, RETURNING -> RECHARGING if at base, RECHARGING -> LAUNCHING if charged, any -> DEAD if battery == 0 and not at base)
- get_return_heading(): angle from current position to base station

### core/swarm.py -- Swarm (Fleet Manager)

**CRITICAL: Parallel Array Architecture.**

All agent state is stored as structure-of-arrays, not array-of-structures:
```python
# Dynamic state (changes every tick)
positions: ndarray          # (N, 2) float64, true positions
believed_positions: ndarray # (N, 2) float64, what agents believe (equals positions when GPS denial disabled)
velocities: ndarray         # (N, 2) float64
headings: ndarray           # (N,) float64
speeds: ndarray             # (N,) float64
battery_levels: ndarray     # (N,) float64
status: ndarray             # (N,) int8 (enum)
active_mask: ndarray        # (N,) bool

# Static per-agent stats (set on init from role modifiers, constant during sim)
roles: ndarray              # (N,) int8 (AgentRole enum)
max_speeds: ndarray         # (N,) float64 (base max_speed * role modifier)
sensor_radii: ndarray       # (N,) float64 (base sensor_radius * role modifier)
comm_radii: ndarray         # (N,) float64 (base comm_radius * role modifier)
battery_capacities: ndarray # (N,) float64 (base capacity * role modifier)
battery_drain_rates: ndarray # (N,) float64 (base drain * role modifier)
```

For the base build with all-STANDARD fleet, the static arrays are uniform (every element equals the config value). But because physics, sensor, comms, and battery functions accept these as arrays rather than scalars, enabling heterogeneous roles later requires zero code changes to those modules.

Individual Agent objects hold their index and reference the swarm arrays. This architecture enables fully vectorized physics, sensor, and communication updates.

**Tick Sequence:**
1. Update staggered launch (launch next drone if launch timer has elapsed)
2. Build communication graph via CommunicationManager
3. Collect Observation for each active agent
4. Call algorithm.batch_decide(observations) or per-agent decide()
5. Apply actions: vectorized physics update on all active agents
6. Update batteries: vectorized drain computation
7. Status transitions: check return threshold, check at-base, check dead
8. Handle recharging: tick recharge timers, relaunch when full
9. Return tick summary (new detections, coverage delta, etc.)

### core/observation.py and core/action.py -- Data Interfaces
```python
@dataclass(frozen=True)
class OwnState:
    position: ndarray          # (2,) believed position (may differ from true position in GPS denial)
    velocity: ndarray          # (2,)
    heading: float
    speed: float
    battery_level: float
    battery_capacity: float
    status: AgentStatus
    role: AgentRole            # STANDARD, SCOUT, SENSOR, RELAY

@dataclass(frozen=True)
class DetectedEntity:
    entity_type: str           # "obstacle", "dense_zone", "target", "agent"
    position: ndarray          # (2,)
    distance: float
    relative_angle: float      # angle from agent heading
    confidence: float          # 0.0-1.0, detection confidence. For base build with single thermal sensor, this equals detection probability. With multi-modal fusion, reflects number of confirming sensor types.
    sensor_type: str           # "thermal" for base build. Future: "acoustic", "visual", "fused"

@dataclass(frozen=True)
class NeighborInfo:
    agent_id: int
    position: ndarray
    heading: float
    speed: float
    battery_level: float
    role: AgentRole            # so algorithms can make role-aware decisions

@dataclass(frozen=True)
class GossipMessage:
    type: str                  # "detection", "coverage", "alert"
    origin_agent: int
    origin_tick: int
    position: ndarray          # relevant position
    data: dict                 # flexible payload
    hops: int
    ttl: int

@dataclass(frozen=True)
class Observation:
    own_state: OwnState
    sensor_readings: list[DetectedEntity]
    neighbors: list[NeighborInfo]
    messages: list[GossipMessage]
    local_memory: LocalMemory
    tick: int
    dt: float

@dataclass
class Action:
    desired_heading: float     # radians
    desired_speed: float       # 0 to max_speed
    broadcast: Optional[GossipMessage] = None

    @staticmethod
    def idle() -> Action: ...

    @staticmethod
    def toward(position, from_position, speed) -> Action: ...
```

### core/sensor.py -- Probabilistic Detection Model

**Sensor Type Abstraction:**
The sensor system is built around a SensorModel base class. The base build ships with ThermalSensorModel only. Future upgrades add AcousticSensorModel and VisualSensorModel. The abstraction exists from day one so adding new sensor types is purely additive (new class, register in config) with no changes to the detection pipeline.
```python
class SensorModel(ABC):
    name: str  # "thermal", "acoustic", "visual"
    @abstractmethod
    def detection_probability(self, distance, sensor_radius, base_prob, target_detect, terrain_mod, **kwargs) -> float: ...

class ThermalSensorModel(SensorModel):
    """Default and only sensor for base build. Distance-based probability with terrain modifier."""
```

The check_detections_batch function accepts a list of SensorModel instances and produces a fused probability. With a single sensor, fusion is a no-op (just the thermal result). With multiple sensors, fusion = 1 - product(1 - p_i). Confidence score = count of sensors with p > threshold. For the base build, confidence always reflects the single thermal reading.

Detection is NOT binary. It is probabilistic and cumulative.

**Single-pass detection probability:**
p = base_detectability * target_detectability * terrain_modifier * distance_falloff
distance_falloff = max(0, 1 - (d / sensor_radius) ^ detection_distance_falloff_exponent)
terrain_modifier = dense_zone_sensor_penalty if in dense zone, else 1.0

**Line of sight:** Ray from agent to target. If ray intersects any obstacle circle, detection is blocked (p = 0).

**Cumulative detection:** Each target tracks how many sensor passes it has received. Cumulative probability:
p_cumulative = 1 - product(1 - p_i for each pass i)
A target is "found" when a random roll against p_cumulative succeeds. This means multiple flyovers of a difficult area increase the chance of finding someone. Algorithms that intelligently re-search uncertain areas will outperform those that only pass once.

**Vectorized implementation:** Check all active agents against all unfound targets in one numpy operation. The distance matrix is (num_active, num_unfound), which is at most (100, 8). Trivial to compute. Note: sensor_radii are per-agent arrays (from role modifiers). The distance check uses each agent's individual sensor_radius, not a global scalar. Relay agents with sensor_radius = 0 automatically produce zero detection probability.

### core/environment.py -- Environmental Effects (Stub for Base Build)

Manages optional environmental effects: wind, GPS denial, communication jamming, sensor noise. In the base build, ALL effects are disabled via config flags (enable_wind=False, etc.). When disabled, the module's tick() method returns immediately with no computation. The module exists as a clean extension point for frontier upgrades.

The Simulation tick loop calls environment.tick() which returns an EnvironmentState:
```python
@dataclass
class EnvironmentState:
    wind_vectors: Optional[ndarray] = None       # (N, 2) or None if wind disabled
    gps_available: Optional[ndarray] = None      # (N,) bool or None if GPS denial disabled
    effective_comm_radii: Optional[ndarray] = None # (N,) or None if jamming disabled
    sensor_noise_mask: Optional[ndarray] = None  # (N,) bool or None if sensor noise disabled
```
When all fields are None (base build), downstream systems skip all environment-related logic via simple None checks. Zero overhead. When frontier features are enabled, the fields are populated and passed to physics (wind_vectors as external_forces), observation builder (gps_available for believed_position divergence), comms (effective_comm_radii override), and sensor (sensor_noise_mask for false positives).

### core/comms.py -- Communication Model

**Connectivity Graph:**
- Built each tick from agent positions
- Use scipy.spatial.cKDTree for O(N log N) neighbor queries
- Two agents are connected if: distance < min(agent_a_comm_radius, agent_b_comm_radius) AND (if comm_line_of_sight enabled) LOS check passes. Note: comm_radii are per-agent arrays (from role modifiers), not a single scalar. Two agents connect if they are within the smaller of their two radii.
- Result: adjacency list per agent

**Message Passing:**
- Each agent can attach one GossipMessage to its Action
- Messages delivered to all connected neighbors
- Each message has a TTL (hops remaining). When relayed, TTL decrements. At 0, message dies.
- Each message has an age. Messages older than message_max_age are discarded.
- Packet loss: each delivery has packet_loss_rate probability of failure
- Agents maintain a MessageBuffer of received messages, deduplicated by (origin_agent, origin_tick, type)

**Gossip Protocol:**
- When agent A receives a message from agent B, it can relay that message to its own neighbors next tick (with decremented TTL)
- This creates information propagation at finite speed through the swarm
- A detection at the north edge of the map takes multiple ticks to reach agents at the south edge
- This is realistic and a key constraint that algorithms must handle

### core/physics.py -- Kinematic Model (Vectorized)
```python
def update_agents(
    positions: ndarray,    # (N, 2) current positions
    headings: ndarray,     # (N,) current headings
    speeds: ndarray,       # (N,) current speeds
    desired_headings: ndarray,  # (N,) target headings from actions
    desired_speeds: ndarray,    # (N,) target speeds from actions
    max_speeds: ndarray,   # (N,) per-agent max speed (from role modifiers)
    min_speed: float,
    max_turn_rate: float,
    acceleration: float,
    dt: float,
    world_bounds: tuple,   # (width, height)
    active_mask: ndarray,  # (N,) bool
    external_forces: Optional[ndarray] = None,  # (N, 2) optional external force vectors (e.g., wind). Added to velocity after heading/speed update. None = no external forces. For base build, always None. When wind is enabled, pass wind vectors here.
) -> tuple[ndarray, ndarray, ndarray]:
    """Returns updated (positions, headings, speeds) for all agents."""
```

- Heading update: rotate toward desired_heading at max_turn_rate. Use shortest angular path. Snap if within one tick of target.
- Speed update: accelerate/decelerate toward desired_speed at acceleration rate. Clamp to [0, max_speeds] (per-agent).
- Position update: pos += [cos(heading) * speed, sin(heading) * speed] * dt. If external_forces is not None, add external_forces * dt to position as well.
- Boundary: clamp to world bounds, bounce heading off walls.
- Obstacle collision: if new position is inside obstacle, revert to previous position and deflect heading. (Simple: treat obstacles as hard walls.)

### core/battery.py -- Battery Model (Vectorized)
```python
def update_batteries(
    battery_levels: ndarray,    # (N,)
    speeds: ndarray,            # (N,)
    max_speeds: ndarray,        # (N,) per-agent max speed (from role modifiers)
    base_drain_rates: ndarray,  # (N,) per-agent drain rate (from role/battery_capacity modifiers)
    hover_drain_multiplier: float,
    dt: float,
    active_mask: ndarray,       # (N,)
    external_speed_penalty: Optional[ndarray] = None,  # (N,) optional additional drain from e.g. fighting wind. None = no penalty. Added to base drain.
) -> ndarray:
    """Returns updated battery levels."""
    # drain = base_rate * lerp(hover_multiplier, 1.0, speed/max_speed) * dt
    # if external_speed_penalty is not None: drain += external_speed_penalty * dt
```

### core/metrics.py -- Metrics System

**Per-Tick Snapshot (stored as columnar numpy arrays):**
- tick, elapsed_time
- num_active, num_returning, num_recharging, num_dead
- coverage_percentage (unique area covered / total searchable area)
- targets_found (cumulative)
- total_distance_this_tick (sum of all agent distances)
- total_energy_this_tick (sum of all agent battery drain)
- mean_battery_level
- communication_graph_edges (how connected is the swarm)
- messages_in_flight

**Aggregate Metrics:**
- time_to_find_all: seconds until all targets found (None if mission timeout)
- time_to_first_find: seconds to first detection
- time_to_find_each: list of individual find times
- coverage_at_time(t): what % was covered at time t
- energy_efficiency: targets_found / total_energy_consumed
- search_rate: area_covered / time
- redundant_coverage_ratio: total_sensor_area_swept / unique_area_covered (lower is better, 1.0 is perfect)
- mean_time_between_finds: average gap between successive finds
- swarm_utilization: fraction of time drones are actively searching (not returning/recharging)

**Export:** JSON (full run), CSV (tick data), summary dict, matplotlib-ready arrays.

**Comparison:** Load multiple MetricsResult objects, compute mean/std across seeds, generate comparison dataframes.

### Rendering -- Pygame Visualization

**Main View:**
- Camera with pan (click-drag or WASD) and zoom (scroll wheel)
- Terrain: open ground as muted green/tan, dense zones as darker patches with texture, obstacles as gray/brown circles with slight shadow
- Base station: distinct icon/shape, glowing when drones are recharging
- Drones: small triangles colored by status (green=active, yellow=returning, blue=recharging, red=dead). Point in heading direction. Size scales with zoom.
- Sensor radius: translucent circle, only shown for selected drone or on toggle
- Communication links: faint lines between connected drones (toggle C)
- Drone trails: fading polyline showing last N positions. Color matches drone status.
- Targets: completely invisible until found, then flash with expanding ring effect and persist as a marker with detection info
- Coverage heatmap: translucent overlay, green=searched, dark=unsearched, alpha-blended (toggle H)

**HUD (always visible):**
- Top bar: elapsed time, tick count, simulation speed multiplier
- Right panel: targets found/total, coverage %, active/returning/recharging/dead counts, average battery, algorithm name
- Bottom: minimap showing full world with agent dots and coverage overlay

**Controls:**
- Space: pause/unpause
- [ / ]: decrease/increase simulation speed (0.25x, 0.5x, 1x, 2x, 4x, 8x, 16x)
- Left click: select nearest drone (shows its info, sensor radius, personal coverage)
- Right click: kill nearest drone (for resilience testing)
- T: place new target at mouse position
- H: toggle heatmap overlay
- C: toggle communication links
- S: toggle sensor radius display
- R: restart simulation (same config, new seed)
- 1-6: switch algorithm (1=random, 2=lawnmower, 3=pheromone, 4=potential_field, 5=voronoi, 6=hybrid)
- Tab: cycle algorithms
- Escape: quit
- WASD / arrow keys: pan camera
- Scroll: zoom in/out
- Home: reset camera to full view

**Performance Target:** 60fps with 100 agents, all effects enabled. The renderer should never be the bottleneck.

### Algorithms -- Interface
```python
class SwarmAlgorithm(ABC):
    """Base class for all swarm coordination algorithms."""

    name: str  # Display name

    @abstractmethod
    def setup(self, config: SimConfig, world_info: WorldInfo) -> None:
        """Called once before simulation starts. WorldInfo contains terrain layout but NOT target positions."""

    @abstractmethod
    def decide(self, agent_id: int, observation: Observation) -> Action:
        """Decide action for a single agent based on its local observation."""

    def batch_decide(self, observations: dict[int, Observation]) -> dict[int, Action]:
        """Decide actions for multiple agents. Default: loop over decide(). Override for vectorized implementations."""
        return {aid: self.decide(aid, obs) for aid, obs in observations.items()}

    def on_detection(self, agent_id: int, target_id: int, position: ndarray) -> None:
        """Called when an agent detects a target. Use for algorithm-specific reactions."""
        pass

    def on_agent_lost(self, agent_id: int) -> None:
        """Called when a drone dies or is killed. Use for reallocation logic."""
        pass

    def on_agent_launched(self, agent_id: int) -> None:
        """Called when a drone (re)launches from base."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state for a new run."""
```

WorldInfo is a read-only summary of the world that does NOT include target positions: world bounds, obstacle positions/radii, dense zone positions/radii, base position. Algorithms must discover targets through search, never by cheating.

### Algorithm Descriptions

**RandomWalk:** Each agent picks random heading, flies for random duration (5-15s), picks new heading. No coordination. No communication. Lower bound on performance.

**Lawnmower:** Single agent (agent 0) performs boustrophedon scan of entire area. Row spacing = sensor_radius * 1.5. Returns to base when battery low, resumes from interruption point. All other agents stay at base. This represents current single-drone SAR operations.

**Pheromone:** Two-channel virtual pheromone grid. "Explored" channel: agents deposit pheromone as they search, decays with configurable half-life. Agents are repelled by high explored-pheromone (avoid re-searching). "Alert" channel: deposited on detection, attracts nearby agents for confirmation, decays faster. Decision: compute local pheromone gradient, add separation force, add noise, combine into heading/speed. Grid is globally written but locally read (within sensor_radius).

**PotentialField:** Virtual forces on each agent. Separation (repel from neighbors), frontier attraction (toward boundary of explored/unexplored), detection attraction (toward unconfirmed finds from gossip), exploration repulsion (away from well-covered areas), random perturbation. Forces summed into resultant vector for heading/speed.

**Voronoi:** Dynamic area decomposition. Each agent computes local Voronoi partition using known neighbor positions. Responsible for searching own cell. Flies to nearest unexplored point in cell. Cells dynamically resize as agents move. Dead/returning agents' cells absorbed by neighbors. Within-cell coverage uses a spiraling outward pattern from cell centroid.

**Hybrid:** Combines Voronoi macro-allocation (which region am I responsible for) with pheromone micro-navigation (how do I search within my region). Uses potential field separation to maintain spacing. Intended to be the strongest classical algorithm, benchmarked against the others and eventually against RL-trained policies.

## Style Rules

- Python 3.11+, type hints on every function signature and variable where non-obvious
- Dataclasses for all data structures, frozen where the data should be immutable
- Numpy vectorized for all per-agent computation, no Python for-loops over agents where avoidable
- Docstrings on every public class and method (Google style)
- No magic numbers. Every constant comes from SimConfig.
- No print(). Use Python logging module. DEBUG for verbose, INFO for key events, WARNING for issues.
- f-strings for string formatting
- Keep functions short. If a function exceeds 40 lines, split it.
- Tests for every module. Pytest. Use conftest.py for shared fixtures.
- Do not use em dashes in any comments, docstrings, or strings.
