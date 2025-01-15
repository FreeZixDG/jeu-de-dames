import re

import numpy as np
import pygame as pg

from case import Case, PlayableCase
from colors_constants import *
from piece import Piece, Queen
from team import Team


def mult(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x * c, t))


def add(t: tuple[int | float, ...], c: int | float):
    return tuple(map(lambda x: x + c, t))


def moddiv(a, b):
    return a % b, a // b

class Board:
    def __init__(self, size: int, init: str = "20B10.20w"):
        self.__size = size
        self.__board = np.zeros((size, size), dtype=Case)

        self.init = [(int(num) if num else 1, char) for num, char in re.findall(r"(\d*)([wW]|[bB]|[.])", init)]
        total = 0
        for num, char in self.init:
            for i in range(num):
                i += total
                x, y = moddiv(i * 2, size)
                if (i // (size // 2)) % 2 == 0:
                    self.__board[x, y] = Case((x, y))
                    x, y = moddiv(i * 2 + 1, size)
                    self.put_playable_case((x, y), char)
                else:
                    self.put_playable_case((x, y), char)
                    x, y = moddiv(i * 2 + 1, size)
                    self.__board[(x, y)] = Case((x, y))
            total += num

    def put_playable_case(self, coordinates: int | tuple[int, int], char: str):
        match char:
            case 'b':
                team = Team.BLACK
                piece_type = Piece
            case 'w':
                team = Team.WHITE
                piece_type = Piece
            case 'B':
                team = Team.BLACK
                piece_type = Queen
            case 'W':
                team = Team.WHITE
                piece_type = Queen
            case '.':
                team = None
                piece_type = None
            case _:
                raise ValueError("Invalid character in init string")
        if team is not None:
            self.__board[coordinates] = PlayableCase(coordinates, content=piece_type(team))
        else:
            self.__board[coordinates] = PlayableCase(coordinates)

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
        if not (0 <= x < self.__size and 0 <= y < self.__size):
            return None
        return self.__board[x, y]

    def is_valid_move(self, coordinates: tuple[int, int]) -> bool:
        """Vérifie si des coordonnées sont valides pour le plateau."""
        x, y = coordinates
        return 0 <= x < self.__size \
            and 0 <= y < self.__size

    def __get_landable_cases(self):
        return self.get_cases(
            lambda c: isinstance(c, PlayableCase) and c.is_landable())

    def get_cases(self, condition):
        return (case for case in self.__board.flatten() if condition(case))

    def is_case(self, coordinates: tuple[int, int], condition) -> bool:
        return condition(self.get_case(coordinates))
