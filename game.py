from copy import deepcopy

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
        board = deepcopy(self.board)

        player1 = deepcopy(self.player1)
        player1.clear_possible_moves()
        player1.deselect_case()
        player2 = deepcopy(self.player2)
        player2.clear_possible_moves()
        player2.deselect_case()
        state = {
            "board": board,
            "player1": player1,
            "player2": player2
        }
        self.history.append(state)
        print("state saved!")
        print(self.history)

    def undo(self):
        if len(self.history) <= 1:
            print("No more history to undo")
            print(self.history)
            return
        print(self.history)
        self.history.pop()
        self.board = deepcopy(self.history[-1]["board"])
        self.player1 = deepcopy(self.history[-1]["player1"])
        self.player2 = deepcopy(self.history[-1]["player2"])
        self.render()

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
                        self.__save_board_state()
                else:
                    self.player2.on_click((x, y), self.board)
                    print(f"({self.player2}) Clicked on ({self.board.get_case((x, y))})")
                    if not self.player2.get_his_turn():
                        self.player1.set_his_turn(True)
                        self.__save_board_state()

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
                elif event.key == pg.K_t:
                    print(self.player1.get_his_turn())
                    print(self.player2.get_his_turn())

    def render(self):
        self.screen.fill("black")
        self.board.draw(self.screen, self.size, self.offset)
        pg.display.flip()

    def run(self):
        self.__save_board_state()
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(10)
        pg.quit()
