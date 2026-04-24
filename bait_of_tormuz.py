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
camera_mode = 1

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

# Gameplay
score = 0
penalties = 0
max_penalties = 3
game_over = False




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

    glVertex3f(0, -300, 10)
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
        glPopMatrix()





# actions

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
        speed = 2
        damage = 10
        firing_cooldown = 8
    elif current_weapon == 2:
        speed = 0.5
        damage = 50
        firing_cooldown = 900
        rpg_ammo -= 1
    
    dx = (direction_x * speed)
    dy = (direction_y * speed)

    start_x = player_pos_x + (direction_x * 50)
    start_y = player_pos_y + (direction_y * 50)

    projectiles.append([start_x, start_y, dx, dy, current_weapon, damage])


def keyboardListener(key, x, y):
    global player_pos_x, player_pos_y, player_hull_angle, player_turret_angle
    global current_weapon, game_over, score, penalties
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

    if key == b"r":
        game_over = False
        score = 0
        penalties = 0
        projectiles.clear()
        ships.clear()
    
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

def idle():
    global ship_spawn_timer, ships
    global firing_cooldown, projectiles
    global score, penalties, game_over

    if game_over:
        return

    if firing_cooldown > 0:
        firing_cooldown -= 1
    
    ship_spawn_timer += 1
    if ship_spawn_timer > ship_spawn_rate and len(ships) < max_ships:
        ship_spawn_timer = 0
        
        y_pos = random.randint(-GRID_LENGTH + 100, GRID_LENGTH - 100)
        speed = random.uniform(ship_speed_min, ship_speed_max)
        
        is_red = random.choice([True, False])
        health = 50 if is_red else 30
        
        # Ship data: [x, y, speed, is_red, health, max_health]
        ships.append([GRID_LENGTH, y_pos, speed, is_red, health, health])
    
    
    for s in ships:
        s[0] -= s[2]  
    
    escaped_ships = [s for s in ships if s[0] < -GRID_LENGTH]
    for s in escaped_ships:
        if s[3]:
            penalties += 1
            print(f"Red ship escaped! Penalty {penalties}")
    
    ships = [s for s in ships if s[0] > -GRID_LENGTH - 100]

    # Move projectiles
    active_projectiles = []

    for p in projectiles:
        p[0] += p[2]
        p[1] += p[3]

        hit_ship = False
        for s in ships:
            dist = math.sqrt((p[0] - s[0])**2 + (p[1] - s[1])**2)

            if dist < 40:
                s[4] -= p[5]
                hit_ship = True 
                print(f"Hit! Damage: {p[5]}")

                if s[4] <= 0:
                    if s[3]:
                        score += 100
                        print(f"Red ship destroyed! Score: {score}")
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
        glPopMatrix()
        draw_health_bar(s[0], s[1], s[4], s[5])
    
    # projectiles
    glPushMatrix()
    draw_projectiles()
    glPopMatrix()



    # Texts
    if current_weapon == 1:
        draw_text(10, WINDOW_HEIGHT - 30, f"Machine Gun [Ammo = Unlimited]")
    elif current_weapon == 2:
        draw_text(10, WINDOW_HEIGHT - 30, f"RPG [Ammo = {rpg_ammo}]")

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
