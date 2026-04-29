from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time

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
firing_cooldown = 0

# Gameplay
score = 0
penalties = 0
max_penalties = 5
game_over = False
total_damage = 0

# ==================== DRONE (FLIES TO ENEMY SHIPS) ====================
drone_active = False
drone_spawning = False
drone_x = 0
drone_y = 0
drone_z = 35
drone_target_ship = None      # The enemy ship drone is targeting
drone_target_x = 0
drone_target_y = 0
drone_shoot_cooldown = 0
drone_damage = 100
drone_arrived = False          # Drone has reached target enemy
drone_attack_range = 100       # Distance to hover from enemy

# ==================== HOMING MINES ====================
mines = []
mine_cooldown = 0
mine_cooldown_max = 1200
max_mines = 4
mine_damage = 100

# ==================== LEARNER MODE (15 STEPS) ====================
learner_mode = False
learner_step = 1
learner_message = ""
learner_waiting = True
learner_step_complete = False
practice_ship = None


#===================== DRAW FUNCTIONS ==============================

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
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
        cam_x = player_pos_x - (dir_x * 100)
        cam_y = player_pos_y - (dir_y * 100)
        look_x = player_pos_x + (dir_x * 100)
        look_y = player_pos_y + (dir_y * 100)
        gluLookAt(cam_x, cam_y, 100, look_x, look_y, 0, 0, 0, 1)
    else:
        x = math.cos(math.radians(camera_angle)) * camera_radius
        y = math.sin(math.radians(camera_angle)) * camera_radius
        gluLookAt(x, y, camera_height, 0, 0, 0, 0, 0, 1)

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
    glPushMatrix()
    glColor3f(0.35, 0.35, 0.4)
    glTranslatef(0, 0, 8)
    glScalef(4.5, 1.4, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.3, 0.3, 0.35)
    glTranslatef(0, 0, 8)
    glRotatef(90, 0, 0, 1)
    glScalef(1.0, 1.2, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    glColor3f(0.25, 0.3, 0.25)  
    glTranslatef(-5, 0, 18)
    glScalef(2.0, 1.2, 1.2)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    glColor3f(0.2, 0.25, 0.2)
    glTranslatef(-5, 0, 25)
    glScalef(1.2, 0.8, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(5, 0, 23)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 1.2, 1.2, 20, 12, 12)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.15, 0.15, 0.15)
    glTranslatef(-20, 5, 20)
    glRotatef(180, 1, 0, 0)
    gluCylinder(quad, 0.5, 0.5, 12, 8, 8)
    glPopMatrix()
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
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.25)  
    glTranslatef(0, 0, 6)
    glScalef(7.0, 2.0, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.18, 0.18, 0.22)
    glTranslatef(30, 0, 6)
    glRotatef(90, 0, 0, 1)
    glScalef(1.0, 1.5, 0.8)
    glutSolidCube(10)
    glPopMatrix()
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
    glPushMatrix()
    glColor3f(0.9, 0.9, 0.95)
    glTranslatef(-28, 0, 16)
    glScalef(2.0, 1.5, 1.2)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.8, 0.8, 0.8)
    glTranslatef(-30, 0, 22)
    gluCylinder(quad, 0.8, 0.8, 25, 8, 8)
    glPopMatrix()
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
    glPushMatrix()
    glColor3f(0.3, 0.0, 0.0)
    glScalef(4.0, 0.8, 0.3)
    glutSolidCube(10)
    glPopMatrix()
    glPushMatrix()
    offset_x = 20.5 * (1 - ratio)
    glTranslatef(offset_x, 0, 0.5)
    if ratio > 0.6:
        glColor3f(0.0, 1.0, 0.0)
    elif ratio > 0.3:
        glColor3f(1.0, 1.0, 0.0)
    else:
        glColor3f(1.0, 0.0, 0.0)
    glScalef(4.1 * ratio, 0.9, 0.4)
    glutSolidCube(10)
    glPopMatrix()
    glPopMatrix()

