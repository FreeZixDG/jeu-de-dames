from __future__ import annotations

import time
from copy import deepcopy
from typing import TYPE_CHECKING, Optional

from case import Case, PlayableCase
from strategy import Strategy
from team import Team

if TYPE_CHECKING:
    from board import Board
    from game import Game

OptionalPlayableCase = Optional[PlayableCase]


class Player:
    def __init__(self, player_id, name, team: Team):
        self.__id = player_id
        self.__name = name
        self.__team = team
        self.__points = 0
        self.__eaten_pieces = []
        self.__last_selected_case: OptionalPlayableCase = None
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

    def on_click(self, board: Board, coordinates: tuple[int, int]) -> bool:
        has_played = False

        case = board.get_case(coordinates)

        if isinstance(case, PlayableCase):

            if case.can_land():
                if self.__last_selected_case.get_can_play():
                    has_played = True
                    print("clearing !")
                    board.clear_cases_who_can_play()
                    for move in self.__move_paths:
                        if move["move_path"][-1] == case.get_coordinates():
                            self.__move_piece(board.get_case(move["move_path"][-1]))
                            for coord in move["eaten_pieces"]:
                                case = board.get_playable_case(coord)
                                piece = case.get_piece()
                                case.set_piece(None)
                                self.__eaten_pieces += [piece]

            elif case.contains_piece_of_team(self.get_team()) and case.get_can_play():
                self.deselect_case()
                self.clear_possible_moves(board)
                self.__last_selected_case = case
                self.__last_selected_case.set_selected(True)

                piece = case.get_piece()
                moves = piece.get_valid_paths(board, case.get_coordinates())
                self.__move_paths = moves
                self.add_possible_move([move["move_path"] for move in self.__move_paths])
                return has_played

        self.deselect_case()
        self.clear_possible_moves(board)
        return has_played

    def deselect_case(self):
        if self.__last_selected_case is not None:
            self.__last_selected_case.set_selected(False)
            self.__last_selected_case = None

    def add_possible_move(self, case: Case):
        self.__possible_moves += case

    def clear_possible_moves(self, board: Board):
        for move in self.__possible_moves:
            for coord in move:
                case = board.get_playable_case(coord)
                case.set_can_land(False)
        self.__possible_moves.clear()

    def __move_piece(self, case: PlayableCase):
        piece = self.__last_selected_case.get_piece()
        self.__last_selected_case.set_piece(None)
        case.set_piece(piece)
        case.try_promotion()

    def win(self, win):
        if win:
            self.__points += 1
        else:
            self.__points -= 1

    def __repr__(self):
        return f"{self.__name} ({self.__team.value}) {self.__eaten_pieces}"


class AI(Player):
    def __init__(self, player_id, name, team: Team, strategy: Strategy):
        super().__init__(player_id, name, team)
        self.strategy = strategy

    def play(self, game: Game):
        self.strategy.update(game.board)
        start, end = self.strategy.choose_move(deepcopy(game.board))
        game.render()
        time.sleep(1)
        self.on_click(game.board, start)
        game.draw()
        self.on_click(game.board, end)
        print(f"AI plays {start} -> {end}")
        return True
