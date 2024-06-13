import random
from typing import Optional, Tuple
import pygame
import time
import math

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

class snake:
    def __init__(self, length):
        self.head_pos = random_position()
        self.max_length = length
        self.dir = 0
        self.parts = []
        self.color = (0 ,255, 0)

    def move(self):
        dir = key_listener()
        if dir != (self.dir+180)%360 and dir != None:
            self.dir = dir
        self.head_pos.x += math.sin(math.radians(self.dir))
        self.head_pos.y += math.cos(math.radians(self.dir))
        self.parts.append((self.head_pos.x, self.head_pos.y))
        if len(self.parts)>self.max_length:
            self.parts.pop(0)
        global apple
        if self.head_pos.x == apple.x and self.head_pos.y == apple.y:
            apple = random_position()
            apple.color = (255, 0, 0) 
            self.max_length +=1
    
    def render(self):
        for i in self.parts:
            y = i[1]* BLOCK_SIZE[1]
            x = i[0] * BLOCK_SIZE[0] 
            pygame.draw.rect(screen, self.color, ((x,y), BLOCK_SIZE))     


# Position vom Apfel
apple = random_position()
apple.color = (255, 0, 0)  # Rot

a_snake = snake(3)

def key_listener():
    dir = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: dir += 180
    if keys[pygame.K_s]: dir -= 360
    if keys[pygame.K_a]: dir -= 90
    if keys[pygame.K_d]: dir += 90
    if dir != 0:
        return ((dir+360)%360)
    else: 
        return None

def render():
    apple.render()
    a_snake.render()

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
    a_snake.move()
    render()
    pygame.display.flip()
    screen.fill((30))
    time.sleep(0.2)