def draw_drone():
    if not drone_active:
        return
    
    glPushMatrix()
    glTranslatef(drone_x, drone_y, drone_z)
    
    if drone_spawning:
        glColor3f(1, 0.5, 0)  # Orange - flying to enemy
    elif drone_arrived:
        glColor3f(0.3, 0.5, 0.8)  # Blue - attacking enemy
    else:
        glColor3f(0.5, 0.5, 0.5)
    
    glutSolidCube(4)
    
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glTranslatef(0, 6, 0)
    glScalef(4, 0.2, 1)
    glutSolidCube(3)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, -6, 0)
    glScalef(4, 0.2, 1)
    glutSolidCube(3)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-6, 0, 0)
    glScalef(1, 4, 0.2)
    glutSolidCube(3)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(6, 0, 0)
    glScalef(1, 4, 0.2)
    glutSolidCube(3)
    glPopMatrix()
    
    if int(time.time() * 4) % 2 == 0:
        if drone_spawning:
            glColor3f(1, 0.5, 0)
        else:
            glColor3f(0, 1, 0)
    else:
        glColor3f(1, 1, 1)
    glutSolidSphere(1.2, 8, 8)
    
    if drone_spawning and drone_target_ship:
        glColor3f(1, 0.5, 0)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        tx = drone_target_x - drone_x
        ty = drone_target_y - drone_y
        glVertex3f(tx, ty, -20)
        glEnd()
    
    glPopMatrix()
    
    if drone_spawning and drone_active and drone_target_ship:
        dist = math.sqrt((drone_x - drone_target_x)**2 + (drone_y - drone_target_y)**2)
        eta = int(dist / 5)
        draw_text(int(50 + (drone_x / 20)), int(400 + (drone_y / 20)), f"🚁 ATTACKING! {eta}s", GLUT_BITMAP_HELVETICA_12)
    elif drone_arrived and drone_active:
        draw_text(int(50 + (drone_x / 20)), int(400 + (drone_y / 20)), "🚁 ENGAGING ENEMY", GLUT_BITMAP_HELVETICA_12)

def draw_mines():
    for mine in mines:
        glPushMatrix()
        glTranslatef(mine[0], mine[1], 5)
        glColor3f(0.1, 0.1, 0.1)
        glutSolidSphere(4, 10, 10)
        glColor3f(0.8, 0.2, 0.2)
        for angle in range(0, 360, 60):
            rad_a = math.radians(angle)
            glPushMatrix()
            glTranslatef(math.cos(rad_a) * 6, math.sin(rad_a) * 6, 0)
            glutSolidCone(1, 2, 4, 4)
            glPopMatrix()
        brightness = (math.sin(time.time() * 5) + 1) / 2
        glColor3f(1, brightness, 0)
        glutSolidSphere(1.5, 6, 6)
        glPopMatrix()

def draw_explosion(x, y):
    glPushMatrix()
    glTranslatef(x, y, 10)
    glColor3f(1, 0.5, 0)
    glutSolidSphere(6, 8, 8)
    glColor3f(1, 0, 0)
    glutSolidSphere(4, 8, 8)
    glColor3f(1, 1, 0)
    glutSolidSphere(2, 8, 8)
    glPopMatrix()

def draw_projectiles():
    global projectiles
    quad = gluNewQuadric()
    new_projectiles = []
    
    for p in projectiles:
        glPushMatrix()
        glTranslatef(p[0], p[1], 20)
        glScalef(3, 3, 3)
        
        if p[4] == 1:
            glColor3f(1, 1, 0)
            glutSolidCube(3)
            new_projectiles.append(p)
        elif p[4] == 2:
            angle = math.degrees(math.atan2(p[3], p[2]))
            glRotatef(angle, 0, 0, 1)
            glRotatef(90, 0, 1, 0)
            glColor3f(0.5, 0.5, 0.5)
            gluCylinder(quad, 1.5, 1.5, 10, 8, 8)
            glTranslatef(0, 0, 10)
            glColor3f(1, 0.3, 0)
            gluSphere(quad, 2, 8, 8)
            new_projectiles.append(p)
        elif p[4] == 3:
            glColor3f(0, 1, 1)
            glLineWidth(3)
            glBegin(GL_LINES)
            glVertex3f(0, 0, 0)
            glVertex3f(0, 30, 0)
            glEnd()
            new_projectiles.append(p)
        elif p[4] == 4:
            draw_explosion(p[0], p[1])
            if len(p) <= 6:
                p.append(0)
            p[6] += 1
            if p[6] <= 8:
                new_projectiles.append(p)
        elif p[4] == 5:
            glColor3f(1, 0.5, 0)
            glPointSize(3)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            if len(p) <= 6:
                p.append(0)
            p[6] += 1
            if p[6] < 5:
                new_projectiles.append(p)
        glPopMatrix()
    
    projectiles = new_projectiles

