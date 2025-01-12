import pygame as pg

from team import Team


class Case:
    def __init__(self, coordinates: tuple[int, int], team: Team = None, is_queen: bool = False):
        self.__x, self.__y = coordinates
        self.__team = team
        self.__is_queen = is_queen
        self.__is_selected = False

        self.__color = "#713a36" if (self.__x + self.__y) % 2 == 0 else "#ffcb98"

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        self.__draw_square(surface, size, offset)
        self.__draw_piece(surface, size, offset)

    def __draw_piece(self, surface: pg.Surface, size: int, offset: int = 0) -> None:

        match self.__team:
            case Team.WHITE:
                c = "#EEEEEE"
            case Team.BLACK:
                c = "#111111"
            case _:
                return

        pg.draw.circle(surface, c, (self.__x * (size + offset) + size / 2, self.__y * (size + offset) + size / 2),
                       size / 2)

    def __draw_square(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        pg.draw.rect(surface, self.__color, pg.Rect(self.__x * (size + offset), self.__y * (size + offset), size, size))

    def __repr__(self) -> str:
        result = f"{self.__class__.__name__}({self.__x}, {self.__y})"
        if self.__team is not None:
            result += f" ({self.__team.value})"
        if self.__is_queen:
            result += " Queen"
        return result
