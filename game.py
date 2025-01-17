from copy import deepcopy

import pygame as pg

from board import Board
from case import PlayableCase
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

        self.current_player = self.player1
        self.size = CELL_SIZE
        self.offset = OFFSET

        self.history = []

    def save_board_state(self):
        board = deepcopy(self.board)

        player1 = deepcopy(self.player1)
        player1.clear_possible_moves()
        player1.deselect_case()
        player2 = deepcopy(self.player2)
        player2.clear_possible_moves()
        player2.deselect_case()

        current_player = True if self.current_player == self.player1 else False
        state = {
            "board": board,
            "player1": player1,
            "player2": player2,
            "current_player": current_player,
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
        self.current_player = self.player1 if self.history[-1]["current_player"] == True else self.player2
        self.render()

    def FINAL_get_eat(self, case: PlayableCase, result=None) -> list[tuple[int, int]]:
        if result is None: result = []

        # lister les coups possibles de la piece dans la case
        possible_moves = case.get_content().get_can_eat(self.board, case.get_coordinates())
        # si la liste est vide (c'est qu'on atteint une feuille).
        if not possible_moves:
            # renvoyer le nombre de piece mangée et sortir
            return result


        # pour chaque coup dans cette liste de coups
        for move in possible_moves:
            pass
            # jouer le coup (en gros manger)
            # rebelote
            # vomir le coup (ctrl z en gros)

        # renvoyer la liste de coup la plus longue

        pass

    def switch_current_player(self):
        """Switch the current player to the other player."""
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2
    
    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                x = mouse_x // (self.size + self.offset)
                y = mouse_y // (self.size + self.offset)

                has_played = self.current_player.on_click(self, (x, y))
                print(f"({self.player1}) Clicked on {self.board.get_case((x, y))}")
                if has_played:
                    self.switch_current_player()
                    self.save_board_state()

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
                    self.save_board_state()

    def render(self):
        self.screen.fill("black")
        self.board.draw(self.screen, self.size, self.offset)
        pg.display.flip()

    def run(self):
        self.save_board_state()
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(24)
        pg.quit()
