from __future__ import annotations

from typing import TYPE_CHECKING

import pygame as pg

from colors_constants import *
from config import GRID_SIZE
from team import Team

if TYPE_CHECKING:
    from piece import Piece


class Case:
    def __init__(self, coordinates: tuple[int, int]):
        self._x, self._y = coordinates
        self._color = DEFAULT_UNPLAYABLE_COLOR

    def get_coordinates(self) -> tuple[int, int]:
        return self._x, self._y

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        pg.draw.rect(surface, self._color, pg.Rect(self._x * (size + offset), self._y * (size + offset), size, size))

    def __repr__(self) -> str:
        return f"({self.__class__.__name__}({self._x}, {self._y}))"


class PlayableCase(Case):
    def __init__(self, coordinates: tuple[int, int], content: Piece = None):
        super().__init__(coordinates)
        self.__is_selected = False
        self.__can_land = False
        self._color = DEFAULT_PLAYABLE_COLOR
        self.__piece = content

    def get_piece(self) -> Piece:
        return self.__piece

    def set_piece(self, content: Piece | None) -> None:
        self.__piece = content

    def set_selected(self, param: bool) -> None:
        self.__is_selected = param
        self._color = SELECTED_COLOR if param else DEFAULT_PLAYABLE_COLOR

    def set_can_land(self, param: bool) -> None:
        self.__can_land = param

    def contains_piece_of_team(self, team: Team) -> bool:
        return self.__piece is not None and self.__piece.get_team() == team

    def is_selected(self) -> bool:
        return self.__is_selected

    def can_land(self) -> bool:
        return self.__can_land

    def try_promotion(self) -> None:
        from piece import Queen
        if self._y == 0 and self.__piece.get_team() is Team.WHITE:
            self.__piece = Queen(self.__piece.get_team())
        elif self._y == GRID_SIZE - 1 and self.__piece.get_team() is Team.BLACK:
            self.__piece = Queen(self.__piece.get_team())

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        super().draw(surface, size, offset)
        if self.__piece is not None:
            self.__piece.draw(surface, self.get_coordinates(), size, offset)
        elif self.__can_land:
            pg.draw.circle(surface, ARROWS_COLOR,
                           (self._x * (size + offset) + size / 2, self._y * (size + offset) + size / 2), size / 6)

    def __repr__(self) -> str:
        return f"{super().__repr__()} {self.__piece}"
