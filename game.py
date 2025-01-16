import pygame as pg

from board import Board
from config import SCREEN_SIZE, GRID_SIZE, CELL_SIZE, OFFSET
from player import Player
from team import Team


class Game:
    def __init__(self, init_board: str = None, player1: str = "Player1", player2: str = "Player 2"):
        pg.init()
        self.screen = pg.display.set_mode(SCREEN_SIZE)
        self.clock = pg.time.Clock()
        self.running = True
        self.board = Board(GRID_SIZE, init_board) if init_board else Board(GRID_SIZE)
        self.player1 = Player(0, player1, Team.WHITE)
        self.player2 = Player(1, player2, Team.BLACK)
        self.size = CELL_SIZE
        self.offset = OFFSET

        self.history = []

    def __save_board_state(self):
        from copy import deepcopy
        state = {
            "board": deepcopy(self.board),
            "player1": deepcopy(self.player1),
            "player2": deepcopy(self.player2)
        }
        self.history.append(state)
        print("state saved!")

    def undo(self):
        if len(self.history) <= 1:
            print("No more history to undo")
            return
        self.history.pop()
        self.board = self.history[-1]["board"]
        self.player1 = self.history[-1]["player1"]
        self.player2 = self.history[-1]["player2"]

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
                elif event.key == pg.K_z:
                    print("Undoing...")
                    self.undo()
                elif event.key == pg.K_s:
                    print("Saving...")
                    self.__save_board_state()

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
