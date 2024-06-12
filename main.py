# pyright:strict
import random
from typing import Tuple

import pygame

# HALLLOOOOOOOOOO
# HI
# Size vom erstellten Fenster
SCREEN = 800, 800
GRID_SIZE = 25, 25

BLOCK_SIZE = (SCREEN[0] // GRID_SIZE[0], SCREEN[1] // GRID_SIZE[1])


# Snake ist ja in Kästchen aufgeteilt, und das ist quasi eine Kästchenposition
class Position:
    def __init__(self, x: int, y: int) -> None:
        assert x <= GRID_SIZE[0]
        assert y <= GRID_SIZE[1]
        self.x = x
        self.y = y

    def to_pygame_pos(self) -> Tuple[int, int]:
        return (self.x * BLOCK_SIZE[0], self.y * BLOCK_SIZE[1])


# Generiert eine zufällige Kästchenposition
def random_position() -> Position:
    return Position(random.randint(0, GRID_SIZE[0]), random.randint(0, GRID_SIZE[1]))


# Position vom Apfel
apple_position = random_position()

pygame.init()
screen = pygame.display.set_mode(SCREEN)

running = True
while running:
    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            running = False
