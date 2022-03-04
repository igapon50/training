#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pygame.examples.glcube import *
import os

magnification = 2.0


# 関数の出口に終了処理を追加するデコレータ
def cleanup(func):
    def wrap(*args):
        print('cleanup')
        func(*args)
        pg.quit()
    return wrap


class PyGame:
    def __init__(self):
        self._running = True
        self._screen = None
        self.gpu = None
        self.f_indices = None
        self.o_indices = None
        self.rotation = None
        self._x = 0.0
        self._y = 0.0
        # eventの分岐をディクショナリに変更
        self._eventMap = {
            pg.QUIT: self.on_quit,
            pg.MOUSEBUTTONDOWN: self.on_mouse_down,
            pg.MOUSEBUTTONUP: self.on_mouse_up,
            pg.MOUSEMOTION: self.on_mouse_motion,
        }

    def initialize(self, w, h):
        pg.init()
        # OPENGL向けに初期化する
        self._screen = pg.display.set_mode((w, h), pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

        # GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        # GL.glEnable(GL.GL_DEPTH_TEST)  # enable shading
        # GL.glMatrixMode(GL.GL_PROJECTION)
        # GL.glLoadIdentity()
        # GL.gluPerspective(45.0, float(w) / float(h), 0.1, 100.0)

        # テクスチャ画像の読み込み
        main_dir = os.path.split(os.path.abspath(__file__))[0]
        image_name = os.path.join(main_dir, "data", "picture.jpg")
        img = pg.image.load(image_name)
        img = pg.transform.smoothscale(img, (w, h))
        img = pg.transform.flip(img, False, True)
        img_width = img.get_width()
        img_height = img.get_height()
        image_data = pg.image.tostring(img, "RGBA", True)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, img_width, img_height,
                        0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, image_data)
        # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)  # アライメント(データの格納方法)の設定
        # テクスチャパラメータの設定(テクスチャマッピングの拡大・縮小法の設定)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
        # テクスチャの合成環境の設定(ポリゴンの陰影等をテクスチャに反映する等の設定)
        GL.glTexEnvf(GL.GL_TEXTURE_ENV, GL.GL_TEXTURE_ENV_MODE, GL.GL_REPLACE)

        pg.display.flip()
        gl_version = (3, 2)  # GL Version number (Major, Minor)
        # By setting these attributes we can choose which Open GL Profile
        # to use, profiles greater than 3.2 use a different rendering path
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, gl_version[0])
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, gl_version[1])
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        self.gpu, self.f_indices, self.o_indices = init_gl_modern((w, h))
        self.rotation = Rotation()
        self.texture_map()
        if not self._screen:
            return

        return True

    def on_event(self, event):
        if event.type in self._eventMap:
            self._eventMap[event.type](event)

    def on_quit(self, event):
        self._running = False

    def on_mouse_down(self, event):
        if event.button == 1:
            print('on_mouse_down', 'left', event.pos)
        elif event.button == 2:
            print('on_mouse_down', 'middle', event.pos)
        elif event.button == 3:
            print('on_mouse_down', 'right', event.pos)
        elif event.button == 4:
            print('on_mouse_down', 'wheel_up', event.pos)
        elif event.button == 5:
            print('on_mouse_down', 'wheel_down', event.pos)

    def on_mouse_up(self, event):
        if event.button == 1:
            print('on_mouse_up', 'left', event.pos)
        elif event.button == 2:
            print('on_mouse_up', 'middle', event.pos)
        elif event.button == 3:
            print('on_mouse_up', 'right', event.pos)
        elif event.button == 4:
            print('on_mouse_up', 'wheel_up', event.pos)
        elif event.button == 5:
            print('on_mouse_up', 'wheel_down', event.pos)

    def on_mouse_motion(self, event):
        print('onMouseMotion', event.pos, event.rel, event.buttons)
        x, y = pg.mouse.get_rel()
        self.draw_cube_modern_mouse(self.gpu, self.f_indices, self.o_indices, self.rotation,
                                    float(self._x + x) / magnification, float(self._y + y) / magnification)
        self._x = x
        self._y = y

    def update(self):
        pass

    def draw(self):
        # OpenGLバッファのクリア
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        # 三角形描画開始
        GL.glBegin(GL.GL_TRIANGLES)
        # 左下
        GL.glVertex(-1, -1)
        # 右下
        GL.glVertex(1, -1)
        # 上
        GL.glVertex(0, 1)
        # 三角形描画終了
        GL.glEnd()
        # OpenGL描画実行
        GL.glFlush()

        # pygameダブルバッファ交換
        pg.display.flip()

    def draw_cube_modern_mouse(self, shader_data, filled_cube_indices, outline_cube_indices, rotation, x, y):
        """
        Draw a cube in the 'modern' Open GL style, for post 3.1 versions of
        open GL.
        :param shader_data: compile vertex & pixel shader data for drawing a cube.
        :param filled_cube_indices: the indices to draw the 'filled' cube.
        :param outline_cube_indices: the indices to draw the 'outline' cube.
        :param rotation: the current rotations to apply.
        :param x: Phi移動量、Y軸に対してのローテーション
        :param y: Psi移動量、X軸に対してのローテーション
        """

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # # Filled cube
        # GL.glDisable(GL.GL_BLEND)
        # GL.glEnable(GL.GL_DEPTH_TEST)
        # GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
        # GL.glUniform4f(shader_data["constants"]["colour_mul"], 1, 1, 1, 1)
        # GL.glUniform4f(shader_data["constants"]["colour_add"], 0, 0, 0, 0.0)
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["filled"])
        # GL.glDrawElements(
        #     GL.GL_TRIANGLES, len(filled_cube_indices), GL.GL_UNSIGNED_INT, None
        # )
        #
        # # Outlined cube
        # GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
        # GL.glEnable(GL.GL_BLEND)
        # GL.glUniform4f(shader_data["constants"]["colour_mul"], 0, 0, 0, 0.0)
        # GL.glUniform4f(shader_data["constants"]["colour_add"], 1, 1, 1, 1.0)
        # GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["outline"])
        # GL.glDrawElements(GL.GL_LINES, len(outline_cube_indices), GL.GL_UNSIGNED_INT, None)
        self.texture_map()

        # Rotate cube
        # rotation.theta += 1.0  # degrees
        rotation.phi += 1.0 * x  # degrees
        rotation.psi += 1.0 * y  # degrees
        model = eye(4, dtype=float32)
        # rotate(model, rotation.theta, 0, 0, 1)
        rotate(model, rotation.phi, 0, 1, 0)
        rotate(model, rotation.psi, 1, 0, 0)
        GL.glUniformMatrix4fv(shader_data["constants"]["model"], 1, False, model)

    def texture_map(self):
        """テクスチャマッピング開始"""
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glNormal3d(0.0, 0.0, 1.0)  # 法線ベクトルの設定
        GL.glBegin(GL.GL_QUADS)

        # 上面（緑）
        GL.glColor3f(0.0, 1.0, 0.0)
        # GL.glTexCoord2d(0, 1)
        GL.glVertex3f(1.0, 1.0, -1.0)  # A
        # GL.glTexCoord2d(0, 0)
        GL.glVertex3f(-1.0, 1.0, -1.0)  # B
        # GL.glTexCoord2d(1, 0)
        GL.glVertex3f(-1.0, 1.0, 1.0)  # C
        # GL.glTexCoord2d(1, 1)
        GL.glVertex3f(1.0, 1.0, 1.0)  # D
        # 下面（オレンジ）
        GL.glColor3f(1, 0.5, 0)
        # GL.glTexCoord2d(0, 1)
        GL.glVertex3f(1.0, -1.0, -1.0)  # E
        # GL.glTexCoord2d(0, 0)
        GL.glVertex3f(-1.0, -1.0, -1.0)  # F
        # GL.glTexCoord2d(1, 0)
        GL.glVertex3f(-1.0, -1.0, 1.0)  # G
        # GL.glTexCoord2d(1, 1)
        GL.glVertex3f(1.0, -1.0, 1.0)  # H
        # 前面（赤）
        # GL.glColor3f(1.0, 0.0, 0.0)
        GL.glTexCoord2d(1, 0)
        GL.glVertex3f(1.0, 1.0, 1.0)  # D
        GL.glTexCoord2d(0, 0)
        GL.glVertex3f(-1.0, 1.0, 1.0)  # C
        GL.glTexCoord2d(0, 1)
        GL.glVertex3f(-1.0, -1.0, 1.0)  # G
        GL.glTexCoord2d(1, 1)
        GL.glVertex3f(1.0, -1.0, 1.0)  # H
        # 背面（黄色）
        # GL.glColor3f(1.0, 1.0, 0.0)
        GL.glTexCoord2d(0, 0)
        GL.glVertex3f(1.0, 1.0, -1.0)  # A
        GL.glTexCoord2d(1, 0)
        GL.glVertex3f(-1.0, 1.0, -1.0)  # B
        GL.glTexCoord2d(1, 1)
        GL.glVertex3f(-1.0, -1.0, -1.0)  # F
        GL.glTexCoord2d(0, 1)
        GL.glVertex3f(1.0, -1.0, -1.0)  # E
        # 左側面（青）
        # GL.glColor3f(0.0, 0.0, 1.0)
        GL.glTexCoord2d(1, 0)
        GL.glVertex3f(-1.0, 1.0, 1.0)  # C
        GL.glTexCoord2d(0, 0)
        GL.glVertex3f(-1.0, 1.0, -1.0)  # B
        GL.glTexCoord2d(0, 1)
        GL.glVertex3f(-1.0, -1.0, -1.0)  # F
        GL.glTexCoord2d(1, 1)
        GL.glVertex3f(-1.0, -1.0, 1.0)  # G
        # 右側面（マゼンタ）
        # GL.glColor3f(1.0, 0.0, 1.0)
        GL.glTexCoord2d(0, 0)
        GL.glVertex3f(1.0, 1.0, 1.0)  # D
        GL.glTexCoord2d(1, 0)
        GL.glVertex3f(1.0, 1.0, -1.0)  # A
        GL.glTexCoord2d(1, 1)
        GL.glVertex3f(1.0, -1.0, -1.0)  # E
        GL.glTexCoord2d(0, 1)
        GL.glVertex3f(1.0, -1.0, 1.0)  # H

        GL.glEnd()
        GL.glDisable(GL.GL_TEXTURE_2D)
        # pygameダブルバッファ交換
        pg.display.flip()
        pg.time.wait(10)

    @cleanup
    def execute(self, w, h):
        if not self.initialize(w, h):
            return

        while self._running:
            for event in pg.event.get():
                self.on_event(event)
            self.update()
            self.texture_map()
            # self.draw()


if __name__ == "__main__":
    game = PyGame()
    game.execute(640, 480)
