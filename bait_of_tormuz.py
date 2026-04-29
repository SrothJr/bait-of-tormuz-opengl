from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
GLUT_KEY_SHIFT_R = 113
#==================== VARIABLES ==============================

# system
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
GRID_LENGTH = 1000

# Camera 
camera_angle = 90
camera_height = 500
camera_radius = 400
fovY = 110
camera_mode = 1

# player
player_pos_x = 0
player_pos_y = 0
player_hull_angle = 0
player_turret_angle = 0
speeds = [-0.05, 0, 0.07, 0.14]
gear = 1
player_health = 100
player_max_health = 100
# --- SALMAN'S DOUBLE SPEED BOOST START ---
boost_active = False
# --- SALMAN'S DOUBLE SPEED BOOST END ---

# ships
ships = []
max_ships = 5
ship_spawn_timer = 0
ship_spawn_rate = 1200
ship_speed_min = 0.01
ship_speed_max = 0.03

# weapons

projectiles = []
current_weapon = 1
rpg_ammo = 10
# --- SALMAN'S MISSILE FEATURE START ---
missile_ammo = 5
# --- SALMAN'S MISSILE FEATURE END ---
# --- SALMAN'S TORPEDO FEATURE START ---
torpedo_ammo = 3
# --- SALMAN'S TORPEDO FEATURE END ---
# --- SALMAN'S CHEAT MODE START ---
cheat_mode = False
# --- SALMAN'S CHEAT MODE END ---
firing_cooldown = 0

# Gameplay
score = 0
penalties = 0
max_penalties = 5
game_over = False
total_damage = 0



#===================== FUNCTIONS ==============================
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, WINDOW_WIDTH/WINDOW_HEIGHT, 0.1, 2000)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if camera_mode == 1:
        rad = math.radians(player_turret_angle - 90)
        dir_x = math.cos(rad)
        dir_y = math.sin(rad)

        cam_dist = 100
        cam_z = 100

        cam_x = player_pos_x - (dir_x * cam_dist)
        cam_y = player_pos_y - (dir_y * cam_dist)

        look_x = player_pos_x + (dir_x * 100)
        look_y = player_pos_y + (dir_y * 100)

        gluLookAt(cam_x, cam_y, cam_z,
                  look_x, look_y, 0,
                  0, 0, 1)
    else:
        x = math.cos(math.radians(camera_angle)) * camera_radius
        y = math.sin(math.radians(camera_angle)) * camera_radius

        gluLookAt(x, y, camera_height,
                0, 0, 0,
                0, 0, 1)
    

def draw_sea():
    glBegin(GL_QUADS)
    glColor3f(0.0, 0.3, 0.8)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glEnd()

def draw_land():
    glBegin(GL_QUADS)
    glColor3f(0.7, 0.6, 0.4)

    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH + 150, 30)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH + 150, 30)

    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH - 150, 30)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH - 150, 30)

    glVertex3f(0, -600, 10)
    glVertex3f(-700, -GRID_LENGTH, 20)
    glVertex3f(0, -GRID_LENGTH, 20)
    glVertex3f(700, -GRID_LENGTH, 20)
    glEnd()

def draw_player():
    quad = gluNewQuadric()
    # 1. Boat Hull 
    glPushMatrix()
    glColor3f(0.35, 0.35, 0.4)
    glTranslatef(0, 0, 8)
    glScalef(4.5, 1.4, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    # 2. Bow
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.35)
    glTranslatef(0, 0, 8)
    glRotatef(90, 0, 0, 1)
    glScalef(1.0, 1.2, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    # 3. Cabin Base 
    glPushMatrix()
    # Rotate turret independently from hull
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.25, 0.3, 0.25)  
    glTranslatef(-5, 0, 18)
    glScalef(2.0, 1.2, 1.2)
    glutSolidCube(10)
    glPopMatrix()
    # 4. Turret Head (rotates with turret)  
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.2, 0.25, 0.2)
    glTranslatef(-5, 0, 25)
    glScalef(1.2, 0.8, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    # 5. Gun Barrel (rotates with turret)
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(5, 0, 23)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 1.2, 1.2, 20, 12, 12)
    glPopMatrix()
    
    # 6. Radar (stays with cabin)
    glPushMatrix()
    glColor3f(0.15, 0.15, 0.15)
    glTranslatef(-20, 5, 20)
    glRotatef(180, 1, 0, 0)
    gluCylinder(quad, 0.5, 0.5, 12, 8, 8)
    glPopMatrix()
    
    # 7. Deck strips
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.55)
    glTranslatef(0, 8, 12)
    glScalef(4.0, 0.2, 0.5)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.55)
    glTranslatef(0, -8, 12)
    glScalef(4.0, 0.2, 0.5)
    glutSolidCube(10)
    glPopMatrix()

