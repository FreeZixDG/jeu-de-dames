import pygame as pg
from board import Board
from player import Player
from team import Team
from config import SCREEN_SIZE, GRID_SIZE, CELL_SIZE, OFFSET

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.board = Board(GRID_SIZE)
        self.player = Player(0, "jerem", Team.WHITE)
        self.size = CELL_SIZE
        self.offset = OFFSET

    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                x = mouse_x // (self.size + self.offset)
                y = mouse_y // (self.size + self.offset)
                self.player.on_click((x, y), self.board)
                print(f"Clicked on ({self.board.get_case((x, y))})")


    def render(self):
        self.screen.fill("grey")
        self.board.draw(self.screen, self.size, self.offset)
        pg.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(10)
        pg.quit()