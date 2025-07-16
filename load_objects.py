import OpenGL.GL as gl
import OpenGL.GLUT as glut

import numpy as np

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

def draw_ground():
    gl.glBegin(gl.GL_QUADS)

    gl.glColor3f(0.0, 0.2, 0.0)
    gl.glVertex3f(-100, 0, -300)

    gl.glColor3f(0.0, 0.2, 0.0)
    gl.glVertex3f(-100, 0, 300)

    gl.glColor3f(0.6, 1.0, 0.6)
    gl.glVertex3f(100, 0, 300)

    gl.glColor3f(0.6, 1.0, 0.6)
    gl.glVertex3f(100, 0, -300)

    gl.glEnd()

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

def draw_ball(): #pode controlar a posição dela depois por meio de parâmetros
    gl.glPushMatrix()
    gl.glTranslatef(55, 15, 0)
    glut.glutSolidSphere(7.5, 20, 20)
    gl.glPopMatrix()

