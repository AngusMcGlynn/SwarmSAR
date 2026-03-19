# SwarmSAR

## What This Is

A research-grade 2D drone swarm simulation framework. 100+ autonomous agents perform coordinated area search to locate hidden targets (missing persons, wildlife, survivors in disaster zones). This is the software foundation for a physical drone swarm system that will eventually:

1. Transfer to NVIDIA Isaac Sim for 3D physics, realistic sensors, and GPU-accelerated MARL training
2. Deploy trained policies onto custom drone hardware (5-inch outdoor SAR platform, 3-inch indoor/confined space platform)
3. Operate in real-world SAR, wildlife survey, and disaster response scenarios

Every architectural decision must serve that path. This is not a toy. It is research infrastructure.

## Core Design Principles

1. **Decentralized intelligence.** No agent has global state. No central controller. Intelligence emerges from local observations, local decisions, and neighbor communication. Any algorithm that peeks at global state is wrong.

2. **Algorithm-Agent separation.** Agents observe and act. Algorithms decide. The Algorithm is a pluggable module with a clean interface. Swapping algorithms requires zero changes to Agent, Swarm, World, or Simulation code.

3. **Renderer-Simulation separation.** The simulation runs at its own tick rate. The renderer reads state snapshots. The sim can run headless at maximum speed for batch evaluation or with a pygame renderer attached for interactive development. The renderer never affects simulation state.

4. **Single config source of truth.** Every tunable parameter lives in config.py as a typed dataclass. No magic numbers anywhere in the codebase. Every module receives config, never hardcodes values.

5. **Metrics are first-class citizens.** Every run produces structured, serializable data. Comparing algorithm performance across hundreds of runs must be trivial.

6. **Numpy-vectorized computation.** 100 agents must run at 60+ fps in real-time mode and thousands of ticks/second headless. All per-agent math operates on numpy arrays, not Python loops. The only per-agent Python iteration should be algorithm decide() calls, and even those should support batch mode.

7. **Reproducibility.** Every run is seeded. Same seed + same config + same algorithm = identical results. Non-negotiable for research.

8. **Future-proofed for heterogeneous swarms.** All per-agent parameters (max_speed, sensor_radius, comm_radius, battery_capacity) are stored as per-agent numpy arrays, not scalars. For the base build all values are uniform, but the architecture supports different values per agent (for role-based heterogeneous swarms) with zero refactoring.

9. **Future-proofed for environmental effects.** Physics accepts optional external_forces (wind). Battery accepts optional external_speed_penalty. Sensor supports a SensorModel abstraction. Communication accepts per-agent effective_comm_radii. Observation delivers believed_position (which equals true position when GPS denial is disabled). All disabled by default with zero overhead.

## Architecture

### Module Map

```
swarmsar/
  __init__.py
  config.py                     # SimConfig dataclass, all parameters
  run.py                        # CLI entry point
  core/
    __init__.py
    world.py                    # Environment: terrain, obstacles, targets, base
    agent.py                    # Single drone: state container + physics applicator
    swarm.py                    # Fleet manager: parallel arrays, tick orchestration
    simulation.py               # Main loop: world tick, swarm tick, detection, metrics, termination
    observation.py              # Observation dataclasses, AgentStatus/AgentRole enums
    action.py                   # Action dataclass
    comms.py                    # Communication graph, message passing, gossip protocol
    sensor.py                   # SensorModel ABC, ThermalSensorModel, probabilistic detection, LOS
    physics.py                  # Kinematic model, vectorized position/velocity updates
    battery.py                  # Drain model, recharge logic
    metrics.py                  # Per-tick recording, aggregates, export
    environment.py              # Environmental effects stub: wind, GPS denial, jamming (all disabled by default)
  algorithms/
    __init__.py
    base.py                     # SwarmAlgorithm ABC
    random_walk.py              # Baseline: no coordination
    lawnmower.py                # Baseline: single drone systematic scan
    pheromone.py                # Ant colony inspired: virtual pheromone trails
    potential_field.py          # Physics inspired: virtual forces
    voronoi.py                  # Dynamic area decomposition
    hybrid.py                   # Combines voronoi macro + pheromone micro + potential field reactive
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
    conftest.py                 # Shared fixtures: small_config, default_config, tiny_world
    test_physics.py
    test_battery.py
    test_sensor.py
    test_comms.py
    test_world.py
    test_swarm.py
    test_simulation.py
    test_algorithms.py
    test_metrics.py
```

### Key Data Interfaces

Observation contains: OwnState (believed_position, velocity, heading, speed, battery, status, role), sensor_readings (list of DetectedEntity with confidence and sensor_type), neighbors (list of NeighborInfo with role), gossip messages, local_memory, tick, dt.

Action contains: desired_heading, desired_speed, optional broadcast GossipMessage. Static factories: idle(), toward(), flee_from(), random().

### Key Enums

AgentStatus: LAUNCHING, ACTIVE, RETURNING, RECHARGING, DEAD
AgentRole: STANDARD, SCOUT, SENSOR, RELAY

### Parallel Array Architecture

Swarm stores ALL agent state as structure-of-arrays numpy arrays:
- Dynamic: positions, believed_positions, velocities, headings, speeds, battery_levels, status, active_mask
- Static per-agent: roles, max_speeds, sensor_radii, comm_radii, battery_capacities, battery_drain_rates

This enables fully vectorized physics, sensor, and communication updates.

### Sensor Model

SensorModel ABC with ThermalSensorModel as first implementation. Detection is probabilistic and cumulative (multiple passes increase probability). Confidence field on detections (reflects sensor type count for future multi-modal fusion). Line-of-sight checks against obstacles.

### Communication Model

Mesh network with gossip protocol. KDTree for neighbor lookup. Per-agent comm_radii. Optional LOS blocking. Messages have TTL for hop-limited propagation. Packet loss simulation. Information propagates at finite speed through the swarm.

### Physics Model

Vectorized kinematic updates. Per-agent max_speeds array. Optional external_forces parameter for wind. Smooth turning with max_turn_rate. Smooth acceleration. Boundary bounce. Obstacle collision response.

### Battery Model

Per-agent drain rates and capacities. Drain proportional to speed. Hover is cheaper than moving. Return-to-base threshold trigger. Recharge timer at base station. Optional external_speed_penalty for wind energy cost.

### Algorithm Interface

```python
class SwarmAlgorithm(ABC):
    name: str
    def setup(self, config, world_info) -> None: ...  # world_info has NO target positions
    def decide(self, agent_id, observation) -> Action: ...
    def batch_decide(self, observations) -> dict[int, Action]: ...  # default loops decide()
    def on_detection(self, agent_id, target_id, position) -> None: ...
    def on_agent_lost(self, agent_id) -> None: ...
    def on_agent_launched(self, agent_id) -> None: ...
    def reset(self) -> None: ...
```

## Style Rules

- Python 3.11+, type hints on every function signature
- Dataclasses for all data structures, frozen where immutable
- Numpy vectorized for all per-agent computation, no Python for-loops over agents where avoidable
- Google-style docstrings on every public class and method
- No magic numbers, everything from SimConfig
- No print(), use Python logging module
- f-strings for formatting
- Functions under 40 lines, split if longer
- Pytest for all tests, use conftest.py fixtures
- Do not use em dashes in comments, docstrings, or strings
