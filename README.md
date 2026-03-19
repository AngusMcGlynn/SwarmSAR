# SwarmSAR

**Research-grade drone swarm coordination simulator for autonomous search and rescue.**

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Status: Active Development](https://img.shields.io/badge/status-active%20development-orange)

## Overview

SwarmSAR is a 2D multi-agent simulation framework for developing, testing, and benchmarking drone swarm coordination algorithms. It models 100+ autonomous agents performing coordinated area search to locate hidden targets across varied terrain. The simulator serves as the foundation for a physical drone swarm system targeting search and rescue, wildlife survey, and disaster response.

The project follows a deliberate pipeline: 2D simulation for rapid algorithm prototyping, NVIDIA Isaac Sim for 3D physics and GPU-accelerated multi-agent reinforcement learning, then deployment onto custom drone hardware.

## Key Features

- 100+ agents running at 60fps rendered, 10,000+ ticks/second headless
- Six pluggable algorithms: random walk, lawnmower (baselines), pheromone swarm, potential field, Voronoi partition, hybrid
- Probabilistic cumulative sensor model with line-of-sight occlusion
- Realistic battery model with return-to-base and recharge cycles
- Mesh communication with gossip protocol and finite information propagation
- Comprehensive metrics and comparison pipeline
- Interactive pygame visualization with pan/zoom, real-time controls, coverage heatmap
- Fully seeded reproducibility for research-grade benchmarking
- Architecture future-proofed for heterogeneous swarms, multi-modal sensors, adversarial environments, and MARL training

## Quick Start

```bash
git clone <repo>
cd swarmsar
pip install -e ".[analysis]"

# Interactive mode with pygame renderer
python -m swarmsar.run --algorithm pheromone

# Headless benchmark
python -m swarmsar.run --algorithm hybrid --headless --seed 42

# Batch comparison across algorithms
python -m swarmsar.run --batch 10 --output-dir results/benchmark
```

## Architecture

```
swarmsar/
  config.py          # SimConfig dataclass -- single source of truth for all parameters
  run.py             # CLI entry point with argparse
  core/
    world.py         # Environment: terrain, obstacles, targets, base station
    agent.py         # Drone state container (no decision logic)
    swarm.py         # Fleet manager with parallel numpy arrays
    simulation.py    # Main loop: tick orchestration, detection, termination
    observation.py   # Observation dataclasses, AgentStatus/AgentRole enums
    action.py        # Action dataclass with static factories
    comms.py         # Mesh communication, gossip protocol, KDTree neighbor lookup
    sensor.py        # SensorModel ABC, ThermalSensorModel, probabilistic detection
    physics.py       # Vectorized kinematic model for all agents
    battery.py       # Drain/recharge model, return-to-base threshold
    metrics.py       # Per-tick recording, aggregation, JSON/CSV export
    environment.py   # Environmental effects stub (wind, GPS denial, jamming)
  algorithms/        # Pluggable coordination algorithms
  rendering/         # pygame visualization (renderer never affects sim state)
  analysis/          # Multi-run comparison, plots, export, replay
```

### Data Flow

```
World -> Observations -> Algorithm -> Actions -> Physics -> Updated State -> Renderer
```

The simulation runs at its own tick rate. The renderer reads state snapshots. Algorithms receive only local observations (no global state) and return actions. This separation means algorithms can be swapped with zero changes to the simulation core.

### Parallel Array Architecture

All agent state is stored as structure-of-arrays numpy arrays in the Swarm class. Dynamic state (positions, velocities, battery levels) and static per-agent parameters (max speeds, sensor radii, comm radii) are all numpy arrays. This enables fully vectorized physics, sensor, and communication updates across 100+ agents.

## Algorithms

**Random Walk** -- Baseline with no coordination. Each agent moves in a random direction, changing heading periodically. Demonstrates the lower bound of swarm performance and the cost of zero communication.

**Lawnmower** -- Systematic back-and-forth scan pattern. Optimal for a single agent but does not benefit from additional agents. Demonstrates that naive parallelism without coordination wastes effort through redundant coverage.

**Pheromone** -- Ant colony inspired approach. Agents deposit virtual pheromone trails that evaporate over time. High pheromone concentration repels agents toward unexplored areas, achieving emergent coverage without explicit task assignment.

**Potential Field** -- Physics-inspired virtual forces. Agents experience attraction toward unexplored frontiers and repulsion from other agents and obstacles. The resultant force determines movement, naturally spreading agents across the search area.

**Voronoi** -- Dynamic area decomposition. The search area is partitioned into Voronoi cells based on agent positions. Each agent is responsible for covering its own cell. Partitions rebalance as agents move, achieving efficient non-overlapping coverage.

**Hybrid** -- Combines Voronoi decomposition for macro-level area assignment, pheromone trails for micro-level exploration within cells, and potential fields for reactive obstacle avoidance and agent spacing. Designed to capture the strengths of all three approaches.

## Adding a New Algorithm

1. Create a file in `swarmsar/algorithms/`
2. Implement the `SwarmAlgorithm` ABC:

```python
from swarmsar.algorithms.base import SwarmAlgorithm
from swarmsar.config import SimConfig
from swarmsar.core.action import Action
from swarmsar.core.observation import Observation


class MyAlgorithm(SwarmAlgorithm):
    name = "my_algorithm"

    def setup(self, config: SimConfig, world_info: dict) -> None:
        # Initialize with config and world info (no target positions)
        pass

    def decide(self, agent_id: int, observation: Observation) -> Action:
        # Return an action based on local observation only
        return Action.idle()
```

3. Register in `swarmsar/algorithms/__init__.py`
4. Run: `python -m swarmsar.run --algorithm my_algorithm`

## Configuration

All parameters live in `swarmsar/config.py` as a `SimConfig` dataclass. Major parameter groups:

| Group | Key Parameters |
|-------|---------------|
| **World** | `world_width`, `world_height`, `num_targets`, `num_obstacles` |
| **Agents** | `num_drones`, `max_speed`, `sensor_radius`, `comm_radius` |
| **Battery** | `battery_capacity`, `battery_drain_rate`, `battery_return_threshold` |
| **Sensor** | `base_detection_probability`, `sensor_distance_falloff`, `sensor_cumulative` |
| **Communication** | `comm_line_of_sight`, `comm_packet_loss`, `comm_gossip_ttl` |
| **Simulation** | `tick_dt`, `max_mission_time`, `seed` |
| **Rendering** | `window_width`, `window_height`, `render_fps`, `show_heatmap` |

Override via JSON config file: `python -m swarmsar.run --config my_config.json`

## Roadmap

- [x] Core simulation framework
- [x] Classical swarm algorithms (pheromone, potential field, Voronoi, hybrid)
- [x] Interactive pygame visualization
- [x] Metrics and benchmarking pipeline
- [ ] Adversarial environments (wind, GPS denial, comm jamming)
- [ ] Heterogeneous swarm with role specialization
- [ ] Multi-modal sensor fusion (thermal + acoustic + visual)
- [ ] Graph Neural Network learned communication (MARL/MAPPO)
- [ ] NVIDIA Isaac Sim 3D environment port
- [ ] Sim-to-real transfer to custom drone hardware
- [ ] Field testing with SAR agencies

## Hardware Targets

**Outdoor SAR (5-inch, ~500g):** 20-25 min flight time, FLIR thermal camera, Raspberry Pi CM4 companion computer, LoRa + ESP-NOW mesh networking. For wilderness search, wildlife survey, and disaster response operations.

**Indoor/Confined Space (3-inch, ~150g):** 8-12 min flight time, FLIR Lepton thermal module, ESP32-S3 companion processor, ESP-NOW mesh networking. For building collapse, mine shaft, and parking structure search operations.

Both platforms run the same coordination algorithms trained in this simulator.

## Research Context

SwarmSAR addresses several open challenges in swarm robotics: sim-to-real transfer of learned coordination policies, emergent communication protocols under bandwidth and range constraints, decentralized decision-making without global state, and scalable multi-agent reinforcement learning. The classical algorithms (pheromone, potential field, Voronoi) serve as baselines for future MARL-trained policies, providing both performance benchmarks and behavioral references for what effective coordination looks like.

## License

MIT

## Contributing

SwarmSAR is currently a solo research project, but contributions are welcome. The algorithm plugin system is the easiest entry point: implement `SwarmAlgorithm`, register it, and submit a PR. See the "Adding a New Algorithm" section above.
