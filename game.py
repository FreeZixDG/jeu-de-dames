import copy
from copy import deepcopy, copy

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

        self.__marked_cases = []
        self.history = []

    def get_marked_cases(self):
        return self.__marked_cases

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
        # print("state saved!")
        # print(self.history)

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

    def compute_eating_moves(self, playable_case: PlayableCase) -> list[tuple[int, int]]:
        all_paths = []

        def loop(playable_case: PlayableCase, eating_path=None):
            if eating_path is None:
                eating_path = []

            # Liste des coups possibles
            start_position = playable_case.get_coordinates()
            possible_moves = playable_case.get_piece().get_can_eat(self, start_position)

            if not possible_moves:  # Cas feuille
                all_paths.append(eating_path)
                return eating_path

            for next_position in possible_moves:  # Parcours des coups possibles
                self.simulate_eat(start_position, next_position)
                eating_path.append(next_position)
                loop(self.board.get_case(next_position), copy(eating_path))
                eating_path.pop()
                self.simulate_move(next_position, start_position)

            longueur_max = max(len(sous_liste) for sous_liste in all_paths)
            return [sous_liste for sous_liste in all_paths if len(sous_liste) == longueur_max]

        best_path = loop(playable_case)
        self.__marked_cases.clear()

        return best_path

    def simulate_move(self, start_pos, end_pos):
        start_case = self.board.get_case(start_pos)
        end_case = self.board.get_case(end_pos)
        assert isinstance(start_case, PlayableCase)
        assert isinstance(end_case, PlayableCase)

        piece_to_move = start_case.get_piece()
        start_case.set_piece(None)
        end_case.set_piece(piece_to_move)

    def simulate_eat(self, start_pos, end_pos):
        start_case = self.board.get_case(start_pos)
        end_case = self.board.get_case(end_pos)
        assert isinstance(start_case, PlayableCase)
        assert isinstance(end_case, PlayableCase)

        self.simulate_move(start_pos, end_pos)

        cases_between = self.board.get_cases_between_start_and_end(start_case, end_case)
        for case in cases_between:
            if case.contains_enemy_piece(self.current_player.get_team()):
                # print(f"adding {case} to marked !")
                self.__marked_cases += [case.get_coordinates()]
                return

    def switch_current_player(self):
        """Switch the current player to the other player."""
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2

    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x = mouse_x // (self.size + self.offset)
                    y = mouse_y // (self.size + self.offset)

                    has_played = self.current_player.on_click(self, (x, y))
                    print(f"({self.player1}) Clicked on {self.board.get_case((x, y))}")
                    if has_played:
                        self.switch_current_player()
                        self.save_board_state()
                else:
                    x = mouse_x // (self.size + self.offset)
                    y = mouse_y // (self.size + self.offset)
                    print(self.compute_eating_moves(self.board.get_case((x, y))))

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
