from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from case import PlayableCase
from colors_constants import *
from config import GRID_SIZE
from team import Team

if TYPE_CHECKING:
    from board import Board


class Piece:
    def __init__(self, team: Team):
        self._team = team

        match self._team:
            case Team.WHITE:
                self._color_in = WHITE_COLOR
                self._color_out = BLACK_COLOR
            case Team.BLACK:
                self._color_in = BLACK_COLOR
                self._color_out = WHITE_COLOR

    def get_team(self):
        return self._team

    def get_valid_paths(self, board: Board, current_position: tuple[int, int]) -> list[list[tuple[int, int]]]:
        # result += self.get_can_eat(game, current_position)
        result = board.compute_eating_moves(board.get_case(current_position))
        if result:
            return result

        result += self.get_can_move(board, current_position)

        return result

    def get_can_move(self, board: Board, current_position: tuple[int, int]):
        result = []
        if self._team is Team.WHITE:
            result += self.get_valid_moves_for_diagonal(board, current_position, (-1, -1))
            result += self.get_valid_moves_for_diagonal(board, current_position, (1, -1))
        else:
            result += self.get_valid_moves_for_diagonal(board, current_position, (-1, 1))
            result += self.get_valid_moves_for_diagonal(board, current_position, (1, 1))
        return result

    def get_can_eat(self, board: Board, current_position: tuple[int, int], eaten_pieces, ignore=None) -> list[
        list[tuple[int, int]]]:
        result = []
        diagonals = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
        if ignore is not None:
            diagonals = [x for x in diagonals if x not in ignore]

        for diagonal in diagonals:
            moves = self.get_can_eat_for_diagonal(board, current_position, diagonal, eaten_pieces)
            if moves:
                result += [moves]
        return result

    def get_valid_moves_for_diagonal(self, board: Board, current_position: tuple[int, int],
                                     diagonal: tuple[int, int]) -> list[dict[list[tuple[int, int]]]]:
        result = []
        dir_x, dir_y = diagonal
        x, y = current_position
        x, y = x + 1 * dir_x, y + 1 * dir_y

        case = board.get_case((x, y))
        if not board.is_valid_move((x, y)):
            return result
        if isinstance(case, PlayableCase):
            if case.get_piece() is None:
                result.append({"move_path": [current_position, (x, y)], "eaten_pieces": []})
                return result
            elif case.get_piece().get_team() == self._team:
                return []

        return result

    def get_can_eat_for_diagonal(self, board: Board, current_position: tuple[int, int],
                                 diagonal: tuple[int, int], eaten_pieces) -> list[tuple[int, int]]:
        dir_x, dir_y = diagonal
        x, y = current_position
        x, y = x + 1 * dir_x, y + 1 * dir_y
        case = board.get_case((x, y))
        if not board.is_valid_move((x, y)):
            return []
        if (x, y) in eaten_pieces:
            return []
        if isinstance(case, PlayableCase):
            if case.get_piece() is None:
                return []
            if case.get_piece().get_team() != self._team:
                x, y = x + 1 * dir_x, y + 1 * dir_y
                if board.is_valid_move((x, y)) and board.get_playable_case((x, y)).get_piece() is None:
                    return [(x, y)]
        return []

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:

        pg.draw.circle(surface, self._color_out,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2.1)
        pg.draw.circle(surface, self._color_in,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2.3)

    def __repr__(self):
        if self._team is not None:
            return f"{self._team.value}"


class Queen(Piece):
    def __init__(self, team: Team):
        super().__init__(team)

    def get_valid_paths(self, board: Board, current_position: tuple[int, int]) -> list[tuple[int, int]]:
        result = []
        # result += self.get_can_eat(game, current_position)
        result += board.compute_eating_moves(board.get_case(current_position))
        if result:
            return result

        result += self.get_valid_moves_for_diagonal(board, current_position, (1, 1))
        result += self.get_valid_moves_for_diagonal(board, current_position, (1, -1))
        result += self.get_valid_moves_for_diagonal(board, current_position, (-1, -1))
        result += self.get_valid_moves_for_diagonal(board, current_position, (-1, 1))

        return result

    def get_can_eat_for_diagonal(self, board: Board, current_position: tuple[int, int],
                                 diagonal: tuple[int, int], eaten_pieces) -> list[tuple[int, int]]:
        dir_x, dir_y = diagonal
        x, y = current_position

        result = []
        has_met_opponent = False
        for i in range(1, GRID_SIZE):
            x, y = x + 1 * dir_x, y + 1 * dir_y
            case = board.get_case((x, y))
            if not board.is_valid_move((x, y)):
                break
            if (x, y) in eaten_pieces:
                break
            if isinstance(case, PlayableCase):
                if case.get_piece() is None:
                    if not has_met_opponent:
                        continue
                    result.append((x, y))
                elif case.get_piece().get_team() == self._team:
                    break
                else:
                    if has_met_opponent:
                        break
                    has_met_opponent = True
        return result

    def get_valid_moves_for_diagonal(self, board: Board, current_position: tuple[int, int],
                                     diagonal: tuple[int, int]) -> list[list[tuple[int, int]]]:
        dir_x, dir_y = diagonal
        x, y = current_position
        result = []
        for i in range(1, GRID_SIZE):
            x, y = x + 1 * dir_x, y + 1 * dir_y
            case = board.get_case((x, y))
            if not board.is_valid_move((x, y)):
                break
            if isinstance(case, PlayableCase):
                if case.get_piece() is None:
                    result.append({"move_path": [current_position, (x, y)], "eaten_pieces": []})
                else:
                    break

        return result

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:
        super().draw(surface, location, size, offset)
        pg.draw.circle(surface, self._color_out,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 6)

    def __repr__(self):
        if self._team is not None:
            return f"{self._team.value} Queen"