def draw_player_dashboard():
    if gear == 0:
        gear_label = "REVERSE"
    elif gear == 1:
        gear_label = "STOP"
    elif gear == 2:
        gear_label = "1/2"
    elif gear == 3:
        gear_label = "FULL"
    
    draw_text(50, 40, f"GEAR: {gear_label}")
    draw_text(30, WINDOW_HEIGHT - 40, f"SCORE: {score}")
    draw_text(WINDOW_WIDTH - 300, WINDOW_HEIGHT - 40, f"PENALTIES: {penalties}/{max_penalties}")
    health_bar = "|" * int(player_health)
    draw_text(WINDOW_WIDTH//2 - 200, 25, health_bar)
    draw_text(WINDOW_WIDTH//2 - 65, 50, f"HULL: {int(player_health)}%")
    
    if current_weapon == 1:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: MG")
    elif current_weapon == 2:
        draw_text(WINDOW_WIDTH - 400, 40, f"WEAPON: RPG - {rpg_ammo}")
    
    draw_text(WINDOW_WIDTH - 400, 15, f"DAMAGE: {int(total_damage)}")
    
    if drone_active:
        if drone_spawning:
            draw_text(50, 80, "🚁 DRONE: FLYING TO ENEMY SHIP! (Orange)", GLUT_BITMAP_HELVETICA_12)
        elif drone_arrived:
            draw_text(50, 80, "🚁 DRONE: ENGAGING ENEMY! (Blue) Press P to recall", GLUT_BITMAP_HELVETICA_12)
    else:
        draw_text(50, 80, "🚁 DRONE: Press O to send drone from LAND to attack ENEMY ships", GLUT_BITMAP_HELVETICA_12)
    
    if mine_cooldown > 0:
        draw_text(50, 110, f"💣 MINE READY IN: {mine_cooldown//60 + 1}s", GLUT_BITMAP_HELVETICA_12)
    else:
        draw_text(50, 110, f"💣 MINE READY! Press M to drop homing mine ({len(mines)}/{max_mines})", GLUT_BITMAP_HELVETICA_12)


# ==================== LEARNER MODE ====================

def start_learner_mode():
    global learner_mode, learner_step, learner_waiting, learner_step_complete
    global player_health, rpg_ammo, score, penalties, game_over, total_damage
    global ships, projectiles, practice_ship, player_pos_x, player_pos_y
    global player_hull_angle, player_turret_angle, gear, drone_active, mines
    global drone_spawning, drone_arrived
    
    learner_mode = True
    learner_step = 1
    learner_waiting = True
    learner_step_complete = False
    game_over = False
    drone_active = False
    drone_spawning = False
    drone_arrived = False
    mines = []
    
    player_health = 100
    rpg_ammo = 10
    score = 0
    penalties = 0
    total_damage = 0
    gear = 1
    player_pos_x = 0
    player_pos_y = 0
    player_hull_angle = 0
    player_turret_angle = 0
    
    ships = []
    projectiles = []
    practice_ship = None
    
    learner_message = "STEP 1: Press W to go FASTER, S to SLOWER"
    print("\n" + "="*60)
    print("🎓 LEARNER MODE STARTED 🎓")
    print("="*60)

def next_learner_step():
    global learner_step, learner_waiting, learner_step_complete
    global ships, practice_ship, learner_message, player_health
    global player_pos_x, player_pos_y, player_hull_angle, player_turret_angle, gear
    global current_weapon, mines
    
    learner_step += 1
    learner_waiting = True
    learner_step_complete = False
    ships = []
    
    player_health = 100
    player_pos_x = 0
    player_pos_y = 0
    player_hull_angle = 0
    player_turret_angle = 0
    gear = 1
    current_weapon = 1
    
    if learner_step == 1:
        learner_message = "STEP 1: Press W to go FASTER, S to SLOWER"
    elif learner_step == 2:
        learner_message = "STEP 2: Press A/D to TURN the ship"
    elif learner_step == 3:
        learner_message = "STEP 3: Press ←/→ to AIM the turret"
    elif learner_step == 4:
        learner_message = "STEP 4: Press 1 for MG, 2 for RPG"
    elif learner_step == 5:
        learner_message = "STEP 5: Click LEFT MOUSE to FIRE!"
        practice_ship = [500, 0, 0, True, 100, 100]
        ships.append(practice_ship)
    elif learner_step == 6:
        learner_message = "STEP 6: RED ships = +100 points. GREEN ships = PENALTY"
        ships.append([600, -80, 0, True, 100, 100])
        ships.append([600, 80, 0, False, 70, 70])
    elif learner_step == 7:
        learner_message = "STEP 7: Chase escaping RED ships!"
        ships.append([800, 0, 0.04, True, 100, 100])
    elif learner_step == 8:
        learner_message = "STEP 8: Every 1000 points = BONUS!"
    elif learner_step == 9:
        learner_message = "STEP 9: Avoid crashing! (-10 health)"
        ships.append([300, 0, 0, True, 100, 100])
    elif learner_step == 10:
        learner_message = "STEP 10: 5 penalties = GAME OVER"
    elif learner_step == 11:
        learner_message = "STEP 11: 🚁 DRONE - Press O to send drone from LAND to attack ENEMY ships!"
        print("\n🚁 Drone flies from land to attack enemy ships directly!")
    elif learner_step == 12:
        learner_message = "STEP 12: Watch drone fly to enemy and destroy it!"
        ships.append([500, 0, 0.02, True, 100, 100])
    elif learner_step == 13:
        learner_message = "STEP 13: 💣 HOMING MINES - Press M to drop!"
        ships.append([600, 0, 0.03, True, 100, 100])
    elif learner_step == 14:
        learner_message = "STEP 14: Drop a mine and watch it chase the enemy!"
        ships.append([700, -50, 0.04, True, 100, 100])
        ships.append([700, 50, 0.04, True, 100, 100])
    elif learner_step == 15:
        learner_message = "🎉 TRAINING COMPLETE! Press R to play!"
        learner_waiting = False
    
    print(learner_message)

def check_learner_step():
    global learner_waiting, learner_step_complete, learner_step
    global gear, player_hull_angle, player_turret_angle, current_weapon
    global total_damage, score, penalties, player_health, ships
    global drone_active, drone_arrived, mines
    
    if not learner_mode or learner_waiting:
        return
    
    if learner_step == 1 and gear != 1:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 2 and player_hull_angle != 0:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 3 and player_turret_angle != 0:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 4 and current_weapon == 2:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 5 and total_damage > 0:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 6 and score >= 100:
        learner_step_complete = True
        learner_waiting = True
        print("✓ Perfect! Press SPACE")
    elif learner_step == 7 and (not ships or score > 0):
        learner_step_complete = True
        learner_waiting = True
        print("✓ Good! Press SPACE")
    elif learner_step == 8 or learner_step == 10:
        learner_step_complete = True
        learner_waiting = True
    elif learner_step == 9 and (player_health < 100 or not ships):
        learner_step_complete = True
        learner_waiting = True
    elif learner_step == 11:
        learner_step_complete = True
        learner_waiting = True
        print("\n✅ Press O to send drone from land to attack enemies!")
        print("Press SPACE to continue")
    elif learner_step == 12:
        if drone_arrived or total_damage > 0:
            learner_step_complete = True
            learner_waiting = True
            print("✓ Great! Drone destroyed the enemy!")
            print("Press SPACE to continue")
        else:
            print("→ Press O to send drone from land to attack the red ship!")
    elif learner_step == 13:
        learner_step_complete = True
        learner_waiting = True
        print("\n✅ Press M to drop homing mines!")
        print("Press SPACE to continue")
    elif learner_step == 14:
        if len(mines) > 0 or total_damage > score:
            learner_step_complete = True
            learner_waiting = True
            print("✓ Amazing!")
            print("Press SPACE to complete training")
        else:
            print("→ Press M to drop a homing mine!")
    elif learner_step == 15:
        pass

def draw_learner_instructions():
    if not learner_mode:
        return
    
    glColor4f(0, 0, 0, 0.8)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glVertex2f(100, WINDOW_HEIGHT - 200)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 50)
    glVertex2f(100, WINDOW_HEIGHT - 50)
    glEnd()
    glDisable(GL_BLEND)
    
    glColor3f(1, 1, 0)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(100, WINDOW_HEIGHT - 200)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 200)
    glVertex2f(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 50)
    glVertex2f(100, WINDOW_HEIGHT - 50)
    glEnd()
    
    draw_text(120, WINDOW_HEIGHT - 130, learner_message, GLUT_BITMAP_HELVETICA_18)
    draw_text(120, WINDOW_HEIGHT - 100, "Press SPACE to continue", GLUT_BITMAP_HELVETICA_12)
    step_text = f"Step {learner_step}/15"
    draw_text(WINDOW_WIDTH - 200, WINDOW_HEIGHT - 100, step_text, GLUT_BITMAP_HELVETICA_12)


