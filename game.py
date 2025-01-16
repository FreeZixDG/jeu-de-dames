import pygame as pg

from board import Board
from config import SCREEN_SIZE, GRID_SIZE, CELL_SIZE, OFFSET
from player import Player
from team import Team


class Game:
    def __init__(self, init_board: str = None):
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.board = Board(GRID_SIZE, init_board) if init_board else Board(GRID_SIZE)
        self.player1 = Player(0, "jerem", Team.WHITE)
        self.player2 = Player(1, "Player2", Team.BLACK)
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
                if self.player1.get_his_turn():
                    self.player1.on_click((x, y), self.board)
                    print(f"({self.player1}) Clicked on {self.board.get_case((x, y))}")
                    if not self.player1.get_his_turn():
                        self.player2.set_his_turn(True)
                else:
                    self.player2.on_click((x, y), self.board)
                    print(f"({self.player2}) Clicked on ({self.board.get_case((x, y))})")
                    if not self.player2.get_his_turn():
                        self.player1.set_his_turn(True)
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    import pyperclip
                    pyperclip.copy(str(self.board))
                    print(self.board)

    def render(self):
        self.screen.fill("black")
        self.board.draw(self.screen, self.size, self.offset)
        pg.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(10)
        pg.quit()
