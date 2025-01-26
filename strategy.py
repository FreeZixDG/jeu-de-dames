from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from case import PlayableCase

if TYPE_CHECKING:
    from board import Board
    from player import AI

State = dict

INF = float('inf')


class Strategy:
    def __init__(self):
        self._start_cases: list[PlayableCase] = []
        self._moves: list[PlayableCase] = []

    def update(self, state: State):
        board = state["board"]
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
            best_value = -INF
            for new_board in self.get_childs(state):
                best_value = max(best_value, self.minimax(new_board, depth - 1, False))
            return best_value
        else:
            best_value = INF
            for new_board in self.get_childs(state):
                best_value = min(best_value, self.minimax(new_board, depth - 1, True))
            return best_value

    def neg_alpha_beta(self, state: State, depth: int, alpha, beta, color: int):
        if self.is_leaf(state) or depth == 0:
            return color * self.evaluate(state), state, "Terminal"

        best_value = -INF
        best_state = None
        best_move = None
        for new_state, new_move in self.get_childs(state):
            value, _, _ = self.neg_alpha_beta(new_state, depth - 1, -beta, -alpha, -color)
            value = -value
            if value > best_value:
                best_value = value
                best_state = new_state
                best_move = new_move

            alpha = max(alpha, value)
            if alpha >= beta:
                return alpha, best_state, best_move
        return best_value, best_state, best_move

    def choose_move(self, state: State):
        val, new_state, best_move = self.neg_alpha_beta(state, 6, -INF, +INF, color=1)
        print(val)
        return best_move

    def is_leaf(self, state: State):
        return not state["board"].find_cases_who_can_play(state["current_player"])

    def evaluate(self, state):
        board: Board = state["board"]
        self_player = state["self_player"]
        if self.is_leaf(state):
            return self.score(state)

        value = 0
        for feature in self.features(state):
            value += feature

        return value

    def get_childs(self, state):
        board: Board = state["board"]
        current_player: AI = state["current_player"]
        enemy_player = state["enemy_player"]
        self_player = state["self_player"]
        result = []
        cases_who_can_play = board.find_cases_who_can_play(current_player)

        for _, moves in cases_who_can_play:
            for move in moves:
                new_board = copy.deepcopy(board)
                current_player.play_move(new_board, move)
                result.append([{
                    "board": new_board,
                    "self_player": self_player,
                    "enemy_player": enemy_player,
                    "current_player": self_player if current_player != self_player else enemy_player,
                }, (move["move_path"][0], move["move_path"][-1])])
        return result

    def score(self, state):
        board: Board = state["board"]
        current_player: AI = state["current_player"]
        enemy_player = state["enemy_player"]
        self_player = state["self_player"]

        number_of_self_pieces = count_number_of_pieces_of_team(board, self_player.get_team())

        number_of_enemy_pieces = count_number_of_pieces_of_team(board, enemy_player.get_team())

        if number_of_self_pieces == 0:
            return -INF
        elif number_of_enemy_pieces == 0:
            return INF
        else:
            return 0

    def features(self, state):
        board: Board = state["board"]
        current_player: AI = state["current_player"]
        enemy_player = state["enemy_player"]
        self_player = state["self_player"]
        features = []
        features.append(1 * count_number_of_pieces_of_team(board, self_player.get_team()))
        features.append(-1 * count_number_of_pieces_of_team(board, enemy_player.get_team()))
        return features


def count_number_of_pieces_of_team(board: Board, team):
    return len(list(board.get_cases(
        lambda c: isinstance(c, PlayableCase) and c.contains_piece_of_team(team)
    )))
