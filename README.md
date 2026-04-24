# Bait of Tormuz: Naval Defense

A specialized 3D Naval Combat Simulator built with Python and PyOpenGL. This project focuses on tactical navigation, turret ballistics, and real-time fleet management.

---

## 🎮 Gameplay & Mechanics

### 🚢 Vessel Propulsion (Gear System)
The ship operates on a 4-gear discrete movement system. Unlike standard WASD movement, the ship maintains momentum based on its current gear setting:
- **REVERSE:** Negative momentum for backward maneuvering.
- **STOP (Neutral):** Full stop.
- **1/2 SPEED:** Standard cruising speed.
- **FULL SPEED:** Maximum velocity for intercepting distant targets.

### ⚔️ Tactical Arsenal
- **Machine Gun (MG):** Unlimited ammunition, high rate of fire, 10 damage per round.
- **RPG Battery:** High-impact shells dealing 50 damage. Projectiles dynamically rotate to face their trajectory vector for visual realism.

### 🛡️ Survival & Collision
The simulation features advanced world-space interactions:
- **Coastal Barriers:** A mathematical boundary prevents the vessel from entering the "Strait" landmass at the bottom of the map.
- **Naval Impacts:** Colliding with a cargo ship triggers a defensive **knockback** maneuver, resets the vessel to "STOP" gear, and applies significant hull damage (-10).
- **Hull Integrity:** Health is monitored via a dynamic string-based HUD. Scoring 1000 points grants an emergency repair (+10 Hull) and bonus RPG ammo.

---

## 🛠️ Technical Implementation

### 1. Dynamic Text-Based HUD
Instead of complex geometry, the HUD utilizes standard bitmap characters. The health bar is procedurally generated using character repetition, ensuring high visibility regardless of the 3D scene complexity.

```python
def draw_player_dashboard():
    # Hull integrity bar using character repetition
    health_bar = "|" * player_health
    draw_text(WINDOW_WIDTH//2 - 200, 25, health_bar)
```

### 2. Difficulty Scaling
Enemy vessel speed is calculated using a dynamic multiplier that increases as the player's tactical score grows, ensuring the challenge scales with player skill.
```python
# Speed scales by 10% for every 100 points
speed_multiplier = 1 + (score / 1000)
speed = random.uniform(ship_speed_min, ship_speed_max) * speed_multiplier
```

### 3. AABB Collision Logic
The game uses Axis-Aligned Bounding Box (AABB) logic for precise hit registration on rectangular ship models, moving away from simple radius-based circles.
```python
# AABB hit detection for 140x40 bounding boxes
if (s[0] - 140 < p[0] < s[0] + 140) and (s[1] - 40 < p[1] < s[1] + 40):
    s[4] -= damage
```

---

## 🕹️ Controls
- **W / S**: Shift Gears Up/Down.
- **A / D**: Rotate Vessel Hull.
- **Left / Right Arrows**: Independent Turret Rotation.
- **1 / 2**: Toggle Weapons System.
- **Mouse Left / R-Shift**: Fire Main Battery.
- **Mouse Right**: Toggle Camera (Orbital vs. Follow mode).
- **R**: Full Tactical Reset.

---

## 📸 Tactical View (Screenshots)

> **Instructions:** Place screenshots in `/docs` to populate these views.

- **[Follow Camera View]**: docs/follow_camera.png
- **[AABB Collision in Action]**: docs/aabb_view.png
- **[RPG Ballistic Trajectory]**: docs/rpg_facing.png
- **[Naval HUD Overview]**: docs/hud_view.png

---

## 🚀 Setup
```bash
pip install PyOpenGL
python bait_of_tormuz.py
```
