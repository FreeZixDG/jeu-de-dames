from __future__ import annotations

from case import Case, PlayableCase

from team import Team

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from board import Board

OptionalPlayableCase = Optional[PlayableCase]


class Player:
    def __init__(self, player_id, name, team: Team):
        self.__id = player_id
        self.__name = name
        self.__team = team

        self.__selected_case: OptionalPlayableCase = None
        self.__possible_moves: list[PlayableCase] = []

    def get_player_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def on_click(self, coordinates: tuple[int, int], board: Board):

        case = board.get_case(coordinates)

        if self.__contains_self_piece(case):
            self.__deselect_case()
            self.clear_possible_moves()
            self.__selected_case = case
            self.__selected_case.set_selected(True)

            piece = case.get_content()
            valid_moves = piece.get_valid_moves(board, case.get_coordinates())
            self.highlight_moves(board, valid_moves)


        elif isinstance(case, PlayableCase) and case.is_landable():
            self.__move_piece(case)
            self.__deselect_case()
            self.clear_possible_moves()
        else:
            self.__deselect_case()
            self.clear_possible_moves()

    def highlight_moves(self, board: Board, valid_moves: list[tuple[int, int]]):
        """Met en évidence les cases accessibles."""
        for move in valid_moves:
            move_case = board.get_case(move)
            if isinstance(move_case, PlayableCase) and not move_case.get_content():  # Case vide uni
                self.add_possible_move(move_case)  # Ou une couleur spécifique pour indiquer possibilité
                self.__possible_moves[-1].set_landable(True)

    def __deselect_case(self):
        if self.__selected_case is not None:
            self.__selected_case.set_selected(False)

    def add_possible_move(self, case: Case):
        self.__possible_moves += [case]

    def clear_possible_moves(self):
        for case in self.__possible_moves:
            case.set_landable(False)
        self.__possible_moves.clear()

    def __contains_self_piece(self, case: Case):
        return isinstance(case, PlayableCase) \
            and case.get_content() is not None \
            and case.get_content().get_team() == self.__team

    def __move_piece(self, case: PlayableCase):
        piece = self.__selected_case.get_content()

        case.set_content(piece)
        self.__selected_case.set_content(None)
