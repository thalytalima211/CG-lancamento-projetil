import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu

import load_objects as obj

def confCamera():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, 800/512, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    glu.gluLookAt(-25,20,-70, 60,10,-10, 0,1,0)

def display():
    gl.glClearColor(1.0, 1.0, 1.0, 1.0) 
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glShadeModel(gl.GL_SMOOTH)

    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [1.0, 1.0, -1.0, 0.0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.1, 0.1, 0.1, 0.5])  # luz ambiente suave
    gl.glEnable(gl.GL_COLOR_MATERIAL)
    gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)

    obj.draw_sky()
    obj.draw_ground()
    obj.draw_cannon()
    obj.draw_cannon_barrel(0) # ATÉ 80 GRAUS
    obj.draw_ball()

    glut.glutSwapBuffers()


glut.glutInit()
glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
glut.glutCreateWindow(b'Simulador de lancamento de projetil')
glut.glutReshapeWindow(800, 512)
confCamera()
glut.glutDisplayFunc(display)
glut.glutMainLoop()
