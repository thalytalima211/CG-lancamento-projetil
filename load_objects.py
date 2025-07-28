import OpenGL.GL as gl
import OpenGL.GLUT as glut

import math
import numpy as np

from PIL import Image

def load_texture(path):
    image = Image.open(path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.convert("RGBA").tobytes()

    tex_id = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.width, image.height, 0,
                    gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, img_data)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tex_id

def calculate_normal(v0, v1, v2):
    u = np.subtract(v1, v0)
    v = np.subtract(v2, v0)
    normal = np.cross(u, v)
    norm = np.linalg.norm(normal)
    return normal / norm if norm != 0 else normal

def draw_faces(faces, vertices):
    for face in faces:
        v0, v1, v2 = [vertices[idx - 1] for idx in face[:3]]
        normal = calculate_normal(v0, v1, v2)
        gl.glBegin(gl.GL_POLYGON)
        gl.glNormal3f(*normal)
        for idx in face:
            gl.glVertex3f(*vertices[idx - 1])
        gl.glEnd()

def load_obj(filename):
    vertices, faces = [], []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                parts = line.strip().split()
                vertices.append(tuple(map(float, parts[1:4])))
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(p.split('/')[0]) for p in parts[1:]]
                faces.append(face)
    return vertices, faces

canhao_vertices, canhao_faces = load_obj('./canhao.obj')
cano_vertices, cano_faces = load_obj('./cano.obj')

def draw_cannon():
    gl.glColor3f(0.55, 0.27, 0.07)
    draw_faces(canhao_faces, canhao_vertices)

def draw_cannon_barrel(ang = 0):
    gl.glPushMatrix()
    gl.glTranslatef(11.740875, 15.961926, 0.581896)
    gl.glRotatef(ang, 0, 0, 1)
    gl.glTranslatef(-11.740875, -15.961926, -0.581896)
    gl.glColor3f(0.3, 0.3, 0.3)
    draw_faces(cano_faces, cano_vertices)
    gl.glPopMatrix()

def draw_ground(texture_id):
    gl.glEnable(gl.GL_TEXTURE_2D)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

    gl.glBegin(gl.GL_QUADS)
    gl.glColor3f(1.0, 1.0, 1.0)

    gl.glTexCoord2f(0, 0)
    gl.glVertex3f(-2000, 0, -1000)

    gl.glTexCoord2f(0, 10)
    gl.glVertex3f(-2000, 0, 1000)

    gl.glTexCoord2f(10, 10)
    gl.glVertex3f(2000, 0, 1000)

    gl.glTexCoord2f(10, 0)
    gl.glVertex3f(2000, 0, -1000)

    gl.glEnd()

    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    gl.glDisable(gl.GL_TEXTURE_2D)

def draw_sky():
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)

    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glBegin(gl.GL_QUADS)
    gl.glColor3f(0.5, 0.8, 1.0)
    gl.glVertex3f(-1, 1, -1)
    gl.glVertex3f(1, 1, -1)
    gl.glColor3f(1.0, 1.0, 1.0)
    gl.glVertex3f(1, -1, -1)
    gl.glVertex3f(-1, -1, -1)
    gl.glEnd()
    gl.glPopMatrix()

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_LIGHTING)

def draw_ball(position):
    gl.glPushMatrix()
    gl.glTranslatef(*position)
    glut.glutSolidSphere(3, 20, 20)
    gl.glPopMatrix()

def get_ball_position_before_launch(angle_deg):
    px, py, pz = 11.740875, 15.961926, 0.581896

    distancia_boca = 18.0

    ang_rad = math.radians(angle_deg)

    x = px + distancia_boca * math.cos(ang_rad)
    y = py + distancia_boca * math.sin(ang_rad)
    z = pz

    return [x, y, z]

def draw_shadow(position, angle, force):
    x, y, z = position

    y = max(y, 0.05)

    ball_radius = 3.0
    base_shadow_radius = ball_radius * 1.1

    shadow_radius = base_shadow_radius

    min_alpha = 0.1
    max_alpha = 0.7
    alpha = lerp(max_alpha, min_alpha, min(y / 20.0, 1.0))

    gl.glPushAttrib(gl.GL_CURRENT_BIT | gl.GL_ENABLE_BIT)
    gl.glPushMatrix()

    gl.glDisable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glColor4f(0.0, 0.0, 0.0, alpha)

    gl.glTranslatef(x, 0.02, z)
    gl.glScalef(shadow_radius, 1.0, shadow_radius)

    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex3f(0, 0, 0)
    for angle in range(0, 361, 15):
        rad = math.radians(angle)
        gl.glVertex3f(math.cos(rad), 0, math.sin(rad))
    gl.glEnd()

    gl.glPopMatrix()
    gl.glPopAttrib()

def lerp(start, end, t):
    return start + t * (end - start)

def draw_trajectory_preview(angle, force, get_trajectory_points):
    start_pos = get_ball_position_before_launch(angle)

    points = get_trajectory_points(angle, force, start_pos=np.array(start_pos))

    gl.glDisable(gl.GL_LIGHTING)
    gl.glColor3f(1.0, 0.0, 0.0)
    gl.glLineWidth(2)
    gl.glEnable(gl.GL_LINE_STIPPLE)
    gl.glLineStipple(1, 0x00FF)

    gl.glBegin(gl.GL_LINE_STRIP)
    for p in points:
        gl.glVertex3f(*p)
    gl.glEnd()

    gl.glDisable(gl.GL_LINE_STIPPLE)
    gl.glEnable(gl.GL_LIGHTING)
