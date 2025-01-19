from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from case import Case, PlayableCase
from team import Team

if TYPE_CHECKING:
    from game import Game
    from board import Board

OptionalPlayableCase = Optional[PlayableCase]


class Player:
    def __init__(self, player_id, name, team: Team):
        self.__id = player_id
        self.__name = name
        self.__team = team
        self.__eaten_pieces = []
        self.__selected_case: OptionalPlayableCase = None
        self.__possible_moves: list[PlayableCase] = []

        self.__move_paths = []

    def get_player_id(self) -> int:
        return self.__id

    def get_name(self):
        return self.__name

    def get_team(self) -> Team:
        return self.__team

    def get_possible_moves(self):
        return self.__possible_moves

    def on_click(self, game: Game, coordinates: tuple[int, int]) -> bool:
        has_played = False

        case = game.board.get_case(coordinates)
        if not isinstance(case, PlayableCase):
            pass

        elif case.can_land():
            if self.__selected_case.get_can_play():
                has_played = True
                print("clearing")
                game.clear_cases_who_can_play()
                for move in self.__move_paths:
                    if move["move_path"][-1] == case.get_coordinates():
                        self.__move_piece(game.board.get_case(move["move_path"][-1]))
                        for coord in move["eaten_pieces"]:
                            case = game.board.get_case(coord)
                            piece = case.get_piece()
                            case.set_piece(None)
                            self.__eaten_pieces += [piece]

        elif case.contains_piece_of_team(self.get_team()) and case.get_can_play():
            self.deselect_case()
            self.clear_possible_moves(game.board)
            self.__selected_case = case
            self.__selected_case.set_selected(True)

            piece = case.get_piece()
            moves = piece.get_valid_paths(game, case.get_coordinates())
            self.__move_paths = moves
            self.add_possible_move([move["move_path"] for move in self.__move_paths])
            return has_played

        self.deselect_case()
        self.clear_possible_moves(game.board)
        return has_played

    def deselect_case(self):
        if self.__selected_case is not None:
            self.__selected_case.set_selected(False)
            self.__selected_case = None

    def add_possible_move(self, case: Case):
        self.__possible_moves += case

    def clear_possible_moves(self, board: Board):
        for move in self.__possible_moves:
            for coord in move:
                case = board.get_playable_case(coord)
                case.set_can_land(False)
        self.__possible_moves.clear()

    def __move_piece(self, case: PlayableCase):
        piece = self.__selected_case.get_piece()
        self.__selected_case.set_piece(None)
        case.set_piece(piece)
        case.try_promotion()

    def __repr__(self):
        return f"{self.__name} ({self.__team.value}) {self.__eaten_pieces}"
