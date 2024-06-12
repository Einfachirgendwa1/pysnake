# pyright:strict
import random
from typing import Optional, Tuple

import pygame

# Size vom erstellten Fenster
SCREEN = 800, 800
GRID_SIZE = 25, 25

BLOCK_SIZE = (SCREEN[0] // GRID_SIZE[0], SCREEN[1] // GRID_SIZE[1])

pygame.init()
screen = pygame.display.set_mode(SCREEN)


# Snake ist ja in Kästchen aufgeteilt, und das ist quasi eine Kästchenposition
class Position:
    def __init__(
        self, x: int, y: int, color: Optional[Tuple[int, int, int]] = None
    ) -> None:
        assert x <= GRID_SIZE[0]
        assert y <= GRID_SIZE[1]
        self.x = x
        self.y = y
        self.color = color

    # Wandelt eine Kästchenposition in eine richtige Pygame Position um
    def to_pygame_pos(self) -> Tuple[int, int]:
        return (self.x * BLOCK_SIZE[0], self.y * BLOCK_SIZE[1])

    # Rendert einen Block mit der angegeben Farbe an der angegeben Position
    def render(self):
        assert self.color != None
        start = self.to_pygame_pos()
        pygame.draw.rect(screen, self.color, (start, BLOCK_SIZE))


# Generiert eine zufällige Kästchenposition
def random_position() -> Position:
    return Position(random.randint(0, GRID_SIZE[0]), random.randint(0, GRID_SIZE[1]))


# Position vom Apfel
apple = random_position()
apple.color = (255, 0, 0)  # Rot


def render():
    apple.render()

    # Die Gridlinien zeichnen
    for x in range(BLOCK_SIZE[0], SCREEN[0], BLOCK_SIZE[0]):
        pygame.draw.line(screen, (255, 255, 255), (x, 0), (x, SCREEN[0]))
    for y in range(BLOCK_SIZE[1], SCREEN[1], BLOCK_SIZE[1]):
        pygame.draw.line(screen, (255, 255, 255), (0, y), (SCREEN[1], y))


running = True
while running:
    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            running = False

    render()
    pygame.display.flip()
    screen.fill((30))
