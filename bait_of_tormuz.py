from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

#==================== VARIABLES ==============================

# system
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
GRID_LENGTH = 1000

# Camera 
camera_angle = 90
camera_height = 500
camera_radius = 400
fovY = 120

# player
player_pos_x = 0
player_pos_y = 0
player_hull_angle = 0
player_turret_angle = 0

# ships
ships = []
max_ships = 5
ship_spawn_timer = 0
ship_spawn_rate = 60
ship_speed_min = 0.01
ship_speed_max = 0.03

# weapons

projectiles = []
current_weapon = 1
rpg_ammo = 10
firing_cooldown = 0






#===================== FUNCTIONS ==============================
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
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

    glVertex3f(0, -300, 10)
    glVertex3f(-700, -GRID_LENGTH, 20)
    glVertex3f(0, -GRID_LENGTH, 20)
    glVertex3f(700, -GRID_LENGTH, 20)
    glEnd()

def draw_player():
    quad = gluNewQuadric()
    # 1. Boat Hull (rotates with hull angle)
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
    # 3. Cabin Base (FIXED - rotates with turret)
    glPushMatrix()
    # Rotate turret independently from hull
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.25, 0.3, 0.25)  
    glTranslatef(-5, 0, 18)
    glScalef(2.0, 1.2, 1.2)
    glutSolidCube(10)
    glPopMatrix()
    # 4. Turret Head (FIXED - rotates with turret)  
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.2, 0.25, 0.2)
    glTranslatef(-5, 0, 25)
    glScalef(1.2, 0.8, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    # 5. Gun Barrel (FIXED - rotates with turret)
    glPushMatrix()
    glRotatef(player_turret_angle - player_hull_angle, 0, 0, 1)
    
    glColor3f(0.1, 0.1, 0.1)
    glTranslatef(5, 0, 23)
    glRotatef(90, 0, 1, 0)
    gluCylinder(quad, 1.2, 1.2, 20, 12, 12)
    glPopMatrix()
    
    # 6. Radar/Antenna (stays with cabin)
    glPushMatrix()
    glColor3f(0.15, 0.15, 0.15)
    glTranslatef(-8, 0, 28)
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
    glColor3f(0.2, 0.2, 0.25)  # Dark blue-grey
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
    glColor3f(0.85, 0.5, 0.15)  # Orange
    glTranslatef(-5, 0, 12)  # FIXED: Y=0, not Y=18
    glScalef(3.5, 1.8, 1.0)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.15, 0.4, 0.7)  # Blue
    glTranslatef(8, 0, 12)  # FIXED: Y=0
    glScalef(2.5, 1.8, 1.0)
    glutSolidCube(10)
    glPopMatrix()
    
    # Top row
    glPushMatrix()
    glColor3f(0.85, 0.5, 0.15)  # Orange
    glTranslatef(-5, 0, 22)  # FIXED: Y=0
    glScalef(2.5, 1.5, 0.8)
    glutSolidCube(10)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.15, 0.4, 0.7)  # Blue
    glTranslatef(8, 0, 22)  # FIXED: Y=0
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
    
    # Flag (RED for enemy, GREEN for ally)
    glPushMatrix()
    if is_red_flag:
        glColor3f(1.0, 0.0, 0.0)  # Red - ENEMY
    else:
        glColor3f(0.0, 1.0, 0.0)  # Green - ALLY
    glTranslatef(-30, 0, 40)
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(-15, 0, 0)
    glVertex3f(-15, 0, 10)
    glVertex3f(0, 0, 10)
    glEnd()
    glPopMatrix()

def draw_health_bar(x, y, health, max_health):
    ratio = health / max_health
    
    glPushMatrix()
    glTranslatef(x, y, 55)
    
    # Background (red - damage)
    glColor3f(0.3, 0.0, 0.0)
    glScalef(4.0, 0.8, 0.3)
    glutSolidCube(10)
    
    # Foreground (green to red based on health)
    glTranslatef(0, 0, 0.5)
    if ratio > 0.6:
        glColor3f(0.0, 1.0, 0.0)  # Green
    elif ratio > 0.3:
        glColor3f(1.0, 1.0, 0.0)  # Yellow
    else:
        glColor3f(1.0, 0.0, 0.0)  # Red
    
    glScalef(ratio, 1.0, 1.0)
    glutSolidCube(10)
    glPopMatrix()


def keyboardListener(key, x, y):
    global player_pos_x, player_pos_y, player_hull_angle, player_turret_angle

    speed = 12
    turn_speed = 3

    dx = math.cos(math.radians(player_hull_angle - 90)) * speed
    dy = math.sin(math.radians(player_hull_angle - 90)) * speed

    if key == b"w":
        if -GRID_LENGTH < player_pos_x + dx < GRID_LENGTH:
            player_pos_x += dx
        if -GRID_LENGTH < player_pos_y + dy < GRID_LENGTH:
            player_pos_y += dy
    
    if key == b's':
        if -GRID_LENGTH < player_pos_x - dx < GRID_LENGTH:
            player_pos_x -= dx
        if -GRID_LENGTH < player_pos_y - dy < GRID_LENGTH:
            player_pos_y -= dy

    if key == b'a':
        player_hull_angle += turn_speed
    
    if key == b'd':
        player_hull_angle -= turn_speed

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

def mouseListener(button, state, x, y):
    pass

def idle():
    global ship_spawn_timer, ships
    
    ship_spawn_timer += 1
    if ship_spawn_timer > ship_spawn_rate and len(ships) < max_ships:
        ship_spawn_timer = 0
        
        # Spawn at right edge
        y_pos = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        speed = random.uniform(ship_speed_min, ship_speed_max)
        
        # Random: red (enemy) or green (ally)
        is_red = random.choice([True, False])
        health = 50 if is_red else 30
        
        # Ship data: [x, y, speed, is_red, health, max_health]
        ships.append([GRID_LENGTH, y_pos, speed, is_red, health, health])
    
    # 2. Move ships left
    for s in ships:
        s[0] -= s[2]  # Move left by speed
    
    # 3. Remove ships that went off-screen
    ships = [s for s in ships if s[0] > -GRID_LENGTH - 100]
    
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

    for s in ships:
        glPushMatrix()
        glTranslatef(s[0], s[1], 0)
        glScalef(4, 4, 4)
        draw_cargo_ship(s[3], s[4], s[5])
        glPopMatrix()
        draw_health_bar(s[0], s[1], s[4], s[5])

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
