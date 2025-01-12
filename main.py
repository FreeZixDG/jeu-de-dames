# Example file showing a basic pygame "game loop"
import numpy as np
import pygame as pg

from board import Board

# pygame setup
pg.init()
screen = pg.display.set_mode((820, 820))
clock = pg.time.Clock()
running = True
GRID = np.zeros((10, 10))
SIZE = 80
OFFSET = 2
BOARD = Board((10, 10))

while running:
    mouse_x, mouse_y = pg.mouse.get_pos()
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            X = mouse_x // (SIZE + OFFSET)
            Y = mouse_y // (SIZE + OFFSET)
            print(BOARD.getCase((X, Y)))

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    # RENDER YOUR GAME HERE
    BOARD.draw(screen, SIZE, OFFSET)

    # flip() the display to put your work on screen
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()
