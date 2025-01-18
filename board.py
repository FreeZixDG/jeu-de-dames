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


def factorize_string(string: str) -> str:
    factorized = ""
    count = 1
    for i in range(1, len(string)):
        if string[i] == string[i - 1]:
            count += 1
        else:
            factorized += f"{count if count > 1 else ''}{string[i - 1]}"
            count = 1
    factorized += f"{count if count > 1 else ''}{string[-1]}"
    return factorized


class Board:
    def __init__(self, size: int, init: str = "20b10.20w"):
        self.__size = size
        self.__board = np.zeros((size, size), dtype=Case)

        self.init = [(int(num) if num else 1, char) for num, char in re.findall(r"(\d*)([wW]|[bB]|[.])", init)]
        total = 0

        def put_playable_case(coordinates, char):
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

        for num, char in self.init:
            for i in range(num):
                i += total
                x, y = moddiv(i * 2, size)
                if (i // (size // 2)) % 2 == 0:
                    self.__board[x, y] = Case((x, y))
                    x, y = moddiv(i * 2 + 1, size)
                    put_playable_case((x, y), char)
                else:
                    put_playable_case((x, y), char)
                    x, y = moddiv(i * 2 + 1, size)
                    self.__board[(x, y)] = Case((x, y))
            total += num


    def get_selected_case(self):
        return next(self.get_cases(lambda c: isinstance(c, PlayableCase) and c.is_selected()), None)

    def get_case(self, coordinates: tuple[int, int]) -> Case | None:
        x, y = coordinates
        if not (0 <= x < self.__size and 0 <= y < self.__size):
            return None
        return self.__board[x, y]

    def get_landing_cases(self):
        return self.get_cases(
            lambda c: isinstance(c, PlayableCase) and c.can_land())

    def get_cases(self, condition):
        return (case for case in self.__board.flatten() if condition(case))

    def get_cases_between_start_and_end(self, start: PlayableCase, end: PlayableCase) -> list[PlayableCase]:
        start_x, start_y = start.get_coordinates()
        end_x, end_y = end.get_coordinates()
        step_x = 1 if end_x > start_x else -1
        step_y = 1 if end_y > start_y else -1

        current_x, current_y = start_x + step_x, start_y + step_y
        result = []

        while (current_x, current_y) != (end_x, end_y):
            result.append(self.get_case((current_x, current_y)))
            current_x += step_x
            current_y += step_y

        return result

    def is_case(self, coordinates: tuple[int, int], condition) -> bool:
        return condition(self.get_case(coordinates))

    def is_valid_move(self, coordinates: tuple[int, int]) -> bool:
        """Vérifie si des coordonnées sont valides pour le plateau."""
        x, y = coordinates
        return 0 <= x < self.__size \
            and 0 <= y < self.__size

    def draw(self, screen: pg.Surface, size: int, offset: int = 0):
        for row in self.__board:
            for case in row:
                case.draw(screen, size, offset)
        self.__draw_arrows(screen, size, offset)

    def __draw_arrows(self, screen: pg.Surface, size: int, offset: int):
        case = self.get_selected_case()
        if case is None:
            return

        cases_can_land = list(self.get_landing_cases())
        for i in range(len(cases_can_land)):
            start_pos = add(mult(case.get_coordinates(), (size + offset)), int(size // 2))
            end_pos = add(mult(cases_can_land[i].get_coordinates(), (size + offset)), int(size // 2))
            pg.draw.line(screen, ARROWS_COLOR, start_pos, end_pos, 3)

    def __repr__(self):
        result = ""
        for case in self.__board.transpose().flatten():
            if isinstance(case, PlayableCase):
                lowercase = case.get_piece().__class__.__name__ == "Piece"
                if case.get_piece() is None:
                    result += '.'
                    continue

                match case.get_piece().get_team():
                    case Team.WHITE:
                        result += 'w' if lowercase else 'W'
                    case Team.BLACK:
                        result += 'b' if lowercase else 'B'
        return factorize_string(result)
