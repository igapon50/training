#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygame as pg
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]


def main():
    # initialize and setup screen
    pg.init()
    width = 640
    height = 480
    display_size = (width, height)
    screen = pg.display.set_mode(display_size, pg.HWSURFACE | pg.DOUBLEBUF)

    # load image and quadruple
    image_name = os.path.join(main_dir, "data", "picture.jpg")
    img = pg.image.load(image_name)
    img = pg.transform.smoothscale(img, display_size)
    # img = pg.transform.scale(img, display_size)

    # get the image and screen in the same format
    if screen.get_bitsize() == 8:
        screen.set_palette(img.get_palette())
    else:
        img = img.convert()
    screen.blit(img, (0, 0))
    stop_events = pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN
    while True:
        for e in pg.event.get():
            if e.type in stop_events:
                return
        pg.display.flip()
        pg.time.wait(10)


if __name__ == "__main__":
    main()
    pg.quit()
