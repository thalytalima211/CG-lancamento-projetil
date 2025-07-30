import OpenGL.GL as gl
import OpenGL.GLUT as glut
import math
import time
import pygame

from load_objects import get_ball_position_before_launch

pygame.init()
launch_sound = pygame.mixer.Sound("launch.wav")
impact_sound = pygame.mixer.Sound("impact.wav")

# Estados do projétil e controle
angle = 0                    # ângulo de lançamento (graus)
force = 30                   # força do lançamento
is_launched = False          # está em voo?
proj_pos = [0, 0, 0]         # posição atual do projétil
proj_vel = [0.0, 0.0, 0.0]   # velocidade atual do projétil (vx, vy, vz)
g = 9.81                     # aceleração da gravidade (m/s²)
last_time = None             # timestamp da última atualização
launch_count = 0             # contador de lançamentos
distances = []               # lista para armazenar resultados das jogadas

trajectory_points = []       # pontos do rastro do projétil (para desenhar)
MIN_FORCE_TO_EXIT = 5.5      # força mínima extra para sair do canhão
start_x_position = 0.0       # posição x inicial do lançamento para calcular distância

# Variáveis para controle do impacto e rebote
is_on_ground = False
bounce_count = 0
max_bounces = 5
sound_played_this_bounce = False
raio_bola = 3             


def draw_text(x, y, text, font=glut.GLUT_BITMAP_HELVETICA_18):
    """Desenha texto na posição x,y da janela."""
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glWindowPos2f(x, y)
    for ch in text:
        glut.glutBitmapCharacter(font, ord(ch))
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_DEPTH_TEST)

def draw_rect(x, y, width, height, color=(0, 0, 0, 0.5)):
    """Desenha um retângulo semi-transparente no espaço da janela."""
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)

    gl.glDisable(gl.GL_LINE_SMOOTH)    # Remove suavização
    gl.glDisable(gl.GL_POLYGON_SMOOTH)
    
    gl.glColor4f(*color)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(x, y)
    gl.glVertex2f(x + width, y)
    gl.glVertex2f(x + width, y + height)
    gl.glVertex2f(x, y + height)
    gl.glEnd()
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_DEPTH_TEST)
    
def draw_force_bar():
    max_width = 200  
    height = 10
    filled_width = (force / 100) * max_width

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, glut.glutGet(glut.GLUT_WINDOW_WIDTH), 0, glut.glutGet(glut.GLUT_WINDOW_HEIGHT), -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    win_w = glut.glutGet(glut.GLUT_WINDOW_WIDTH)
    x = (win_w - max_width) // 2
    y = 40  

    # Define cor dinâmica
    if force < 40:
        color = (0.2, 0.4, 1.0, 0.8) 
    elif force < 70:
        color = (1.0, 0.8, 0.0, 0.8) 
    else:
        color = (1.0, 0.2, 0.2, 0.8)  

    # Desenha borda
    draw_rect(x - 2, y - 2, max_width + 4, height + 4, color=(0, 0, 0, 1.0))
    draw_rect(x, y, max_width, height, color=(0.3, 0.3, 0.3, 0.7))
    draw_rect(x, y, filled_width, height, color=color)

    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)

def draw_hud():
    """Desenha o HUD com informações sobre ângulo, força, estado e comandos."""
    global launch_count

    box_x, box_y = 10, 510
    box_w, box_h = 240, 130
    line_height = 20

    draw_rect(box_x, box_y, box_w, box_h, color=(0.1, 0.1, 0.1, 0.6))
    gl.glColor3f(0.0, 0.0, 0.0) 

    start_y = box_y - 25
    draw_text(box_x + 10, start_y, f"🎯 Ângulo: {angle}°")
    draw_text(box_x + 10, start_y - 1*line_height, f"💪 Força: {force}")
    draw_text(box_x + 10, start_y - 2*line_height, f"🚀 Estado: {'Voo' if is_launched else 'Parado'}")
    draw_text(box_x + 10, start_y - 3*line_height, f"🎲 Arremessos: {launch_count}")
    draw_text(box_x + 10, start_y - 4*line_height, " W/S ou ↑/↓: Ângulo")
    draw_text(box_x + 10, start_y - 5*line_height, " A/D ou ←/→: Força")
    draw_text(box_x + 10, start_y - 6*line_height, " Espaço: Lançar")
    
    if distances:
        draw_text(box_x + 10, start_y - 7*line_height, f"🏁 Distância percorrida: {distances[-1]:.2f} m")
    sorted_distances = sorted(enumerate(distances, 1), key=lambda x: x[1], reverse=True)
    
    draw_text(box_x + 10, start_y - 8*line_height, "🏆 Ranking:")
    for i, (jogada, dist) in enumerate(sorted_distances[:3], start=1):  # top 3
        draw_text(box_x + 10, start_y - (8+i)*line_height, f"{i}º Jogada {jogada}: {dist:.2f} m")
    draw_force_bar()

