import OpenGL.GL as gl
import OpenGL.GLUT as glut
import math
import time

angle = 0
force = 30
is_launched = False
proj_pos = [55.0, 15.0, 0.0]
proj_vel = [0.0, 0.0, 0.0]
g = 9.81
last_time = None
launch_count = 0  # contador de arremessos

def draw_text(x, y, text, font=glut.GLUT_BITMAP_HELVETICA_18):
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glWindowPos2f(x, y)
    for ch in text:
        glut.glutBitmapCharacter(font, ord(ch))
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_DEPTH_TEST)

def draw_rect(x, y, width, height, color=(0, 0, 0, 0.5)):
    """Desenha um retângulo semi-transparente no espaço da janela"""
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + width, y)
    gl.glVertex2f(x + width, y - height)
    gl.glVertex2f(x, y - height)
    gl.glEnd()
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_DEPTH_TEST)

def draw_hud():
    global launch_count

    box_x, box_y = 10, 510
    box_w, box_h = 240, 130

    # Fundo translúcido para o HUD
    draw_rect(box_x, box_y, box_w, box_h, color=(0.1, 0.1, 0.1, 0.6))

    gl.glColor3f(1, 1, 1)
    line_height = 20
    start_y = box_y - 25

    draw_text(box_x + 10, start_y, f"🎯 Ângulo: {angle}°")
    draw_text(box_x + 10, start_y - 1*line_height, f"💪 Força: {force}")
    draw_text(box_x + 10, start_y - 2*line_height, f"🚀 Estado: {'Voo' if is_launched else 'Parado'}")
    draw_text(box_x + 10, start_y - 3*line_height, f"🎲 Arremessos: {launch_count}")
    draw_text(box_x + 10, start_y - 4*line_height, "W/S ou ↑/↓: Ângulo")
    draw_text(box_x + 10, start_y - 5*line_height, "A/D ou ←/→: Força")
    draw_text(box_x + 10, start_y - 6*line_height, "Espaço: Lançar")

def keyboard(key, x, y):
    global angle, force, is_launched, proj_pos, proj_vel, last_time, launch_count
    key = key.decode('utf-8').lower()

    if key == 'w':
        if not is_launched and angle < 80:
            angle += 1
    elif key == 's':
        if not is_launched and angle > 0:
            angle -= 1
    elif key == 'd':
        if not is_launched and force < 100:
            force += 1
    elif key == 'a':
        if not is_launched and force > 1:
            force -= 1
    elif key == ' ' and not is_launched:
        is_launched = True
        proj_pos[:] = [55.0, 15.0, 0.0]
        rad = math.radians(angle)
        proj_vel[0] = force * math.cos(rad)
        proj_vel[1] = force * math.sin(rad)
        proj_vel[2] = 0.0
        last_time = time.time()
        launch_count += 1
    elif key == '\x1b':  # ESC
        glut.glutLeaveMainLoop()

    glut.glutPostRedisplay()

def special_keyboard(key, x, y):
    global angle, force, is_launched
    if is_launched:
        return

    if key == glut.GLUT_KEY_UP:
        if angle < 80:
            angle += 1
    elif key == glut.GLUT_KEY_DOWN:
        if angle > 0:
            angle -= 1
    elif key == glut.GLUT_KEY_RIGHT:
        if force < 100:
            force += 1
    elif key == glut.GLUT_KEY_LEFT:
        if force > 1:
            force -= 1

    glut.glutPostRedisplay()

def update_projectile():
    global proj_pos, proj_vel, is_launched, last_time

    if not is_launched:
        return

    current_time = time.time()
    dt = current_time - last_time if last_time else 0
    last_time = current_time

    proj_pos[0] += proj_vel[0] * dt
    proj_pos[1] += proj_vel[1] * dt - 0.5 * g * dt * dt
    proj_vel[1] -= g * dt

    if proj_pos[1] <= 0:
        proj_pos[1] = 0
        is_launched = False

    glut.glutPostRedisplay()
