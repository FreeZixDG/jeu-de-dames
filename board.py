import numpy as np
import pygame

from case import Case
from team import Team


class Board:
    def __init__(self, size: tuple[int, int], init: str = None):
        self.__size = size
        self.__board = np.zeros(size, dtype=Case)

        for y in range(size[0]):
            for x in range(size[1]):
                if y >= 6:
                    self.__board[x, y] = Case((x, y), team=Team.WHITE)
                    continue
                elif y <= 3:
                    self.__board[x, y] = Case((x, y), team=Team.BLACK)
                    continue

                if y == 4:  # Test a supprimer
                    self.__board[x, y] = Case((x, y), team=Team.BLACK, is_queen=True)
                    continue

                self.__board[x, y] = Case((x, y))

    def draw(self, screen: pygame.Surface, size: int, offset: int = 0):
        for row in self.__board:
            for case in row:
                case.draw(screen, size, offset)

    def getCase(self, coordinates: tuple[int, int]) -> Case:
        return self.__board[coordinates[0], coordinates[1]]