def keyboard(key, x, y):
    """Teclas normais (ASCII)."""
    global angle, force, is_launched, proj_pos, proj_vel, last_time, launch_count, camera_mode, start_x_position

    key = key.decode('utf-8').lower()

    if key == 'w' and not is_launched and angle < 80:
        angle += 1
    elif key == 's' and not is_launched and angle > 0:
        angle -= 1
    elif key == 'd' and not is_launched and force < 100:
        force += 1
    elif key == 'a' and not is_launched and force > 1:
        force -= 1
    elif key == ' ' and not is_launched:
        is_launched = True
        launch_sound.play()

        proj_pos[:] = get_ball_position_before_launch(angle)
        start_x_position = proj_pos[0]

        rad = math.radians(angle)
        initial_force = force + MIN_FORCE_TO_EXIT
        proj_vel[0] = initial_force * math.cos(rad)
        proj_vel[1] = initial_force * math.sin(rad)
        proj_vel[2] = 0.0

        last_time = time.time()
        launch_count += 1
        trajectory_points.clear()

    elif key == '\x1b':  # ESC
        glut.glutLeaveMainLoop()

    glut.glutPostRedisplay()

def special_keyboard(key, x, y):
    """Teclas especiais (setas)."""
    global angle, force, is_launched

    if is_launched:
        return

    if key == glut.GLUT_KEY_UP and angle < 80:
        angle += 1
    elif key == glut.GLUT_KEY_DOWN and angle > 0:
        angle -= 1
    elif key == glut.GLUT_KEY_RIGHT and force < 100:
        force += 1
    elif key == glut.GLUT_KEY_LEFT and force > 1:
        force -= 1

    glut.glutPostRedisplay()

def update_projectile():
    """Atualiza a posição do projétil no tempo, aplicando física simples e colisões."""
    global proj_pos, proj_vel, is_launched, last_time, is_on_ground

    if not is_launched:
        return

    current_time = time.time()
    dt = current_time - last_time if last_time else 0
    last_time = current_time

    next_x = proj_pos[0] + proj_vel[0] * dt
    next_y = proj_pos[1] + proj_vel[1] * dt - 0.5 * g * dt * dt

    if next_y <= raio_bola:
        proj_pos[1] = raio_bola
        proj_pos[0] = next_x

        if not is_on_ground:
            impact_sound.play()
            is_on_ground = True

        coef_restituicao = 0.2
        coef_atrito = 0.8
        velocidade_minima = 0.1

        proj_vel[1] = -proj_vel[1] * coef_restituicao  
        proj_vel[0] *= coef_atrito                     

        if abs(proj_vel[1]) < velocidade_minima and abs(proj_vel[0]) < velocidade_minima:
            proj_vel[0] = 0
            proj_vel[1] = 0
            is_launched = False

            distancia = proj_pos[0] - start_x_position
            distances.append(distancia)
            print(f"🏁 Distância percorrida: {distancia:.2f} metros")

    else:
        proj_pos[0] = next_x
        proj_pos[1] = next_y
        proj_vel[1] -= g * dt
        is_on_ground = False

    trajectory_points.append(tuple(proj_pos))
    glut.glutPostRedisplay()

def calculate_trajectory_points(angle_deg, force, start_pos, steps=50, dt=0.1):
    """Calcula os pontos da trajetória para desenhar o rastro."""
    points = []
    rad = math.radians(angle_deg)
    vx = force * math.cos(rad)
    vy = force * math.sin(rad)

    for i in range(steps):
        t = i * dt
        x = start_pos[0] + vx * t
        y = start_pos[1] + vy * t - 0.5 * g * t * t
        z = start_pos[2]

        if y < 0:
            break
        points.append((x, y, z))
    return points