def draw_cargo_ship(is_red_flag, health, max_health):
    quad = gluNewQuadric()
    
    # 1. Main Hull (long, flat bottom)
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.25)  
    glTranslatef(0, 0, 6)
    glScalef(7.0, 2.0, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    
    # 2. Bow (front)
    glPushMatrix()
    glColor3f(0.18, 0.18, 0.22)
    glTranslatef(30, 0, 6)
    glRotatef(90, 0, 0, 1)
    glScalef(1.0, 1.5, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    
    # 3. Cargo Containers (stacked on deck)
    # Bottom row
    glPushMatrix()
    glColor3f(0.85, 0.5, 0.15) 
    glTranslatef(-5, 0, 12)  
    glScalef(3.5, 1.8, 1.0)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.5, 0.4, 0.3)
    glTranslatef(8, 0, 12) 
    glScalef(2.5, 1.8, 1.0)
    glutSolidCube(10)
    glPopMatrix()
    
    # Top row
    glPushMatrix()
    glColor3f(0.85, 0.5, 0.15)
    glTranslatef(-5, 0, 22)  
    glScalef(2.5, 1.5, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.5, 0.4, 0.7)  
    glTranslatef(8, 0, 22)  
    glScalef(2.0, 1.5, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    
    # 4. Smokestacks (at back)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-25, 10, 10)
    gluCylinder(quad, 3, 3, 18, 10, 10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(-25, -10, 10)
    gluCylinder(quad, 3, 3, 18, 10, 10)
    glPopMatrix()
    
    # 5. Bridge (at back top)
    glPushMatrix()
    glColor3f(0.9, 0.9, 0.95)  # White
    glTranslatef(-28, 0, 16)
    glScalef(2.0, 1.5, 1.2)
    glutSolidCube(10)
    glPopMatrix()
    
    # 6. Flag Pole & Flag
    glPushMatrix()
    glColor3f(0.8, 0.8, 0.8)
    glTranslatef(-30, 0, 22)
    gluCylinder(quad, 0.8, 0.8, 25, 8, 8)
    glPopMatrix()
    
    # Flag 
    glPushMatrix()
    if is_red_flag:
        glColor3f(1.0, 0.0, 0.0)  
    else:
        glColor3f(0.0, 1.0, 0.0)  
    glTranslatef(-30, 0, 40)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(-15, 0, 0)
    glVertex3f(-15, 0, 10)
    glVertex3f(0, 0, 10)
    glEnd()
    glPopMatrix()

def draw_health_bar(health, max_health):
    ratio = health / max_health
    
    glPushMatrix()
    glTranslatef(0, 0, 35)
    
    # Background (red - damage)
    glPushMatrix()
    glColor3f(0.3, 0.0, 0.0)
    glScalef(4.0, 0.8, 0.3)
    glutSolidCube(10)
    glPopMatrix()

    # Foreground (green to red based on health)
    glPushMatrix()
    offset_x = 20.5 * (1 - ratio)
    glTranslatef(offset_x, 0, 0.5)
    if ratio > 0.6:
        glColor3f(0.0, 1.0, 0.0)  # Green
    elif ratio > 0.3:
        glColor3f(1.0, 1.0, 0.0)  # Yellow
    else:
        glColor3f(1.0, 0.0, 0.0)  # Red
    
    glScalef(4.1 * ratio, 0.9, 0.4)
    glutSolidCube(10)
    glPopMatrix()
    glPopMatrix()

def draw_projectiles():
    quad = gluNewQuadric()

    for p in projectiles:
        glPushMatrix()
        glTranslatef(p[0], p[1], 20)

        glScalef(3, 3, 3)

        if p[4] == 1:
            glColor3f(1, 1, 0)
            glutSolidCube(3)
        elif p[4] == 2:
            angle = math.degrees(math.atan2(p[3], p[2]))
            # body
            
            glRotatef(angle, 0, 0, 1)
            glRotatef(90, 0, 1, 0)
            glScalef(2, 2, 2)
            glColor3f(0.5, 0.5, 0.5)
            gluCylinder(quad, 1.5, 1.5, 10, 8, 8)
            # tip
            glTranslatef(0, 0, 10)
            glColor3f(1, 0.3, 0)
            gluSphere(quad, 2, 8, 8)
        # --- SALMAN'S MISSILE FEATURE START ---
        elif p[4] == 3:
            angle = math.degrees(math.atan2(p[3], p[2]))
            glRotatef(angle, 0, 0, 1)
            glRotatef(90, 0, 1, 0)
            glScalef(2, 2, 2)
            glColor3f(0.8, 0.1, 0.1)
            gluCylinder(quad, 1.2, 1.2, 15, 8, 8)
            glTranslatef(0, 0, 15)
            glColor3f(1.0, 1.0, 1.0)
            gluSphere(quad, 1.2, 8, 8)
            glTranslatef(0, 0, -12)
            glColor3f(0.2, 0.2, 0.2)
            glScalef(3, 0.2, 2)
            glutSolidCube(1)
        # --- SALMAN'S MISSILE FEATURE END ---
        # --- SALMAN'S TORPEDO FEATURE START ---
        elif p[4] == 4:
            angle = math.degrees(math.atan2(p[3], p[2]))
            
            glPushMatrix()
            glTranslatef(0, 0, -25)
            glRotatef(angle, 0, 0, 1)
            glRotatef(90, 0, 1, 0)
            glScalef(2, 2, 2)
            glColor3f(0.1, 0.2, 0.2)
            gluCylinder(quad, 1.2, 1.2, 12, 8, 8)
            glTranslatef(0, 0, 12)
            glColor3f(0.15, 0.25, 0.25)
            gluSphere(quad, 1.2, 8, 8)
            glPopMatrix()

            glPushMatrix()
            glTranslatef(0, 0, -20)
            glColor3f(0.8, 0.9, 1.0)
            glutSolidCube(3)
            glTranslatef(-math.cos(math.radians(angle))*8, -math.sin(math.radians(angle))*8, 0)
            glutSolidCube(2)
            glPopMatrix()
        # --- SALMAN'S TORPEDO FEATURE END ---
        glPopMatrix()


def draw_player_dashboard():
    if gear == 0:
        gear_label = "REVERSE"
    elif gear == 1:
        gear_label = "STOP"
    elif gear == 2:
        gear_label = "1/2"
    elif gear == 3:
        gear_label = "FULL"
    
    # --- SALMAN'S DOUBLE SPEED BOOST START ---
    if boost_active:
        gear_label += " (BOOST)"
    # --- SALMAN'S DOUBLE SPEED BOOST END ---
        
    draw_text(50, 40, f"GEAR: {gear_label}")
    draw_text(30, WINDOW_HEIGHT - 40, f"TACTICAL SCORE: {score}")
    draw_text(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 40, f"PENALTIES: {penalties} / {max_penalties}")
    health_bar = "|" * player_health
    draw_text(WINDOW_WIDTH//2 - 200, 25, health_bar)
    draw_text(WINDOW_WIDTH//2 - 65, 50, f"HULL: {int(player_health)}%")
    if current_weapon == 1:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: MG - AMMO : UNLIMITED")
    elif current_weapon == 2:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: RPG - AMMO : {rpg_ammo}")
    # --- SALMAN'S MISSILE FEATURE START ---
    elif current_weapon == 3:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: MISSILE - AMMO : {missile_ammo}")
    # --- SALMAN'S MISSILE FEATURE END ---
    # --- SALMAN'S TORPEDO FEATURE START ---
    elif current_weapon == 4:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: TORPEDO - AMMO : {torpedo_ammo}")
    # --- SALMAN'S TORPEDO FEATURE END ---
    # --- SALMAN'S CHEAT MODE START ---
    status = "ON" if cheat_mode else "OFF"
    draw_text(WINDOW_WIDTH - 400, 65, f"CHEAT MODE: {status}")
    # --- SALMAN'S CHEAT MODE END ---
    draw_text(WINDOW_WIDTH - 400, 15, f"TOTAL DAMAGE DEALT: {int(total_damage)}")




# actions

# --- SALMAN'S MISSILE FEATURE START ---
def get_nearest_red_ship(px, py):
    nearest = None
    min_dist = float('inf')
    for s in ships:
        if s[3]: # is_red
            dist = math.hypot(s[0] - px, s[1] - py)
            if dist < min_dist:
                min_dist = dist
                nearest = s
    return nearest
# --- SALMAN'S MISSILE FEATURE END ---

def fire_weapon():
    global current_weapon, rpg_ammo, missile_ammo, firing_cooldown, torpedo_ammo

    if firing_cooldown > 0:
        return
    if current_weapon == 2 and rpg_ammo <= 0:
        print("No RPG Ammo!")
        return
    # --- SALMAN'S MISSILE FEATURE START ---
    if current_weapon == 3 and missile_ammo <= 0:
        print("No Missile Ammo!")
        return
    # --- SALMAN'S MISSILE FEATURE END ---
    # --- SALMAN'S TORPEDO FEATURE START ---
    if current_weapon == 4 and torpedo_ammo <= 0:
        print("No Torpedo Ammo!")
        return
    # --- SALMAN'S TORPEDO FEATURE END ---
    
    rad = math.radians(player_turret_angle - 90)
    direction_x = math.cos(rad)
    direction_y = math.sin(rad)

    start_x = player_pos_x + (direction_x * 50)
    start_y = player_pos_y + (direction_y * 50)

    if current_weapon == 1:
        speed = 2
        damage = 10
        firing_cooldown = 8
        dx = (direction_x * speed)
        dy = (direction_y * speed)
        projectiles.append([start_x, start_y, dx, dy, current_weapon, damage])
    elif current_weapon == 2:
        speed = 0.5
        damage = 50
        firing_cooldown = 900
        rpg_ammo -= 1
        dx = (direction_x * speed)
        dy = (direction_y * speed)
        projectiles.append([start_x, start_y, dx, dy, current_weapon, damage])
    # --- SALMAN'S MISSILE FEATURE START ---
    elif current_weapon == 3:
        target = get_nearest_red_ship(start_x, start_y)
        if not target:
            print("No red ship detected! Missile abort.")
            return
        
        speed = 0.8
        damage = 90
        firing_cooldown = 1200
        missile_ammo -= 1
        dx = (direction_x * speed)
        dy = (direction_y * speed)
        projectiles.append([start_x, start_y, dx, dy, current_weapon, damage, target])
    # --- SALMAN'S MISSILE FEATURE END ---
    # --- SALMAN'S TORPEDO FEATURE START ---
    elif current_weapon == 4:
        target = get_nearest_red_ship(start_x, start_y)
        if not target:
            print("No red target found!")
            return
        
        speed = 0.4
        damage = 80
        firing_cooldown = 1500
        torpedo_ammo -= 1
        dx = (direction_x * speed)
        dy = (direction_y * speed)
        projectiles.append([start_x, start_y, dx, dy, current_weapon, damage, target])
    # --- SALMAN'S TORPEDO FEATURE END ---


def keyboardListener(key, x, y):
    global player_pos_x, player_pos_y, player_hull_angle, player_turret_angle
    global current_weapon, game_over, score, penalties
    global speeds, gear, player_health, total_damage, rpg_ammo, missile_ammo, torpedo_ammo
    global cheat_mode, boost_active

    turn_speed = 3

    if key == b"w":
        gear = min(3, gear + 1)
    
    if key == b's':
        gear = max(0, gear - 1)

    if key == b'a':
        player_hull_angle += turn_speed
    
    if key == b'd':
        player_hull_angle -= turn_speed

    if key == b"r":
        player_health = 100
        gear = 1
        player_pos_x = 0
        player_pos_y = 0
        game_over = False
        score = 0
        penalties = 0
        total_damage = 0
        rpg_ammo = 10
        # --- SALMAN'S MISSILE FEATURE START ---
        missile_ammo = 5
        # --- SALMAN'S MISSILE FEATURE END ---
        # --- SALMAN'S TORPEDO FEATURE START ---
        torpedo_ammo = 3
        # --- SALMAN'S TORPEDO FEATURE END ---
        # --- SALMAN'S CHEAT MODE START ---
        cheat_mode = False
        # --- SALMAN'S CHEAT MODE END ---
        # --- SALMAN'S DOUBLE SPEED BOOST START ---
        boost_active = False
        # --- SALMAN'S DOUBLE SPEED BOOST END ---

        projectiles.clear()
        ships.clear()
    
    if key == b"1":
        current_weapon = 1
    if key == b"2":
        current_weapon = 2
    # --- SALMAN'S MISSILE FEATURE START ---
    if key == b"3":
        current_weapon = 3
    # --- SALMAN'S MISSILE FEATURE END ---
    # --- SALMAN'S TORPEDO FEATURE START ---
    if key == b"4":
        current_weapon = 4
    # --- SALMAN'S TORPEDO FEATURE END ---
    # --- SALMAN'S CHEAT MODE START ---
    if key == b"c":
        cheat_mode = not cheat_mode
    # --- SALMAN'S CHEAT MODE END ---
    
    # --- SALMAN'S DOUBLE SPEED BOOST START ---
    if key == b" ":
        boost_active = not boost_active
    # --- SALMAN'S DOUBLE SPEED BOOST END ---
        
    

def specialKeyListener(key, x, y):
    global camera_angle, camera_height, player_turret_angle
    if key == GLUT_KEY_LEFT:
        player_turret_angle += 5
    if key == GLUT_KEY_RIGHT:
        player_turret_angle -= 5
    if key == GLUT_KEY_DOWN:
        camera_height -= 20
    if key == GLUT_KEY_UP:
        camera_height += 20
    if key == GLUT_KEY_SHIFT_R:
        fire_weapon()

def mouseListener(button, state, x, y):
    global camera_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        print("Left click works!")
        fire_weapon()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        if camera_mode == 1:
            camera_mode = 0
        else:
            camera_mode = 1

def is_in_strait(x, y):
    if y < -1000 or y > -600:
        return False
    limit_y = -600 - (400/700) * abs(x)
    return y < limit_y

def idle():
    global ship_spawn_timer, ships
    global firing_cooldown, projectiles
    global score, penalties, game_over
    global rpg_ammo, missile_ammo, total_damage, torpedo_ammo
    global speeds, gear, player_pos_x, player_pos_y, player_hull_angle
    global player_health
    global cheat_mode, player_turret_angle, current_weapon, boost_active
    if game_over:
        return

    # --- SALMAN'S DOUBLE SPEED BOOST START ---
    speed_mult = 2.0 if boost_active else 1.0
    dx = math.cos(math.radians(player_hull_angle - 90)) * speeds[gear] * speed_mult
    dy = math.sin(math.radians(player_hull_angle - 90)) * speeds[gear] * speed_mult
    # --- SALMAN'S DOUBLE SPEED BOOST END ---

    next_x = player_pos_x + dx
    next_y = player_pos_y + dy

    can_move = True

    if abs(next_x) > GRID_LENGTH or abs(next_y) > GRID_LENGTH or is_in_strait(next_x, next_y):
        can_move = False
    
    for s in ships:
        if abs(next_x - s[0]) < 185 and abs(next_y - s[1]) < 55:
            can_move = False
            player_health -= 10
            s[4] -= 20
            player_pos_x = player_pos_x - (dx * 700)
            player_pos_y = player_pos_y - (dy * 700)
            gear = 1
            if player_health <= 0:
                game_over = True     
                break
    
    if can_move:
        player_pos_x, player_pos_y = next_x, next_y

    

    if firing_cooldown > 0:
        firing_cooldown -= 1
    
    # --- SALMAN'S CHEAT MODE START ---
    if cheat_mode:
        target = get_nearest_red_ship(player_pos_x, player_pos_y)
        if target:
            target_rad = math.atan2(target[1] - player_pos_y, target[0] - player_pos_x)
            target_angle = math.degrees(target_rad) + 90
            
            diff = (target_angle - player_turret_angle) % 360
            if diff > 180:
                diff -= 360
            
            if abs(diff) > 2.0:
                if diff > 0:
                    player_turret_angle += 2.0
                else:
                    player_turret_angle -= 2.0
            
            if abs(diff) < 5.0 and firing_cooldown <= 0:
                prev_weapon = current_weapon
                current_weapon = 1
                fire_weapon()
                current_weapon = prev_weapon
    # --- SALMAN'S CHEAT MODE END ---

    ship_spawn_timer += 1
    if ship_spawn_timer > ship_spawn_rate and len(ships) < max_ships:
        ship_spawn_timer = 0
        
        y_pos = random.randint(-GRID_LENGTH + 450, GRID_LENGTH - 100)
        
        speed_multiplier = 1 + (score / 1000)
        speed = random.uniform(ship_speed_min, ship_speed_max) * speed_multiplier
        
        red_count = sum(1 for s in ships if s[3])
        if red_count < 2:
            is_red = True
        else:
            is_red = random.choice([True, False])
        
        health = 100 if is_red else 70
        
        # Ship data: [x, y, speed, is_red, health, max_health]
        ships.append([GRID_LENGTH, y_pos, speed, is_red, health, health])
    
    
    for s in ships:
        s[0] -= s[2]  
    
    escaped_ships = [s for s in ships if s[0] < -GRID_LENGTH]
    for s in escaped_ships:
        if s[3]:
            penalties += 1
            print(f"Red ship escaped! Penalty {penalties}")
    
    ships = [s for s in ships if s[0] >= -GRID_LENGTH]

    # Move projectiles
    active_projectiles = []

    for p in projectiles:
        # --- SALMAN'S MISSILE FEATURE START ---
        if p[4] == 3:
            target = p[6]
            if target not in ships:
                continue
            
            angle = math.atan2(target[1] - p[1], target[0] - p[0])
            speed = 0.8
            p[2] = math.cos(angle) * speed
            p[3] = math.sin(angle) * speed
        # --- SALMAN'S MISSILE FEATURE END ---
        # --- SALMAN'S TORPEDO FEATURE START ---
        if p[4] == 4:
            target = p[6]
            if target not in ships:
                continue
            
            angle = math.atan2(target[1] - p[1], target[0] - p[0])
            speed = 0.4
            p[2] = math.cos(angle) * speed
            p[3] = math.sin(angle) * speed
        # --- SALMAN'S TORPEDO FEATURE END ---

        p[0] += p[2]
        p[1] += p[3]

        hit_ship = False
        for s in ships:
            if (s[0] - 140 < p[0] < s[0] + 140) and (s[1] - 40 < p[1] < s[1] + 40):

                s[4] -= p[5]
                total_damage += p[5]
                hit_ship = True 
                print(f"Hit! Total Damage: {total_damage}")

                if s[4] <= 0:
                    if s[3]:
                        score += 100
                        print(f"Red ship destroyed! Score: {score}")

                        if score % 1000 == 0:
                            rpg_ammo += 5
                            penalties = max(0, penalties - 1)
                            player_health = min(100, player_health + 10)
                            print(f"Bonus +5 RPG Ammo! [Total: {rpg_ammo}]")
                            print(f"One penalty reduced! Penalties = {penalties}")

                    else:
                        penalties += 1
                        print(f"Green ship destroyed! Penalties {penalties}")
                break
        
        if not hit_ship and (-GRID_LENGTH - 100 < p[0] < GRID_LENGTH + 100) and (-GRID_LENGTH - 100 < p[1] < GRID_LENGTH + 100):
            active_projectiles.append(p)
            
    projectiles = active_projectiles
    
    ships = [s for s in ships if s[4] > 0]

    if penalties >= max_penalties:
        game_over = True
        print(f"Game over! Finaly Score: {score}")


    
    glutPostRedisplay()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setupCamera()

    # drawinh map
    draw_sea()
    draw_land()

    # player
    glPushMatrix()
    glTranslatef(player_pos_x, player_pos_y, 0)
    glRotatef(player_hull_angle - 90, 0, 0, 1)
    glTranslatef(0, 0, 0)
    glScalef(2, 2, 2)
    draw_player()
    glPopMatrix()

    # ships
    for s in ships:
        glPushMatrix()
        glTranslatef(s[0], s[1], 0)
        glScalef(4, 4, 4)
        draw_cargo_ship(s[3], s[4], s[5])
        draw_health_bar(s[4], s[5])
        glPopMatrix()
    
    # projectiles
    glPushMatrix()
    draw_projectiles()
    glPopMatrix()


    draw_player_dashboard()

    if game_over:
        draw_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2, "GAME OVER")
        draw_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30, f"Score: {score}")
        draw_text(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60, f"Press 'r' to Restart")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bait of Tormuz - Naval Defense")

    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    glutMainLoop()


if __name__ == "__main__":
    main()
