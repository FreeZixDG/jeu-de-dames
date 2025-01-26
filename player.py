from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Optional

from case import Case, PlayableCase
from piece import Piece
from strategy import Strategy
from team import Team

if TYPE_CHECKING:
    from board import Board
    from game import Game

OptionalPlayableCase = Optional[PlayableCase]


class Player:
    def __init__(self, player_id, name, team: Team):
        self._id = player_id
        self._name = name
        self._team = team
        self._points = 0
        self._eaten_pieces = []
        self._last_selected_case: OptionalPlayableCase = None
        self._possible_moves: list[PlayableCase] = []

        self._move_paths = []

    def get_player_id(self) -> int:
        return self._id

    def get_name(self):
        return self._name

    def get_team(self) -> Team:
        return self._team

    def get_possible_moves(self):
        return self._possible_moves

    def on_click(self, board: Board, coordinates: tuple[int, int]) -> bool:
        has_played = False

        case = board.get_case(coordinates)

        if isinstance(case, PlayableCase):

            if case.can_land():
                if self._last_selected_case.get_can_play():
                    has_played = True
                    board.clear_cases_who_can_play()
                    for move in self._move_paths:
                        if move["move_path"][-1] == case.get_coordinates():
                            if move["move_path"][0] == self._last_selected_case.get_coordinates():
                                self.play_move(board, move)




            elif case.contains_piece_of_team(self.get_team()) and case.get_can_play():
                self.deselect_case()
                self.clear_possible_moves(board)
                self._last_selected_case = case
                self._last_selected_case.set_selected(True)

                moves = case.get_move()
                self._move_paths = moves
                self.add_possible_move([move["move_path"] for move in self._move_paths])
                return has_played

        self.deselect_case()
        self.clear_possible_moves(board)
        return has_played



    def deselect_case(self):
        if self._last_selected_case is not None:
            self._last_selected_case.set_selected(False)
            self._last_selected_case = None

    def add_possible_move(self, case: Case):
        self._possible_moves += case

    def clear_possible_moves(self, board: Board):
        for move in self._possible_moves:
            for coord in move:
                case = board.get_playable_case(coord)
                case.set_can_land(False)
        self._possible_moves.clear()

    def _move_piece(self, start, end: PlayableCase):
        piece = start.get_piece()
        start.set_piece(None)
        end.set_piece(piece)
        return end.try_promotion()

    def win(self, win):
        if win:
            self._points += 1
        else:
            self._points -= 1

    def __repr__(self):
        return f"{self._name} ({self._team.value}) {self._eaten_pieces}"

    def _eat_pieces(self, board: Board, eating_list):
        for coord in eating_list:
            case = board.get_playable_case(coord)
            piece = case.get_piece()
            case.set_piece(None)
            self._eaten_pieces += [piece]

    def play_move(self, board, move):
        promoted = self._move_piece(board.get_case(move["move_path"][0]), board.get_case(move["move_path"][-1]))
        self._eat_pieces(board, move["eaten_pieces"])
        return promoted

    def undo_move(self, board, move, unpromote=False):
        if unpromote:
            board.get_case(move["move_path"][-1]).set_piece(Piece(self.get_team()))
        self._move_piece(board.get_case(move["move_path"][-1]), board.get_case(move["move_path"][0]))
        self._vomit_pieces(board, move["eaten_pieces"])

    def _vomit_pieces(self, board, eating_list):
        for coord in eating_list:
            case = board.get_playable_case(coord)
            case.set_piece(self._eaten_pieces.pop())


class AI(Player):
    def __init__(self, player_id, name, team: Team, strategy: Strategy):
        super().__init__(player_id, name, team)
        self.strategy = strategy

    def play(self, game: Game):
        state = {
            "board": game.get_board(),
            "self_player": self,
            "enemy_player": game.get_player1(),
            "current_player": self,
        }
        self.strategy.update(state)
        game.render()
        start, end = self.strategy.choose_move(deepcopy(state))

        # time.sleep(1)
        self.on_click(game.get_board(), start)
        game.draw()
        self.on_click(game.get_board(), end)
        print(f"{self} plays {start} -> {end}")
        return True

    def __repr__(self):
        return f"{self._name} ({self._team.value}) (Start: {self.strategy.__class__.__name__})"
