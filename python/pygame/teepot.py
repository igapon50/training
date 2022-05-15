#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys

diffuse = [0.7, 0.6, 0.2, 1.0]  # 拡散反射成分(R,G,B,A強度0.0〜1.0)
specular = [0.6, 0.5, 0.4, 1.0]  # 鏡面反射成分(R,G,B,A強度0.0〜1.0)
ambient = [0.3, 0.2, 0.1, 1.0]  # 環境光反射成分(R,G,B,A強度0.0〜1.0)
shininess = 10.0  # 鏡面光の鋭さ(0.0〜128.0)
angle = 0.0
width = 640
height = 480
display_size = (width, height)
main_dir = os.path.split(os.path.abspath(__file__))[0]


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    # glutInitDisplayMode(GLUT_RGB | GLUT_SINGLE | GLUT_DEPTH)
    glutInitWindowSize(width, height)     # window size
    glutInitWindowPosition(int(width/2), int(height/2))  # window position
    glutCreateWindow(b"teapot")      # show window
    glutDisplayFunc(display)         # draw callback function
    glutReshapeFunc(reshape)         # resize callback function
    glutIdleFunc(idle)
    init(300, 300)
    glutMainLoop()


def init(width, height):
    """ initialize """
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)  # enable shading
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)

    # テクスチャ画像の読み込み
    # path = os.path.join(main_dir, "data", "picture.jpg")
    path = os.path.join(main_dir, "data", "前.jpg")
    img = pg.image.load(path)
    img = pg.transform.smoothscale(img, display_size)
    img = pg.transform.flip(img, False, True)
    img_width = img.get_width()
    img_height = img.get_height()
    image_data = pg.image.tostring(img, "RGBA", True)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img_width, img_height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)  # アライメント(データの格納方法)の設定
    # テクスチャパラメータの設定(テクスチャマッピングの拡大・縮小法の設定)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # テクスチャの合成環境の設定(ポリゴンの陰影等をテクスチャに反映する等の設定)
    glTexEnvf(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_REPLACE)


