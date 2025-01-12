import pygame as pg


class Case:
    def __init__(self, coordinates: tuple[int, int], team: bool = None, is_queen: bool = False):
        self.x, self.y = coordinates
        self.team = team
        self.is_queen = is_queen
        self.is_selected = False

        self.color = "#713a36" if (self.x + self.y) % 2 == 0 else "#ffcb98"

    def draw(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        self.draw_square(surface, size, offset)
        self.draw_piece(surface, size, offset)

    def draw_piece(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        if self.team is None:
            return

        if self.team:
            c = "#EEEEEE"
        else:
            c = "#111111"

        pg.draw.circle(surface, c, (self.x * (size + offset) + size / 2, self.y * (size + offset) + size / 2), size / 2)

    def draw_square(self, surface: pg.Surface, size: int, offset: int = 0) -> None:
        pg.draw.rect(surface, self.color, pg.Rect(self.x * (size + offset), self.y * (size + offset), size, size))

    def __repr__(self) -> str:
        result = f"{self.__class__.__name__}({self.x}, {self.y})"
        if self.team is not None:
            result += f" ({self.team})"
        if self.is_queen:
            result += " Queen"
        return result
