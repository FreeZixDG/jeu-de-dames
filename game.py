import copy
from copy import deepcopy, copy

import pygame as pg

from board import Board
from case import PlayableCase
from colors_constants import ARROWS_COLOR
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

        self.is_edit_mode = False

    def get_marked_cases(self):
        return self.__marked_cases

    def save_board_state(self):
        board = deepcopy(self.board)

        player1 = deepcopy(self.player1)
        player1.clear_possible_moves(self.board)
        player1.deselect_case()
        player2 = deepcopy(self.player2)
        player2.clear_possible_moves(self.board)
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

    def compute_eating_moves(self, playable_case: PlayableCase) -> list[list[tuple[int, int]]]:
        all_paths = []

        def loop(playable_case: PlayableCase, move_path=None, eaten_pieces=None):
            if move_path is None:
                move_path = []
            if eaten_pieces is None:
                eaten_pieces = []

            # Liste des coups possibles
            start_position = playable_case.get_coordinates()
            possible_moves = playable_case.get_piece().get_can_eat(self, start_position)

            if not possible_moves:  # Cas feuille
                if not move_path:
                    return []
                move = {"move_path": move_path, "eaten_pieces": eaten_pieces}
                all_paths.append(move)
                return move

            for next_position in possible_moves:  # Parcours des coups possibles
                eaten_piece = self.simulate_eat(start_position, next_position)
                eaten_pieces.append(eaten_piece)
                move_path.append(next_position)
                loop(self.board.get_case(next_position), copy(move_path), copy(eaten_pieces))
                move_path.pop()
                eaten_pieces.pop()
                self.simulate_move(next_position, start_position)

            longueur_max = max(len(sous_liste["move_path"]) for sous_liste in all_paths)
            return [sous_liste for sous_liste in all_paths if len(sous_liste["move_path"]) == longueur_max]

        best_path = loop(playable_case)
        self.__marked_cases.clear()

        return best_path

    def simulate_move(self, start_pos, end_pos):
        start_case = self.board.get_playable_case(start_pos)
        end_case = self.board.get_playable_case(end_pos)

        piece_to_move = start_case.get_piece()
        start_case.set_piece(None)
        end_case.set_piece(piece_to_move)

    def simulate_eat(self, start_pos, end_pos):
        start_case = self.board.get_playable_case(start_pos)
        end_case = self.board.get_playable_case(end_pos)

        self.simulate_move(start_pos, end_pos)

        cases_between = self.board.get_cases_between_start_and_end(start_case, end_case)
        for case in cases_between:
            opposite_team = self.player1.get_team() if self.current_player == self.player2 else self.player2.get_team()
            if case.contains_piece_of_team(opposite_team):
                # print(f"adding {case} to marked !")
                eaten_case = case.get_coordinates()
                self.__marked_cases += [eaten_case]
                return eaten_case

    def switch_current_player(self):
        """Switch the current player to the other player."""
        self.current_player = self.player1 if self.current_player == self.player2 else self.player2

    def find_cases_who_can_play(self):
        # liste toutes les cases et leurs moves possibles
        cases_data = []
        for case in self.board.get_cases(
                lambda c: isinstance(c, PlayableCase) and c.contains_piece_of_team(self.current_player.get_team())):
            cases_data.append((case, self.compute_eating_moves(case)))

        cases_with_totals = [
            (case_info[0], len(case_info[1][0]["eaten_pieces"]) if case_info[1] else 0)
            for case_info in cases_data
        ]

        max_eaten = max(total for _, total in cases_with_totals)

        return [case for case, total in cases_with_totals if total == max_eaten]

    def highlight_cases_who_can_play(self):
        pass

    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                return
            if self.is_edit_mode:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self.is_edit_mode = False
                        print("edit mode: False")
                        return
                    if event.key == pg.K_c:
                        print("clear")
                        for case in self.board.get_cases(lambda c: isinstance(c, PlayableCase)):
                            case.set_piece(None)

                        return

                    from piece import Piece, Queen
                    x = mouse_x // (self.size + self.offset)
                    y = mouse_y // (self.size + self.offset)
                    case = self.board.get_case((x, y))
                    if isinstance(case, PlayableCase):
                        piece = None
                        if event.key == pg.K_q:
                            piece = Piece(Team.WHITE)
                        if event.key == pg.K_d:
                            piece = Piece(Team.BLACK)
                        if event.key == pg.K_z:
                            piece = Queen(Team.WHITE)
                        if event.key == pg.K_s:
                            piece = Queen(Team.BLACK)
                        case.set_piece(piece)
                return

            if event.type == pg.MOUSEBUTTONDOWN:
                x = mouse_x // (self.size + self.offset)
                y = mouse_y // (self.size + self.offset)
                if event.button == 1:

                    has_played = self.current_player.on_click(self, (x, y))
                    print(f"({self.player1}) Clicked on {self.board.get_case((x, y))}")
                    if has_played:
                        self.switch_current_player()
                        self.save_board_state()
                else:
                    print(self.find_cases_who_can_play())
                return

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    self.is_edit_mode = True
                    print(f"edit mode: {self.is_edit_mode}")
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
                return

    def render(self):
        self.screen.fill("black")
        self.draw()
        pg.display.flip()

    def run(self):
        self.save_board_state()
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(60)
        pg.quit()

    def draw(self):
        for row in self.board.get_board():
            for case in row:
                case.draw(self.screen, self.size, self.offset)

        self.highlight_moves()

    def highlight_moves(self):
        """Met en évidence les cases accessibles."""

        for path in self.current_player.get_possible_moves():
            last_case = self.board.get_playable_case(path[-1])
            last_case.set_can_land(True)

            case = self.board.get_selected_case()
            if case is None:
                return
            self.draw_arrows(case.get_coordinates(), path[0])
            for i in range(len(path) - 1):
                self.draw_arrows(path[i], path[i + 1])

    def draw_arrows(self, start_coord, end_coord):
        start_pos = add(mult(start_coord, (self.size + self.offset)), int(self.size // 2))
        end_pos = add(mult(end_coord, (self.size + self.offset)), int(self.size // 2))
        pg.draw.line(self.screen, ARROWS_COLOR, start_pos, end_pos, 3)


def mult(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x * c, t))


def add(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x + c, t))
