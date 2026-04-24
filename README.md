# Bait of Tormuz: Naval Defense

A professional-grade 3D Naval Combat Simulator built using Python and the OpenGL (PyOpenGL) fixed-function pipeline. Defend your waters against enemy cargo ships while navigating complex straits and managing your vessel's propulsion and tactical systems.

---

## 🎮 Game Overview
In **Bait of Tormuz**, you command a modern naval vessel. Your mission is to intercept red-flagged enemy cargo ships. You must manage your ship's speed through a multi-gear system, aim your turret independently of your hull, and ensure you don't damage neutral (green-flagged) vessels.

### Key Features
- **Dual Camera System:** Switch between a strategic orbital view and a modern turret-locked follow camera.
- **Realistic Propulsion:** 4-gear movement system including Reverse, Neutral, and high-speed settings.
- **Tactical Arsenal:** Toggle between a rapid-fire Machine Gun and high-impact RPGs.
- **Dynamic Difficulty:** Enemy ships scale their speed as your score increases, and the game ensures a constant threat level.
- **Advanced HUD:** Professional 2D overlay providing real-time hull integrity, gear status, and tactical data.

---

## 🕹 Controls
| Input | Action |
| :--- | :--- |
| **W / S** | Shift Gears (Up / Down) |
| **A / D** | Rotate Ship Hull (Steering) |
| **Arrow Left / Right** | Rotate Turret Independently |
| **Arrow Up / Down** | Adjust Camera Height (Free Mode) |
| **Mouse Left Click / R-Shift** | Fire Weapon |
| **Mouse Right Click** | Toggle Camera Mode (Free / Follow) |
| **1 / 2** | Switch Weapon (Machine Gun / RPG) |
| **R** | Restart Game / Re-engage |

---

## 🛠 Technical Implementation

### 1. Hybrid 2D/3D Rendering (HUD)
The game uses a sophisticated projection switching technique to render a 2D interface over a 3D environment. This is achieved by disabling depth testing and swapping the projection matrix during the render loop.

```python
def draw_ui_bar(x, y, width, height, ratio, color):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT) # Switch to screen-space
    
    glDisable(GL_DEPTH_TEST) # Ensure UI is always on top
    # ... Draw Quads ...
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
```

### 2. Collision Physics
#### Ship-to-Ship (AABB)
Instead of simple circular distance, the game uses **Axis-Aligned Bounding Boxes (AABB)** to account for the rectangular nature of naval vessels.
```python
# Check if projectile (p) is inside cargo ship (s) boundaries
if (s[0] - 140 < p[0] < s[0] + 140) and (s[1] - 40 < p[1] < s[1] + 40):
    s[4] -= damage # Apply damage
```

#### Terrain Collision (Mathematical Boundaries)
The "Strait" peninsula is defined by linear inequalities, preventing the player from clipping through the land.
```python
def is_in_strait(x, y):
    if y < -1000 or y > -600: return False
    limit_y = -600 - (400/700) * abs(x)
    return y < limit_y # Collision if Y is below the triangle's edge
```

### 3. Ballistics & Weaponry
Projectiles are calculated using the absolute orientation of the turret. RPGs feature a specialized transformation that rotates the model to face its velocity vector.
```python
# Projectile heading calculation
angle = math.degrees(math.atan2(p[3], p[2]))
glRotatef(angle, 0, 0, 1)  # Yaw
glRotatef(90, 0, 1, 0)     # Tip flat onto plane
```

---

## 📸 Screenshots

> **Note to Developer:** To add screenshots, take the following captures and save them in a folder named `docs/`. Replace the placeholders below with your file paths.

### 1. Modern Follow Camera
![Follow Mode Placeholder](docs/follow_camera.png)
*Modern Warship perspective following the turret's orientation.*

### 2. Tactical Engagement
![Combat MG Placeholder](docs/combat_mg.png)
*Machine gun engagement with the dynamic health bar and HUD visible.*

### 3. RPG Ballistics
![Combat RPG Placeholder](docs/combat_rpg.png)
*RPG projectile rotation and impact on enemy hull.*

### 4. Tactical Dashboard
![Dashboard Placeholder](docs/dashboard.png)
*Close-up of the propulsion, hull integrity, and battery status HUD.*

---

## 🚀 Setup & Installation
1. Install Python 3.x.
2. Install requirements:
   ```bash
   pip install PyOpenGL PyOpenGL_accelerate
   ```
3. Run the game:
   ```bash
   python bait_of_tormuz.py
   ```

---

## ⚓ Future Roadmap
- [ ] Implement particle systems for water wakes and explosions.
- [ ] Add sound effects for engine gears and weapon fire.
- [ ] Introduce varying weather conditions (Fog/Night) affecting visibility.
- [ ] Add a Boss-class vessel after 5000 points.