def texture_map():
    """テクスチャマッピング開始"""
    glEnable(GL_TEXTURE_2D)
    glNormal3d(0.0, 0.0, 1.0)  # 法線ベクトルの設定
    glBegin(GL_QUADS)

    # glTexCoord2d(0, 1)
    # glVertex3d(-1, -1, 0)  # 左下
    # glTexCoord2d(1, 1)
    # glVertex3d(1, -1, 0)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, 1, 0)  # 右上
    # glTexCoord2d(0, 0)
    # glVertex3d(-1, 1, 0)  # 右下

    # 上面（緑）
    glColor3f(0.0, 1.0, 0.0)
    # glTexCoord2d(0, 1)
    glVertex3f(1.0, 1.0, -1.0)   # A
    # glTexCoord2d(0, 0)
    glVertex3f(-1.0, 1.0, -1.0)  # B
    # glTexCoord2d(1, 0)
    glVertex3f(-1.0, 1.0, 1.0)   # C
    # glTexCoord2d(1, 1)
    glVertex3f(1.0, 1.0, 1.0)    # D
    # 下面（オレンジ）
    glColor3f(1, 0.5, 0)
    # glTexCoord2d(0, 1)
    glVertex3f(1.0, -1.0, -1.0)  # E
    # glTexCoord2d(0, 0)
    glVertex3f(-1.0, -1.0, -1.0) # F
    # glTexCoord2d(1, 0)
    glVertex3f(-1.0, -1.0, 1.0)  # G
    # glTexCoord2d(1, 1)
    glVertex3f(1.0, -1.0, 1.0)   # H
    # 前面（赤）
    # glColor3f(1.0, 0.0, 0.0)
    glTexCoord2d(1, 0)
    glVertex3f(1.0, 1.0, 1.0)    # D
    glTexCoord2d(0, 0)
    glVertex3f(-1.0, 1.0, 1.0)   # C
    glTexCoord2d(0, 1)
    glVertex3f(-1.0, -1.0, 1.0)  # G
    glTexCoord2d(1, 1)
    glVertex3f(1.0, -1.0, 1.0)   # H
    # 背面（黄色）
    # glColor3f(1.0, 1.0, 0.0)
    glTexCoord2d(0, 0)
    glVertex3f(1.0, 1.0, -1.0)   # A
    glTexCoord2d(1, 0)
    glVertex3f(-1.0, 1.0, -1.0)  # B
    glTexCoord2d(1, 1)
    glVertex3f(-1.0, -1.0, -1.0) # F
    glTexCoord2d(0, 1)
    glVertex3f(1.0, -1.0, -1.0)  # E
    # 左側面（青）
    # glColor3f(0.0, 0.0, 1.0)
    glTexCoord2d(1, 0)
    glVertex3f(-1.0, 1.0, 1.0)   # C
    glTexCoord2d(0, 0)
    glVertex3f(-1.0, 1.0, -1.0)  # B
    glTexCoord2d(0, 1)
    glVertex3f(-1.0, -1.0, -1.0) # F
    glTexCoord2d(1, 1)
    glVertex3f(-1.0, -1.0, 1.0)  # G
    # 右側面（マゼンタ）
    # glColor3f(1.0, 0.0, 1.0)
    glTexCoord2d(0, 0)
    glVertex3f(1.0, 1.0, 1.0)    # D
    glTexCoord2d(1, 0)
    glVertex3f(1.0, 1.0, -1.0)   # A
    glTexCoord2d(1, 1)
    glVertex3f(1.0, -1.0, -1.0)  # E
    glTexCoord2d(0, 1)
    glVertex3f(1.0, -1.0, 1.0)   # H

    # # 上面
    # glTexCoord2d(0, 1)
    # glVertex3d(0, 0, 0)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(1, 0, 0)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, 0, -1)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(0, 0, -1)  # 右下
    # # 底面
    # glTexCoord2d(0, 1)
    # glVertex3d(0, -1, 0)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(0, -1, -1)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, -1, -1)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(1, -1, 0)  # 右下
    # # 左側
    # glTexCoord2d(0, 1)
    # glVertex3d(0, -1, 0)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(0, 0, 0)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(0, 0, -1)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(0, -1, -1)  # 右下
    # # 奥側
    # glTexCoord2d(0, 1)
    # glVertex3d(0, -1, -1)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(0, 0, -1)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, 0, -1)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(1, -1, -1)  # 右下
    # # 右側
    # glTexCoord2d(0, 1)
    # glVertex3d(1, -1, 0)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(1, 0, 0)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, 0, -1)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(1, -1, -1)  # 右下
    # # 手前側
    # glTexCoord2d(0, 1)
    # glVertex3d(0, -1, 0)  # 左下
    # glTexCoord2d(0, 0)
    # glVertex3d(0, 0, 0)  # 左上
    # glTexCoord2d(1, 0)
    # glVertex3d(1, 0, 0)  # 右上
    # glTexCoord2d(1, 1)
    # glVertex3d(1, -1, 0)  # 右下
    glEnd()
    glDisable(GL_TEXTURE_2D)


def display():
    """ display """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # set camera
    gluLookAt(0.0, 1.0, 5.0,  # 視点の位置
              0.0, 0.0, 0.0,  # 対象の位置
              0.0, 1.0, 0.0)  # 画像の上となる位置(ベクトル)
    glRotatef(angle, 0.0, 1.0, 0.0)
    # draw a teapot
    glColor3f(0.9, 1.0, 0.9)
    # glutWireTeapot(1.0)   # wireframe
    # glutSolidTeapot(1.0)  # solid
    # 立方体の描画（外側）
    # glLineWidth(2.0)
    # glutWireCube(2.0)
    # 照明をON
    # glEnable(GL_LIGHT0);
    # glEnable(GL_LIGHTING);

    # 表面属性の設定
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialf(GL_FRONT, GL_SHININESS, shininess)
    texture_map()
    # glFlush()  # enforce OpenGL command
    glutSwapBuffers()


def reshape(width, height):
    """callback function resize window"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 100.0)


def idle():
    """アイドル時に呼ばれるコールバック関数"""
    global angle
    angle += 2  # 角度を更新
    glutPostRedisplay()  # 再描画


if __name__ == "__main__":
    main()
