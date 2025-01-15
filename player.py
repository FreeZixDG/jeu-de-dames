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
        self.__eaten_pieces = []
        self.__his_turn = True if self.__team == Team.WHITE else False

        self.__selected_case: OptionalPlayableCase = None
        self.__possible_moves: list[PlayableCase] = []

    def get_his_turn(self) -> bool:
        return self.__his_turn

    def set_his_turn(self, value: bool):
        self.__his_turn = value

    def get_player_id(self) -> int:
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
            for case in self.__get_cases_between_start_and_end(board, case):
                piece = case.get_content()
                if not (piece is None or piece.get_team() == self.__team):
                    case.set_content(None)
                    self.__eaten_pieces += [piece]
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
        self.set_his_turn(False)

    def __get_cases_between_start_and_end(self, board: Board, case: PlayableCase) -> list[PlayableCase]:
        start_x, start_y = self.__selected_case.get_coordinates()
        end_x, end_y = case.get_coordinates()
        step_x = 1 if end_x > start_x else -1
        step_y = 1 if end_y > start_y else -1

        current_x, current_y = start_x + step_x, start_y + step_y
        result = []

        while (current_x, current_y) != (end_x, end_y):
            result.append(board.get_case((current_x, current_y)))
            current_x += step_x
            current_y += step_y

        return result

    def __repr__(self):
        return f"{self.__name} ({self.__team.value}) {self.__eaten_pieces}"
