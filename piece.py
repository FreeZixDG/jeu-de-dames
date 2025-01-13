import pygame as pg

from team import Team


class Piece:
    def __init__(self, team: Team):
        self.__team = team

        match self.__team:
            case Team.WHITE:
                self._color_in = "#DDDDDD"
                self._color_out = "#333333"
            case Team.BLACK:
                self._color_in = "#333333"
                self._color_out = "#DDDDDD"
            case _:
                return

    def get_team(self):
        return self.__team

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:

        pg.draw.circle(surface, self._color_out,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2)
        pg.draw.circle(surface, self._color_in,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 2.2)

    def __repr__(self):
        if self.__team is not None:
            return f"{self.__team.value}"


class Queen(Piece):
    def __init__(self, team: Team):
        super().__init__(team)

    def draw(self, surface: pg.Surface, location: tuple[int, int], size: int, offset: int = 0) -> None:
        super().draw(surface, location, size, offset)
        pg.draw.circle(surface, self._color_out,
                       (location[0] * (size + offset) + size / 2, location[1] * (size + offset) + size / 2), size / 6)

    def __repr__(self):
        if self.get_team() is not None:
            return f"{self.get_team().value} Queen"
