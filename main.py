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
        assert (
            0 <= x <= GRID_SIZE[0]
        ), f"Fehler beim Initialiseren von x beim Konstruieren einer Position: {x}"
        assert (
            0 <= y <= GRID_SIZE[1]
        ), f"Fehler beim Initialiseren von y beim Konstruieren einer Position: {y}"
        self.x = x
        self.y = y
        self.color = color

    # Wandelt eine Kästchenposition in eine richtige Pygame Position um
    def to_pygame_pos(self) -> Tuple[int, int]:
        return (self.x * BLOCK_SIZE[0], self.y * BLOCK_SIZE[1])

    # Rendert einen Block mit der angegeben Farbe an der angegeben Position
    def render(self):
        assert self.color != None, f"Render auf {self} gerufen, aber color ist None"
        assert (
            0 <= self.x < GRID_SIZE[0]
        ), f"Render auf {self} gerufen, aber X ist invalid: {self.x}"
        assert (
            0 <= self.y < GRID_SIZE[1]
        ), f"Render auf {self} gerufen, aber Y ist invalid: {self.y}"

        start = self.to_pygame_pos()
        pygame.draw.rect(screen, self.color, (start, BLOCK_SIZE))


# Generiert eine zufällige Kästchenposition
def random_position() -> Position:
    return Position(
        random.randint(0, GRID_SIZE[0] - 1), random.randint(0, GRID_SIZE[1] - 1)
    )

# Position vom Apfel
apple = random_position()
apple.color = (255, 0, 0)  # Rot

def key_listener():
    joystick_x = 0
    joystick_y = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: joystick_y += 1
    if keys[pygame.K_s]: joystick_y -= 1
    if keys[pygame.K_a]: joystick_x -= 1
    if keys[pygame.K_d]: joystick_x += 1
    return (joystick_x, joystick_y)

def render():
    apple.render()

    surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    color = pygame.Color(100, 100, 100, 50)
    #                     r    g    b   alpha wert
    # Die Gridlinien zeichnen
    for x in range(BLOCK_SIZE[0], SCREEN[0], BLOCK_SIZE[0]):
        pygame.draw.line(surface, color, (x, 0), (x, SCREEN[0]))
    for y in range(BLOCK_SIZE[1], SCREEN[1], BLOCK_SIZE[1]):
        pygame.draw.line(surface, color, (0, y), (SCREEN[1], y))
    screen.blit(surface, (0,0))

running = True
while running:
    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            running = False

    render()
    pygame.display.flip()
    screen.fill((30))
