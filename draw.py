import pygame as pg
class Case:
    def __init__(self, coordinates: tuple[int, int], team: bool = None, is_queen: bool = False):
        self.x, self.y = coordinates
        self.team = team
        self.is_queen = is_queen
        self.is_selected = False

        self.color = "#713a36" if self.x + self.y % 2 == 0 else "#ffcb98"

    def draw(self, surface: pg.Surface, size: int) -> None:
        pg.draw.rect(surface, "#713a36", pg.Rect(self.x * (size + OFFSET), self.y * (size + OFFSET), size, size))
