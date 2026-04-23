from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

#==================== VARIABLES ==============================

WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 800
GRID_LENGTH = 1000

camera_angle = 90
camera_height = 500
camera_radius = 400
fovY = 120








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

def keyboardListener(key, x, y):
    pass

def specialKeyListener(key, x, y):
    global camera_angle, camera_height

    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5
    if key == GLUT_KEY_DOWN:
        camera_height -= 20
    if key == GLUT_KEY_UP:
        camera_height += 20

def mouseListener(button, state, x, y):
    pass

def idle():
    
    
    glutPostRedisplay()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)

    setupCamera()

    draw_sea()
    draw_land()

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