# ==================== ACTIONS ====================

def fire_weapon():
    global current_weapon, rpg_ammo, firing_cooldown
    if firing_cooldown > 0:
        return
    if current_weapon == 2 and rpg_ammo <= 0:
        print("No RPG Ammo!")
        return
    
    rad = math.radians(player_turret_angle - 90)
    direction_x = math.cos(rad)
    direction_y = math.sin(rad)
    
    if current_weapon == 1:
        speed = 2.5
        damage = 10
        firing_cooldown = 8
    elif current_weapon == 2:
        speed = 0.6
        damage = 50
        firing_cooldown = 900
        rpg_ammo -= 1
    
    dx = direction_x * speed
    dy = direction_y * speed
    start_x = player_pos_x + (direction_x * 50)
    start_y = player_pos_y + (direction_y * 50)
    projectiles.append([start_x, start_y, dx, dy, current_weapon, damage])


# ==================== DRONE FUNCTIONS ====================

def activate_drone():
    global drone_active, drone_spawning, drone_x, drone_y
    global drone_target_ship, drone_target_x, drone_target_y, drone_arrived
    
    if not drone_active and not learner_mode:
        # Find the nearest RED enemy ship to attack
        target_ship = None
        if ships:
            nearest_dist = 999999
            for s in ships:
                if s[3] == True:  # RED ship only
                    dist = math.sqrt((s[0] - player_pos_x)**2 + (s[1] - player_pos_y)**2)
                    if dist < nearest_dist:
                        nearest_dist = dist
                        target_ship = s
        
        if target_ship:
            drone_active = True
            drone_spawning = True
            drone_arrived = False
            drone_target_ship = target_ship
            drone_target_x = target_ship[0]
            drone_target_y = target_ship[1]
            
            # Spawn from random land area
            if random.choice([True, False]):
                drone_x = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
                drone_y = GRID_LENGTH + 50
            else:
                drone_x = random.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
                drone_y = -GRID_LENGTH - 50
            
            print("\n" + "="*50)
            print("🚁 DRONE DEPLOYED! 🚁")
            print("="*50)
            print("→ Drone flying from LAND to attack ENEMY ship!")
            print("→ ONE SHOT = 100 damage kills RED ships!")
            print("="*50 + "\n")
        else:
            print("No RED enemy ships to attack! Spawn some enemies first.")
    elif learner_mode and learner_step < 11:
        print("Drone will be available after completing basic training!")
    elif drone_active:
        print("Drone already active! Press P to recall.")

