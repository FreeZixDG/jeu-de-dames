from copy import deepcopy

import pygame as pg

from board import Board
from case import PlayableCase
from colors_constants import ARROWS_COLOR
from config import SCREEN_SIZE, GRID_SIZE, CELL_SIZE, OFFSET, LINES_INDICATOR_WIDTH
from player import Player, AI
from strategy import RandomStrategy
from team import Team


class Game:
    def __init__(self, init_board: str = None, player1: str = "Player1", player2: str = "Player 2"):
        pg.init()
        self._screen = pg.display.set_mode(SCREEN_SIZE)
        self._clock = pg.time.Clock()
        self._running = True
        self._board = Board(GRID_SIZE, init_board) if init_board else Board(GRID_SIZE)

        self._size = CELL_SIZE
        self._offset = OFFSET

        self._history = []

        self._is_edit_mode = False

        self._winner = None
        self._player1 = Player(0, player1, Team.WHITE)
        self._player2 = AI(1, player2, Team.BLACK, RandomStrategy())
        self._current_player = self._player1

    def save_board_state(self):
        board = deepcopy(self._board)

        player1 = deepcopy(self._player1)
        player1.clear_possible_moves(self._board)
        player1.deselect_case()
        player2 = deepcopy(self._player2)
        player2.clear_possible_moves(self._board)
        player2.deselect_case()

        current_player = True if self._current_player == self._player1 else False
        winner = None if self._winner is None else True if self._winner == self._player1 else False
        state = {
            "board": board,
            "player1": player1,
            "player2": player2,
            "current_player": current_player,
            "winner": winner,
        }
        self._history.append(state)
        # print("state saved!")
        # print(self.history)

    def undo(self):
        if len(self._history) <= 1:
            print("No more history to undo")
            print(self._history)
            return
        print(self._history)
        self._history.pop()
        self._board = deepcopy(self._history[-1]["board"])
        self._player1 = deepcopy(self._history[-1]["player1"])
        self._player2 = deepcopy(self._history[-1]["player2"])
        self._current_player = self._player1 if self._history[-1]["current_player"] == True else self._player2
        self._winner = None if self._history[-1]["winner"] is None else self._player1 if self._history[-1][
                                                                                             "winner"] == True else self._player2
        self.render()

    def get_board(self):
        return self._board

    def switch_current_player(self):
        """Switch the current player to the other player."""
        self._current_player = self._player1 if self._current_player == self._player2 else self._player2

    def find_cases_who_can_play(self):
        if self._board.get_cases_who_can_play():
            return []
        # liste toutes les cases et leurs moves possibles
        cases_data = []
        for case in self._board.get_cases(
                lambda c: isinstance(c, PlayableCase) and c.contains_piece_of_team(self._current_player.get_team())):
            cases_data.append((case, case.get_piece().get_valid_paths(self._board, case.get_coordinates())))

        cases_with_totals = [
            (case_info[0], case_info[1], len(case_info[1][0]["eaten_pieces"]) if case_info[1] else 0)
            for case_info in cases_data
        ]

        if not cases_with_totals:
            self.declare_winner(self._player1 if self._current_player == self._player2 else self._player2)
            return []

        max_move = max(total for _, _, total in cases_with_totals)
        if max_move == 0:
            cases_with_totals = [
                (case_info[0], case_info[1], len(case_info[1][0]["move_path"]) if case_info[1] else 0)
                for case_info in cases_data
            ]
            max_move = max(total for _, _, total in cases_with_totals)
            if max_move == 0:
                self.declare_winner(self._player1 if self._current_player == self._player2 else self._player2)
                return []
        # building result
        cases_who_can_play = []
        result = []
        for case, move, total in cases_with_totals:
            if total == max_move:
                cases_who_can_play.append(case)
                result.append((case, move))
        self._board.set_cases_who_can_play(cases_who_can_play)
        return result

    def highlight_cases_who_can_play(self):
        case_who_can_play = self.find_cases_who_can_play()
        for case, move in case_who_can_play:
            case.set_can_play(move)

    def handle_events(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._running = False
                return
            if self._is_edit_mode:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        self._is_edit_mode = False
                        print("edit mode: False")
                        return
                    if event.key == pg.K_c:
                        print("clear")
                        for case in self._board.get_cases(lambda c: isinstance(c, PlayableCase)):
                            case.set_piece(None)

                        return

                    from piece import Piece, Queen
                    x = mouse_x // (self._size + self._offset)
                    y = mouse_y // (self._size + self._offset)
                    case = self._board.get_case((x, y))
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
                if self._winner is not None: return
                x = mouse_x // (self._size + self._offset)
                y = mouse_y // (self._size + self._offset)
                has_played = self._current_player.on_click(self._board, (x, y))
                print(f"({self._player1}) Clicked on {self._board.get_case((x, y))}")
                if has_played:
                    self.switch_current_player()
                    self.render()
                    # tester
                    if isinstance(self._current_player, AI) and self._winner is None:
                        self._current_player.play(self)
                        self.switch_current_player()
                        self.save_board_state()
                return

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    self._is_edit_mode = True
                    print(f"edit mode: {self._is_edit_mode}")
                    self._board.clear_cases_who_can_play()
                if event.key == pg.K_a:
                    import pyperclip
                    pyperclip.copy(str(self._board))
                    print(self._board)
                elif event.key == pg.K_z:
                    print("Undoing...")
                    self.undo()
                elif event.key == pg.K_s:
                    print("Saving...")
                    self.save_board_state()
                return

    def render(self):
        self._screen.fill("black")
        self.draw()
        pg.display.flip()

    def run(self):
        self.save_board_state()
        while self._running:
            if self._winner:
                self.end()
            self.handle_events()
            self.render()
            self._clock.tick(60)
        pg.quit()

    def draw(self):
        for row in self._board.get_board():
            for case in row:
                case.draw(self._screen, self._size, self._offset)

        self.highlight_moves()
        self.highlight_cases_who_can_play()

    def highlight_moves(self):
        """Met en évidence les cases accessibles."""

        for path in self._current_player.get_possible_moves():
            last_case = self._board.get_playable_case(path[-1])
            last_case.set_can_land(True)

            case = self._board.get_selected_case()
            self.draw_arrows(case.get_coordinates(), path[0])
            for i in range(len(path) - 1):
                self.draw_arrows(path[i], path[i + 1])

    def draw_arrows(self, start_coord, end_coord):
        start_pos = add(mult(start_coord, (self._size + self._offset)), int(self._size // 2))
        end_pos = add(mult(end_coord, (self._size + self._offset)), int(self._size // 2))
        pg.draw.line(self._screen, ARROWS_COLOR, start_pos, end_pos, LINES_INDICATOR_WIDTH)

    def declare_winner(self, param):
        self._winner = param
        self._winner.win(True)
        self._current_player.win(False)
        self.end()

    def end(self):
        game_font = pg.font.SysFont("Arial", 50)
        text = game_font.render(f"{self._winner.get_team().value}s won !", 1, (0, 0, 0))
        self._screen.blit(text, (int(SCREEN_SIZE[0] // 4), int(SCREEN_SIZE[1] // 4)))


def mult(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x * c, t))


def add(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x + c, t))
