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

    def get_player_id(self) -> int:
        return self.__id

    def get_name(self):
        return self.__name

    def get_team(self) -> Team:
        return self.__team

    def on_click(self, game: Game, coordinates: tuple[int, int]) -> bool:
        has_played = False

        case = game.board.get_case(coordinates)

        if self.__contains_self_piece(case):
            self.deselect_case()
            self.clear_possible_moves()
            self.__selected_case = case
            self.__selected_case.set_selected(True)

            piece = case.get_piece()
            valid_moves = piece.get_valid_moves(game, case.get_coordinates())
            self.highlight_moves(game.board, valid_moves)


        elif isinstance(case, PlayableCase) and case.can_land():
            self.__move_piece(case)
            has_played = True
            for c in game.board.get_cases_between_start_and_end(self.__selected_case, case):
                if c.contains_enemy_piece(self.__team):
                    piece = c.get_piece()
                    c.set_piece(None)
                    self.__eaten_pieces += [piece]

                    # if case.get_piece().get_can_eat(game, case.get_coordinates()):
                    if game.compute_eating_moves(case):
                        has_played = False
                        self.deselect_case()
                        self.clear_possible_moves()
                        from game import Game
                        game.save_board_state()
                        game.render()
                        return has_played

            self.deselect_case()
            self.clear_possible_moves()
        else:
            self.deselect_case()
            self.clear_possible_moves()

        game.render()
        return has_played

    def highlight_moves(self, board: Board, valid_moves: list[tuple[int, int]]):
        """Met en évidence les cases accessibles."""
        for move in valid_moves:
            move_case = board.get_case(move)
            if isinstance(move_case, PlayableCase) and not move_case.get_piece():  # Case vide uni
                self.add_possible_move(move_case)  # Ou une couleur spécifique pour indiquer possibilité
                self.__possible_moves[-1].set_can_land(True)

    def deselect_case(self):
        if self.__selected_case is not None:
            self.__selected_case.set_selected(False)
            self.__selected_case = None

    def add_possible_move(self, case: Case):
        self.__possible_moves += [case]

    def clear_possible_moves(self):
        for case in self.__possible_moves:
            case.set_can_land(False)
        self.__possible_moves.clear()

    def __contains_self_piece(self, case: Case):
        return isinstance(case, PlayableCase) \
            and case.get_piece() is not None \
            and case.get_piece().get_team() == self.__team

    def __move_piece(self, case: PlayableCase):
        piece = self.__selected_case.get_piece()

        case.set_piece(piece)
        case.promote()
        self.__selected_case.set_piece(None)

    def __repr__(self):
        return f"{self.__name} ({self.__team.value}) {self.__eaten_pieces}"
