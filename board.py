from typing import Any

import numpy as np
import pygame as pg
from colors_constants import *
from case import Case, PlayableCase
from team import Team
from piece import Piece, Queen


def mult(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x * c, t))


def add(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x + c, t))


class Board:
    def __init__(self, size: tuple[int, int], init: str = None):
        self.__size = size
        self.__board = np.zeros(size, dtype=Case)

        for y in range(size[0]):
            for x in range(size[1]):
                if (x + y) % 2 == 0:
                    self.__board[x, y] = Case((x, y))
                    continue

                if y >= 6:
                    self.__board[x, y] = PlayableCase((x, y), content=Piece(Team.WHITE))
                elif y <= 3:
                    self.__board[x, y] = PlayableCase((x, y), content=Piece(Team.BLACK))
                else:
                    self.__board[x, y] = PlayableCase((x, y))

                if x == 5 and y == 6:
                    self.__board[x, y] = PlayableCase((x, y), content=Queen(Team.WHITE))

    def draw(self, screen: pg.Surface, size: int, offset: int = 0):
        for row in self.__board:
            for case in row:
                case.draw(screen, size, offset)
        self.__draw_arrows(screen, size, offset)

    def __draw_arrows(self, screen: pg.Surface, size: int, offset: int):
        case = self.__get_selected_case()
        if case is None:
            return

        landables = list(self.__get_landable_cases())
        for i in range(len(landables)):
            start_pos = add(mult(case.get_coordinates(), (size + offset)), int(size // 2))
            end_pos = add(mult(landables[i].get_coordinates(), (size + offset)), int(size // 2))
            pg.draw.line(screen, ARROWS_COLOR, start_pos, end_pos, 3)

    def __get_selected_case(self):
        return next(self.get_cases(lambda c: isinstance(c, PlayableCase) and c.is_selected()), None)

    def get_case(self, coordinates: tuple[int, int]) -> np.ndarray[tuple[int, int], np.dtype[Case]] | None:
        x, y = coordinates
        if not (0 <= x < self.__size[0] and 0 <= y < self.__size[1]):
            return None
        return self.__board[x, y]

    def is_valid_move(self, coordinates: tuple[int, int]) -> bool:
        """Vérifie si des coordonnées sont valides pour le plateau."""
        x, y = coordinates
        return 0 <= x < self.__size[0] \
            and 0 <= y < self.__size[1]

    def __get_landable_cases(self):
        return self.get_cases(
            lambda c: isinstance(c, PlayableCase) and c.is_landable())

    def get_cases(self, condition):
        return (case for case in self.__board.flatten() if condition(case))

    def is_case(self, coordinates: tuple[int, int], condition) -> bool:
        return condition(self.get_case(coordinates))

