import numpy as np
import pygame

from case import Case


class Board:
    def __init__(self, size: tuple[int, int], init: str = None):
        self.size = size
        self.board = np.zeros(size, dtype=Case)

        for y in range(size[0]):
            for x in range(size[1]):
                if y >= 6:
                    self.board[x, y] = Case((x, y), team=True)
                    continue
                elif y <= 3:
                    self.board[x, y] = Case((x, y), team=False)
                    continue
                self.board[x, y] = Case((x, y))

    def draw(self, screen: pygame.Surface, size: int, offset: int = 0):
        for row in self.board:
            for case in row:
                case.draw(screen, size, offset)

    def getCase(self, coordinates: tuple[int, int]) -> Case:
        return self.board[coordinates[0], coordinates[1]]
