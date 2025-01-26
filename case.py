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
    def __init__(self, coordinates: tuple[int, int], piece: Piece = None):
        super().__init__(coordinates)
        self._is_selected = False
        self._can_land = False
        self._color = DEFAULT_PLAYABLE_COLOR
        self._piece = piece
        self._move = []

    def get_move(self):
        return self._move

    def get_can_play(self):
        return self._move

    def set_can_play(self, can_play):
        self._move = can_play
        self.update_color()

    def get_piece(self) -> Piece:
        return self._piece

    def set_piece(self, content: Piece | None) -> None:
        self._piece = content

    def set_selected(self, param: bool) -> None:
        self._is_selected = param
        self.update_color()

    def set_can_land(self, param: bool) -> None:
        self._can_land = param

    def contains_piece_of_team(self, team: Team) -> bool:
        return self._piece is not None and self._piece.get_team() == team

    def is_selected(self) -> bool:
        return self._is_selected

    def can_land(self) -> bool:
        return self._can_land

    def try_promotion(self) -> bool:
        from piece import Queen
        if self._y == 0 and self._piece.get_team() is Team.WHITE:
            self._piece = Queen(self._piece.get_team())
            return True
        elif self._y == GRID_SIZE - 1 and self._piece.get_team() is Team.BLACK:
            self._piece = Queen(self._piece.get_team())
            return True
        return False

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        super().draw(surface, size, offset)
        if self._piece is not None:
            self._piece.draw(surface, self.get_coordinates(), size, offset)
        elif self._can_land:
            pg.draw.circle(surface, ARROWS_COLOR,
                           (self._x * (size + offset) + size / 2, self._y * (size + offset) + size / 2), size / 6)


    def __repr__(self) -> str:
        return f"{super().__repr__()} {self._piece}"

    def update_color(self):
        if self.is_selected():
            self._color = SELECTED_COLOR
        elif self._move:
            self._color = CAN_PLAY_COLOR
        else:
            self._color = DEFAULT_PLAYABLE_COLOR
