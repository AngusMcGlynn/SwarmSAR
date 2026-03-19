"""Color palette constants for the renderer.

Centralized color definitions to maintain visual consistency.
"""

from __future__ import annotations

# Background and terrain
BACKGROUND = (20, 20, 30)
TERRAIN = (40, 45, 40)
OBSTACLE = (80, 80, 90)
DENSE_ZONE = (30, 50, 30)

# Agents
AGENT_ACTIVE = (50, 180, 255)
AGENT_RETURNING = (255, 200, 50)
AGENT_RECHARGING = (100, 255, 100)
AGENT_DEAD = (150, 50, 50)
AGENT_LAUNCHING = (200, 200, 200)

# Roles
ROLE_SCOUT = (255, 150, 50)
ROLE_SENSOR = (50, 255, 150)
ROLE_RELAY = (150, 50, 255)

# Targets
TARGET_HIDDEN = (255, 50, 50)
TARGET_FOUND = (50, 255, 50)

# Overlays
COMM_LINK = (100, 100, 150, 80)
SENSOR_RADIUS = (255, 255, 100, 40)
TRAIL = (50, 150, 255, 60)
HEATMAP_COLD = (0, 0, 100)
HEATMAP_HOT = (255, 50, 0)

# UI
HUD_BACKGROUND = (0, 0, 0, 180)
HUD_TEXT = (220, 220, 220)
HUD_HIGHLIGHT = (50, 180, 255)
MINIMAP_BORDER = (150, 150, 150)
BASE_STATION = (255, 255, 100)
