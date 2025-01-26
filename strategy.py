from dataclasses import dataclass
from typing import TYPE_CHECKING

from case import PlayableCase

if TYPE_CHECKING:
    from board import Board
    from player import Player


@dataclass
class State:
    board: "Board"
    current_player: "Player"


class Strategy:
    def __init__(self):
        self._start_cases: list[PlayableCase] = []
        self._moves: list[PlayableCase] = []

    def update(self, state: State):
        board = state.board
        self._start_cases = board.get_cases_who_can_play()
        self._moves = []
        for case in self._start_cases:
            for move in case.get_piece().get_valid_paths(board, case.get_coordinates()):
                self._moves += [(case.get_coordinates(), move["move_path"][-1])]

    def choose_move(self, state: State):
        raise NotImplementedError


class RandomStrategy(Strategy):
    def __init__(self):
        super().__init__()

    def choose_move(self, state: State):
        from random import choice
        result_start, result_end = choice(self._moves)

        return result_start, result_end


class MiniMax(Strategy):
    def __init__(self):
        super().__init__()

    def minimax(self, state: State, depth: int, maximizing_player: bool):
        if self.is_leaf(state) or depth == 0:
            return self.evaluate(state)
        if maximizing_player:
            best_value = -9999
            for new_board in self.get_childs(state):
                best_value = max(best_value, self.minimax(new_board, depth - 1, False))
            return best_value
        else:
            best_value = 9999
            for new_board in self.get_childs(state):
                best_value = min(best_value, self.minimax(new_board, depth - 1, True))
            return best_value

    def choose_move(self, state: State):
        pass

    def is_leaf(self, state: State):
        pass

    def evaluate(self, state):
        pass

    def get_childs(self, state):
        board = state.board
        current_player = state.current_player
        for case in board.get_cases(
                lambda c: isinstance(c, PlayableCase) and c.contains_piece_of_team(current_player.get_team())):
            if case.get_piece().get_valid_paths(board, case.get_coordinates()):
                return False
        return True
