import pygame as pg

from piece import Piece


class Case:
    def __init__(self, coordinates: tuple[int, int], content: Piece = None):
        self.__x, self.__y = coordinates
        self.__is_selected = False

        self.__color = "#713a36" if (self.__x + self.__y) % 2 == 0 else "#ffcb98"

        self.__content = content

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        self.__draw_square(surface, size, offset)

        if self.__content is not None:
            self.__content.draw(surface, (self.__x, self.__y), size, offset)

    def __draw_square(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        pg.draw.rect(surface, self.__color, pg.Rect(self.__x * (size + offset), self.__y * (size + offset), size, size))


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__x}, {self.__y}) {self.__content}"
