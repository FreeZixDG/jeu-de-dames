import numpy as np
import pygame

from case import Case
from piece import Piece
from team import Team


class Board:
    def __init__(self, size: tuple[int, int], init: str = None):
        self.__size = size
        self.__board = np.zeros(size, dtype=Case)

        for y in range(size[0]):
            for x in range(size[1]):
                if y >= 6:
                    self.__board[x, y] = Case((x, y), content=Piece(Team.WHITE))
                    continue
                elif y <= 3:
                    self.__board[x, y] = Case((x, y), content=Piece(Team.BLACK))
                    continue

                if x == 4 and y == 4:
                    self.__board[x, y] = Case((x, y), content=Piece(Team.BLACK, is_queen=True))
                    continue

                self.__board[x, y] = Case((x, y))

    def draw(self, screen: pygame.Surface, size: int, offset: int = 0):
        for row in self.__board:
            for case in row:
                case.draw(screen, size, offset)

    def getCase(self, coordinates: tuple[int, int]) -> Case:
        x, y = coordinates
        if not (0 <= x < self.__size[0] and 0 <= y < self.__size[1]):
            return None
        return self.__board[x, y]