def deactivate_drone():
    global drone_active, drone_spawning, drone_arrived, drone_target_ship
    
    if drone_active:
        drone_active = False
        drone_spawning = False
        drone_arrived = False
        drone_target_ship = None
        print("\n🚁 Drone recalled to base!\n")


# ==================== MINES FUNCTIONS ====================

def drop_mine():
    global mine_cooldown, mines, max_mines
    
    if mine_cooldown > 0:
        print(f"⏳ Mine ready in {mine_cooldown//60 + 1} seconds")
        return
    
    if len(mines) >= max_mines:
        mines.pop(0)
        print("💣 Oldest mine removed")
    
    target = None
    if ships:
        nearest_dist = 999999
        for s in ships:
            dist = math.sqrt((s[0] - player_pos_x)**2 + (s[1] - player_pos_y)**2)
            if dist < nearest_dist:
                nearest_dist = dist
                target = s
    
    if target:
        mines.append([player_pos_x, player_pos_y, target[0], target[1], 0])
        print(f"💣 HOMING MINE DROPPED! Chasing enemy (100 damage!)")
    else:
        mines.append([player_pos_x, player_pos_y, None, None, 0])
        print("💣 MINE DROPPED!")
    
    mine_cooldown = mine_cooldown_max

def update_mines():
    global mines, score, penalties, total_damage, rpg_ammo, player_health, game_over, ships
    
    for mine in mines[:]:
        mine_x, mine_y, target_x, target_y, timer = mine
        
        target_ship = None
        if target_x is not None:
            for s in ships:
                if abs(s[0] - target_x) < 10 and abs(s[1] - target_y) < 10:
                    target_ship = s
                    break
        
        if target_ship:
            dx = target_ship[0] - mine_x
            dy = target_ship[1] - mine_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                mine[0] += (dx / dist) * 3
                mine[1] += (dy / dist) * 3
        else:
            rad = math.radians(player_hull_angle - 90)
            mine[0] += math.cos(rad) * 1.5
            mine[1] += math.sin(rad) * 1.5
        
        mine[4] += 1
        
        if mine[4] > 900:
            mines.remove(mine)
            continue
        
        for s in ships[:]:
            if (s[0] - 140 < mine[0] < s[0] + 140) and (s[1] - 40 < mine[1] < s[1] + 40):
                old_health = s[4]
                s[4] -= mine_damage
                total_damage += mine_damage
                
                print(f"💥💣 MINE EXPLOSION! -{mine_damage} damage!")
                print(f"   Ship health: {old_health} → {s[4]}")
                
                projectiles.append([mine[0], mine[1], 0, 0, 4, 0])
                
                if s[4] <= 0:
                    if s[3]:
                        score += 100
                        print(f"✅ MINE destroyed RED ship! +100 points! Score: {score}")
                        if score % 1000 == 0 and score > 0:
                            rpg_ammo += 5
                            penalties = max(0, penalties - 1)
                            player_health = min(100, player_health + 10)
                            print(f"🎁 BONUS! +5 RPG, +10 HP, -1 penalty")
                    else:
                        penalties += 1
                        print(f"⚠️ MINE destroyed GREEN ship! Penalty: {penalties}")
                    ships.remove(s)
                
                mines.remove(mine)
                break


