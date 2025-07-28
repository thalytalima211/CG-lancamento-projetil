import OpenGL.GL as gl
import OpenGL.GLUT as glut
import OpenGL.GLU as glu

import load_objects as obj
import controller

offset_x = -25 - 60
offset_y = 20 - 10
offset_z = -70 - (-10)

texture_grass = None

def confCamera():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, 800/512, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    glu.gluLookAt(-25,20,-70, 60,10,-10, 0,1,0)

def confCameraFollowProjectile():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, 800/512, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    proj_x, proj_y, proj_z = controller.proj_pos

    cam_x = proj_x + offset_x
    cam_y = proj_y + offset_y
    cam_z = proj_z + offset_z

    glu.gluLookAt(cam_x, cam_y, cam_z, proj_x, proj_y, proj_z, 0, 1, 0)


def confCameraFollowSide():
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(60.0, 800 / 512, 0.1, 1000.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    proj_x, proj_y, proj_z = controller.proj_pos
    cam_height = 30
    cam_side = -120 

    glu.gluLookAt(
        proj_x, proj_y + cam_height, proj_z + cam_side,  
        proj_x, proj_y, proj_z,                                     
        0, 1, 0   
    )

def display():
    global texture_grass

    if controller.is_launched:
        confCameraFollowSide()            
    else:
        confCamera()

    gl.glClearColor(1.0, 1.0, 1.0, 1.0) 
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glShadeModel(gl.GL_SMOOTH)

    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [1.0, 1.0, -1.0, 0.0])
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.1, 0.1, 0.1, 0.5])
    gl.glEnable(gl.GL_COLOR_MATERIAL)
    gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)

    obj.draw_sky()
    obj.draw_ground(texture_grass)
    obj.draw_cannon()
    obj.draw_cannon_barrel(controller.angle)
    
    if controller.is_launched:
        ball_pos = controller.proj_pos
        obj.draw_shadow(ball_pos, controller.angle, controller.force)
        obj.draw_ball(ball_pos)
    else:
        obj.draw_trajectory_preview(controller.angle, controller.force, controller.calculate_trajectory_points)

    controller.draw_hud()

    glut.glutSwapBuffers()

def main():
    global texture_grass
    glut.glutInit()
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutCreateWindow(b'Simulador de lancamento de projetil')
    glut.glutReshapeWindow(800, 512)
    
    texture_grass = obj.load_texture("Grass008_2K-PNG_Color.png") # carregue aqui, após o contexto
    
    confCamera()
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    glut.glutDisplayFunc(display)
    glut.glutKeyboardFunc(controller.keyboard)
    glut.glutSpecialFunc(controller.special_keyboard) 
    glut.glutIdleFunc(controller.update_projectile)

    glut.glutMainLoop()

if __name__ == "__main__":
    main()
