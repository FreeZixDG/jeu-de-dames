# Example file showing a basic pygame "game loop"
import numpy as np
import pygame as pg

# pygame setup
pg.init()
screen = pg.display.set_mode((1280, 720))
clock = pg.time.Clock()
running = True
GRID = np.zeros((10, 10))
W = 50
OFFSET = 2

while running:
    mouse_x, mouse_y = pg.mouse.get_pos()
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            print(mouse_x // (W + OFFSET), mouse_y // (W + OFFSET))

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    # RENDER YOUR GAME HERE
    for y, row in enumerate(GRID):
        for x, col in enumerate(row):
            if x == 2 and y == 5:
                pg.draw.rect(screen, "#713a36", pg.Rect(x * (W + OFFSET), y * (W + OFFSET), W, W))
            else:
                pg.draw.rect(screen, "#ffcb98", pg.Rect(x * (W + OFFSET), y * (W + OFFSET), W, W))

    # flip() the display to put your work on screen
    pg.display.flip()

    clock.tick(60)  # limits FPS to 60

pg.quit()