# ==================== KEYBOARD LISTENER ====================

def keyboardListener(key, x, y):
    global player_hull_angle, player_turret_angle, current_weapon
    global game_over, score, penalties, player_health, total_damage, rpg_ammo
    global gear, player_pos_x, player_pos_y, drone_active, mine_cooldown
    global learner_mode, learner_waiting, learner_step, mines, projectiles, ships
    global drone_spawning, drone_arrived
    
    turn_speed = 3
    
    if key == b"l" or key == b"L":
        if not learner_mode:
            start_learner_mode()
            return
        else:
            print("Already in learner mode! Press R to exit.")
            return
    
    if key == b" " and learner_mode:
        if learner_waiting:
            next_learner_step()
        return
    
    if key == b"o" or key == b"O":
        activate_drone()
        return
    
    if key == b"p" or key == b"P":
        deactivate_drone()
        return
    
    if key == b"m" or key == b"M":
        drop_mine()
        return
    
    if key == b"w":
        gear = min(3, gear + 1)
    if key == b's':
        gear = max(0, gear - 1)
    if key == b'a':
        player_hull_angle += turn_speed
    if key == b'd':
        player_hull_angle -= turn_speed
    
    if key == b"r":
        if learner_mode:
            learner_mode = False
            print("\nExited Learner Mode. Starting NORMAL mode!\n")
        
        drone_active = False
        drone_spawning = False
        drone_arrived = False
        mines = []
        
        player_health = 100
        gear = 1
        player_pos_x = 0
        player_pos_y = 0
        game_over = False
        score = 0
        penalties = 0
        total_damage = 0
        rpg_ammo = 10
        player_turret_angle = 0
        player_hull_angle = 0
        
        projectiles = []
        ships = []
        
        if learner_mode:
            learner_step = 1
            learner_waiting = True
    
    if key == b"1":
        current_weapon = 1
    if key == b"2":
        current_weapon = 2


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
        fire_weapon()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_mode = 1 - camera_mode


def is_in_strait(x, y):
    if y < -1000 or y > -600:
        return False
    limit_y = -600 - (400/700) * abs(x)
    return y < limit_y


# ==================== IDLE LOOP ====================

