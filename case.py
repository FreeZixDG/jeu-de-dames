from __future__ import annotations

import pygame as pg
from colors_constants import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from piece import Piece


class Case:
    def __init__(self, coordinates: tuple[int, int]):
        self.__x, self.__y = coordinates
        self._color = DEFAULT_UNPLAYABLE_COLOR

    def get_coordinates(self) -> tuple[int, int]:
        return self.__x, self.__y

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        self.__draw_square(surface, size, offset)

    def __draw_square(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        pg.draw.rect(surface, self._color, pg.Rect(self.__x * (size + offset), self.__y * (size + offset), size, size))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__x}, {self.__y})"


class PlayableCase(Case):
    def __init__(self, coordinates: tuple[int, int], content: Piece = None):
        super().__init__(coordinates)
        self.__is_selected = False
        self.__is_landable = False
        self._color = DEFAULT_PLAYABLE_COLOR
        self.__content = content

    def get_content(self) -> Piece:
        return self.__content

    def set_content(self, content: Piece | None):
        self.__content = content

    def set_selected(self, param: bool):
        self.__is_selected = param
        self._color = SELECTED_COLOR if param else DEFAULT_PLAYABLE_COLOR

    def set_landable(self, param: bool):
        self.__is_landable = param

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        super().draw(surface, size, offset)
        if self.__content is not None:
            self.__content.draw(surface, self.get_coordinates(), size, offset)

    def __repr__(self) -> str:
        return f"{super().__repr__()} {self.__content}"

    def is_selected(self):
        return self.__is_selected

    def is_landable(self):
        return self.__is_landable
