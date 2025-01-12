import pygame as pg

from board import Board
from team import Team


class Piece:
    def __init__(self, team: Team):
        self.__team = team

    def get_team(self):
        return self.__team

    def __can_move(self, board: Board, start_pos, end_pos):
        pass

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:

        match self.__team:
            case Team.WHITE:
                color_in = "#DDDDDD"
                color_out = "#333333"
            case Team.BLACK:
                color_in = "#333333"
                color_out = "#DDDDDD"
            case _:
                return

        pg.draw.circle(surface, color_out,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2)
        pg.draw.circle(surface, color_in,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2.2)

    def __repr__(self):
        if self.__team is not None:
            return f"{self.__team.value}"


class Queen(Piece):
    def __init__(self, team: Team):
        super().__init__(team)

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:
        super().draw(surface, location, size)
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
        if self.__team is not None:
            return f"{self.__team.value} Queen"