def idle():
    global ship_spawn_timer, ships
    global firing_cooldown, projectiles
    global score, penalties, game_over
    global rpg_ammo, total_damage
    global speeds, gear, player_pos_x, player_pos_y, player_hull_angle
    global player_health
    global drone_active, drone_spawning, drone_arrived, drone_x, drone_y
    global drone_target_ship, drone_target_x, drone_target_y, drone_shoot_cooldown
    global mine_cooldown
    
    if game_over:
        return
    
    dx = math.cos(math.radians(player_hull_angle - 90)) * speeds[gear]
    dy = math.sin(math.radians(player_hull_angle - 90)) * speeds[gear]
    
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
    
    # ==================== DRONE - FLY TO ENEMY SHIP ====================
    if drone_active:
        if drone_spawning and not drone_arrived:
            # Update target position (enemy ship might move)
            if drone_target_ship and drone_target_ship in ships:
                drone_target_x = drone_target_ship[0]
                drone_target_y = drone_target_ship[1]
            else:
                # Target died, find new target or recall
                new_target = None
                for s in ships:
                    if s[3] == True:
                        new_target = s
                        break
                if new_target:
                    drone_target_ship = new_target
                    drone_target_x = new_target[0]
                    drone_target_y = new_target[1]
                    print("🚁 Drone switching to new target!")
                else:
                    deactivate_drone()
                 
            # Fly toward enemy
            dx_drone = drone_target_x - drone_x
            dy_drone = drone_target_y - drone_y
            dist = math.sqrt(dx_drone*dx_drone + dy_drone*dy_drone)
            
            if dist < drone_attack_range:
                drone_arrived = True
                drone_spawning = False
                print("🚁 Drone reached enemy ship! Now attacking!")
                print("   💥 Damage: 100 (ONE SHOT kills RED ships!)")
            else:
                if dist > 0:
                    drone_x += (dx_drone / dist) * 5
                    drone_y += (dy_drone / dist) * 5
                    projectiles.append([drone_x, drone_y, 0, 0, 5, 0])
        
        if drone_arrived:
            # Hover near enemy and shoot
            if drone_target_ship and drone_target_ship in ships:
                drone_x = drone_target_ship[0] - 40
                drone_y = drone_target_ship[1]
                drone_z = 35
                
                if drone_shoot_cooldown > 0:
                    drone_shoot_cooldown -= 1
                else:
                    # Shoot at target
                    shot_dx = drone_target_ship[0] - drone_x
                    shot_dy = drone_target_ship[1] - drone_y
                    shot_dist = math.sqrt(shot_dx*shot_dx + shot_dy*shot_dy)
                    if shot_dist > 0:
                        shot_dx = shot_dx / shot_dist * 6
                        shot_dy = shot_dy / shot_dist * 6
                    
                    projectiles.append([drone_x, drone_y, shot_dx, shot_dy, 3, drone_damage])
                    drone_shoot_cooldown = 12
                    print(f"🚁 DRONE attacking enemy ship! (100 damage)")
            else:
                # Target destroyed, find new enemy or recall
                new_target = None
                for s in ships:
                    if s[3] == True:
                        new_target = s
                        break
                if new_target:
                    drone_target_ship = new_target
                    drone_target_x = new_target[0]
                    drone_target_y = new_target[1]
                    drone_spawning = True
                    drone_arrived = False
                    print("🚁 Drone moving to next enemy!")
                else:
                    print("🚁 No more enemies! Drone returning to base.")
                    deactivate_drone()
    
    # Weapon cooldown
    if firing_cooldown > 0:
        firing_cooldown -= 1
    
    # Mine cooldown
    if mine_cooldown > 0:
        mine_cooldown -= 1
    
    update_mines()
    
    # Enemy spawning
    if not learner_mode or learner_step > 7:
        ship_spawn_timer += 1
        if ship_spawn_timer > ship_spawn_rate and len(ships) < max_ships:
            ship_spawn_timer = 0
            y_pos = random.randint(-GRID_LENGTH + 450, GRID_LENGTH - 100)
            speed_multiplier = 1 + (score / 1000)
            speed = random.uniform(ship_speed_min, ship_speed_max) * speed_multiplier
            red_count = sum(1 for s in ships if s[3])
            is_red = True if red_count < 2 else random.choice([True, False])
            health = 100 if is_red else 70
            ships.append([GRID_LENGTH, y_pos, speed, is_red, health, health])
    
    # Move ships
    for s in ships:
        s[0] -= s[2]
    
    # Handle escaped ships
    escaped_ships = [s for s in ships if s[0] < -GRID_LENGTH]
    for s in escaped_ships:
        if s[3]:
            penalties += 1
            print(f"⚠️ Red ship escaped! Penalty +1 (Total: {penalties})")
    ships = [s for s in ships if s[0] >= -GRID_LENGTH]
    
    # ==================== PROJECTILES ====================
    active_projectiles = []
    
    for p in projectiles:
        if p[4] == 3:
            p[0] += p[2]
            p[1] += p[3]
            
            if not (-GRID_LENGTH - 100 < p[0] < GRID_LENGTH + 100) or \
               not (-GRID_LENGTH - 100 < p[1] < GRID_LENGTH + 100):
                continue
            
            hit_ship = False
            for s in ships[:]:
                if (s[0] - 140 < p[0] < s[0] + 140) and (s[1] - 40 < p[1] < s[1] + 40):
                    old_health = s[4]
                    s[4] -= p[5]
                    total_damage += p[5]
                    hit_ship = True
                    
                    print(f"🔴 DRONE HIT! -{p[5]} damage!")
                    print(f"   Ship health: {old_health} → {s[4]}")
                    
                    if s[4] <= 0:
                        if s[3]:
                            score += 100
                            print(f"✅ DRONE DESTROYED RED SHIP! +100 points! Score: {score}")
                            if score % 1000 == 0 and score > 0:
                                rpg_ammo += 5
                                penalties = max(0, penalties - 1)
                                player_health = min(100, player_health + 10)
                                print(f"🎁 BONUS! +5 RPG, +10 HP, -1 penalty")
                        else:
                            penalties += 1
                            print(f"⚠️ DRONE hit GREEN ship! Penalty: {penalties}")
                        ships.remove(s)
                    break
            
            if not hit_ship:
                active_projectiles.append(p)
            continue
        
        if p[4] == 5:
            if len(p) <= 6:
                p.append(0)
            p[6] += 1
            if p[6] < 5:
                active_projectiles.append(p)
            continue
        
        p[0] += p[2]
        p[1] += p[3]
        
        if p[4] == 4:
            if len(p) <= 6:
                p.append(0)
            p[6] += 1
            if p[6] <= 8:
                active_projectiles.append(p)
            continue
        
        hit_ship = False
        for s in ships[:]:
            if (s[0] - 140 < p[0] < s[0] + 140) and (s[1] - 40 < p[1] < s[1] + 40):
                old_health = s[4]
                s[4] -= p[5]
                total_damage += p[5]
                hit_ship = True
                print(f"💥 HIT! -{p[5]} damage! Health: {old_health} → {s[4]}")
                
                if s[4] <= 0:
                    if s[3]:
                        score += 100
                        print(f"✅ Destroyed RED ship! +100 points! Score: {score}")
                        if score % 1000 == 0 and score > 0:
                            rpg_ammo += 5
                            penalties = max(0, penalties - 1)
                            player_health = min(100, player_health + 10)
                            print(f"🎁 BONUS! +5 RPG, +10 HP, -1 penalty")
                    else:
                        penalties += 1
                        print(f"⚠️ Destroyed GREEN ship! Penalty: {penalties}")
                    ships.remove(s)
                break
        
        if not hit_ship and (-GRID_LENGTH - 100 < p[0] < GRID_LENGTH + 100) and (-GRID_LENGTH - 100 < p[1] < GRID_LENGTH + 100):
            active_projectiles.append(p)
    
    projectiles = active_projectiles
    ships = [s for s in ships if s[4] > 0]
    
    if penalties >= max_penalties:
        game_over = True
        print(f"\n💀 GAME OVER! Final Score: {score} 💀\n")
    
    if learner_mode and not game_over:
        check_learner_step()
    
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    setupCamera()
    
    draw_sea()
    draw_land()
    
    glPushMatrix()
    glTranslatef(player_pos_x, player_pos_y, 0)
    glRotatef(player_hull_angle - 90, 0, 0, 1)
    glScalef(2, 2, 2)
    draw_player()
    glPopMatrix()
    
    draw_drone()
    draw_mines()
    
    for s in ships:
        glPushMatrix()
        glTranslatef(s[0], s[1], 0)
        glScalef(4, 4, 4)
        draw_cargo_ship(s[3], s[4], s[5])
        draw_health_bar(s[4], s[5])
        glPopMatrix()
    
    draw_projectiles()
    draw_player_dashboard()
    
    if learner_mode:
        draw_learner_instructions()
    
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
    
    print("\n" + "="*60)
    print("⚓ BAIT OF TORMUZ - NAVAL DEFENSE ⚓")
    print("="*60)
    print("\n🎮 CONTROLS:")
    print("   W/S     - Change gears")
    print("   A/D     - Turn ship")
    print("   ←/→     - Aim turret")
    print("   1/2     - Switch weapons")
    print("   Mouse L - Fire")
    print("   R.Shift - Fire")
    print("   Mouse R - Camera")
    print("   R       - Restart")
    print("\n🚁 DRONE:")
    print("   Press O  - Send drone from LAND to attack ENEMY ships!")
    print("   💥 ONE SHOT kill on RED ships!")
    print("   Press P  - Recall drone")
    print("\n💣 HOMING MINES:")
    print("   Press M  - Drop mine that CHASES enemies!")
    print("   💥 100 damage - ONE SHOT kill!")
    print("\n🎓 LEARNER MODE:")
    print("   Press L  - Start tutorial")
    print("   SPACE   - Next step")
    print("="*60 + "\n")
    
    glutMainLoop()


if __name__ == "__main__":
    main()