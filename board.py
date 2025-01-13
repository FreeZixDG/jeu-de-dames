from typing import Any

import numpy as np
import pygame

from case import Case, PlayableCase
from piece import Piece, Queen
from team import Team


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

    def draw(self, screen: pygame.Surface, size: int, offset: int = 0):
        for row in self.__board:
            for case in row:
                case.draw(screen, size, offset)

    def get_case(self, coordinates: tuple[int, int]) -> np.ndarray[tuple[int, int], np.dtype[Case]] | None:
        x, y = coordinates
        if not (0 <= x < self.__size[0] and 0 <= y < self.__size[1]):
            return None
        return self.__board[x, y]
