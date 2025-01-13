from __future__ import annotations

import pygame as pg
from team import Team

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board

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

    def get_valid_moves(self, board: Board, current_position: tuple[int, int]) -> list[tuple[int, int]]:
        x, y = current_position
        potential_moves = []

        # Exemples pour un mouvement de type pièce standard (jeux de dames) :
        if self.__team == Team.WHITE:
            potential_moves.extend([(x - 1, y - 1), (x + 1, y - 1)])  # Diagonales haut pour blanc
        elif self.__team == Team.BLACK:
            potential_moves.extend([(x - 1, y + 1), (x + 1, y + 1)])  # Diagonales bas pour noir

        # Filtrer pour enlever les mouvements hors du plateau ou avec une case non vide.
        valid_moves = [
            pos for pos in potential_moves
            if board.is_valid_move(pos)  # À implémenter dans Board
        ]
        return valid_moves

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
