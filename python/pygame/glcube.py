#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OpenGLを使った3Dの立体アニメーションのお勉強
Gimp前景抽出選択ツールの使い方
https://gazocustomize.com/gimp-foreground-extraction-tool/
ブログ
https://qiita.com/i-tanaka730/items/ad56461a4f223fdbb4e5
http://www.mit.edu/~brignole/3dem.html
https://aidiary.hatenablog.com/entry/20080915/1281750879
https://aidiary.hatenablog.com/entry/20081018/1281751729
http://gunload.web.fc2.com/opengl/tutorial/skinning/pygame/
documents
http://westplain.sakuraweb.com/translate/pygame/Examples.cgi#pygame.examples.glcube.main
https://docs.microsoft.com/ja-jp/windows/win32/opengl/opengl
https://docs.microsoft.com/en-us/dotnet/api/android.opengl.gles20.glgetuniformlocation?view=xamarin-android-sdk-12
git
https://github.com/pygame/pygame/blob/main/examples/glcube.py
"""
from pygame.examples.glcube import *
import os
from math import sin

width = 640
height = 480
display_size = (width, height)


def draw_cube_modern_mouse(shader_data, filled_cube_indices, outline_cube_indices, rotation, x, y):
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

    # Filled cube
    GL.glDisable(GL.GL_BLEND)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_POLYGON_OFFSET_FILL)
    GL.glUniform4f(shader_data["constants"]["colour_mul"], 1, 1, 1, 1)
    GL.glUniform4f(shader_data["constants"]["colour_add"], 0, 0, 0, 0.0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["filled"])
    GL.glDrawElements(
        GL.GL_TRIANGLES, len(filled_cube_indices), GL.GL_UNSIGNED_INT, None
    )

    # Outlined cube
    GL.glDisable(GL.GL_POLYGON_OFFSET_FILL)
    GL.glEnable(GL.GL_BLEND)
    GL.glUniform4f(shader_data["constants"]["colour_mul"], 0, 0, 0, 0.0)
    GL.glUniform4f(shader_data["constants"]["colour_add"], 1, 1, 1, 1.0)
    GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, shader_data["buffer"]["outline"])
    GL.glDrawElements(GL.GL_LINES, len(outline_cube_indices), GL.GL_UNSIGNED_INT, None)

    # Rotate cube
    # rotation.theta += 1.0  # degrees
    rotation.phi += 1.0 * x  # degrees
    rotation.psi += 1.0 * y  # degrees
    model = eye(4, dtype=float32)
    # rotate(model, rotation.theta, 0, 0, 1)
    rotate(model, rotation.phi, 0, 1, 0)
    rotate(model, rotation.psi, 1, 0, 0)
    GL.glUniformMatrix4fv(shader_data["constants"]["model"], 1, False, model)


def main():
    """run the demo"""

    # initialize pygame and setup an opengl display
    pg.init()
    screen = pg.display.set_mode(display_size, pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE)

    # load image and quadruple
    # main_dir = os.path.split(os.path.abspath(__file__))[0]
    # image_name = os.path.join(main_dir, "data", "picture.jpg")
    # img = pg.image.load(image_name)
    # img = pg.transform.smoothscale(img, display_size)
    # # img = pg.transform.scale(img, display_size)
    # screen.blit(img, (int((width - img.get_width()) / 2), int((height - img.get_height()) / 2)))
    # pg.display.flip()
    # print("flip")
    # pg.time.wait(1000)

    gl_version = (3, 0)  # GL Version number (Major, Minor)
    if USE_MODERN_GL:
        gl_version = (3, 2)  # GL Version number (Major, Minor)

        # By setting these attributes we can choose which Open GL Profile
        # to use, profiles greater than 3.2 use a different rendering path
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, gl_version[0])
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, gl_version[1])
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
    full_screen = False  # start in windowed mode

    if USE_MODERN_GL:
        gpu, f_indices, o_indices = init_gl_modern(display_size)
        rotation = Rotation()
    else:
        init_gl_stuff_old()

    _x = _y = 0.0
    going = True
    while going:
        # check for quit'n events
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT or (
                event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
            ):
                going = False

            elif event.type == pg.KEYDOWN and event.key == pg.K_f:
                if not full_screen:
                    print("Changing to FULLSCREEN")
                    pg.display.set_mode(
                        (640, 480), pg.OPENGL | pg.DOUBLEBUF | pg.FULLSCREEN
                    )
                else:
                    print("Changing to windowed mode")
                    pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
                full_screen = not full_screen
                if gl_version[0] >= 4 or (gl_version[0] == 3 and gl_version[1] >= 2):
                    gpu, f_indices, o_indices = init_gl_modern(display_size)
                    rotation = Rotation()
                else:
                    init_gl_stuff_old()

        x, y = pg.mouse.get_rel()
        print(x, y)
        magnification = 2.0
        if USE_MODERN_GL:
            draw_cube_modern_mouse(gpu, f_indices, o_indices, rotation,
                                   float(_x + x) / magnification, float(_y + y) / magnification)
        else:
            # clear screen and move camera
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
            # orbit camera around by 1 degree
            GL.glRotatef(1, 0, _x + x, _y + y)
            drawcube_old()
        _x = x
        _y = y

        pg.display.flip()
        pg.time.wait(10)

    pg.quit()


if __name__ == '__main__':
    main()
