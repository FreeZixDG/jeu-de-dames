import pygame as pg

from team import Team


class Piece:
    def __init__(self, team: Team, is_queen: bool = False):
        self.__team = team
        self.__is_queen = is_queen

    def get_team(self):
        return self.__team

    def is_queen(self):
        return self.__is_queen

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:

        match self.__team:
            case Team.WHITE:
                c = "#DDDDDD"
            case Team.BLACK:
                c = "#333333"
            case _:
                return

        pg.draw.circle(surface, c, (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2),
                       size / 2.2)

        if self.__is_queen:
            self.__draw_queen(surface, location, size, offset)

    def __draw_queen(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:
        match self.__team:
            case Team.WHITE:
                c = "#333333"
            case Team.BLACK:
                c = "#DDDDDD"
            case _:
                return

        pg.draw.circle(surface, c, (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2),
                       size / 6)

    def __repr__(self):
        result = "("
        if self.__team is not None:
            result += f"{self.__team.value}"
        if self.__is_queen:
            result += " Queen"
        return result + ")"
