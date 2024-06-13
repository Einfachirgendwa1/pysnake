import random
from typing import Callable, List, Literal, Optional, Tuple, Union

import pygame
from pygame.rect import RectType

# Size vom erstellten Fenster
SCREEN = 800, 800
GRID_SIZE = 25, 25

TITLESCREEN_SIZE_MAX = 55
TITLESCREEN_SIZE_MIN = 50
SNAKE_MOVES_PER_SECOND = 7.5

BLOCK_SIZE = (SCREEN[0] // GRID_SIZE[0], SCREEN[1] // GRID_SIZE[1])

mode: Literal["titlescreen", "pausemenu", "game"] = "titlescreen"
titlescreen_size = TITLESCREEN_SIZE_MIN
titlescreen_growing = True

button_checks: List[Tuple[int, int, int, int, Callable]] = []

pygame.init()
screen = pygame.display.set_mode(SCREEN)
pygame.display.set_caption("PySnake", "PySnake")

font = pygame.font.Font(None, 36)


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

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, Position) and self.x == value.x and self.y == value.y

    # Wandelt eine Kästchenposition in eine richtige Pygame Position um
    def to_pygame_pos(self) -> Tuple[int, int]:
        return (self.x * BLOCK_SIZE[0], self.y * BLOCK_SIZE[1])

    def is_valid(self) -> bool:
        return 0 <= self.x < GRID_SIZE[0] and 0 <= self.y < GRID_SIZE[1]

    # Rendert einen Block mit der angegeben Farbe an der angegeben Position
    def render(self):
        assert self.color != None, f"Render auf {self} gerufen, aber color ist None"
        assert (
            self.is_valid()
        ), f"Render auf {self} gerufen, aber die Position ist invalid!"

        start = self.to_pygame_pos()
        pygame.draw.rect(screen, self.color, (start, BLOCK_SIZE))


Direction = Literal["Up", "Down", "Left", "Right"]


# Generiert eine zufällige Kästchenposition
def random_position(
    min=Position(0, 0), max=Position(GRID_SIZE[0] - 1, GRID_SIZE[1] - 1)
) -> Position:
    return Position(random.randint(min.x, max.x), random.randint(min.y, max.y))


class Snake:
    def __init__(self, length: int):
        self.head_pos = random_position(
            min=Position(5, 5),
            max=Position(10, 10),  # Die Snake irgendwo in der Mitte spawnen
        )
        self.max_length = length
        self.direction: Direction = "Down"
        self.parts: List[Position] = []
        self.color = (0, 255, 0)
        self.dead = False

    def check_direction(self):
        key_input = key_listener()
        if key_input != None:
            if (
                (self.direction == "Up" and key_input == "Down")
                or (self.direction == "Down" and key_input == "Up")
                or (self.direction == "Left" and key_input == "Right")
                or (self.direction == "Right" and key_input == "Left")
            ):
                return
            self.direction = key_input

    def move(self):
        match self.direction:
            case "Up":
                self.head_pos.y -= 1
            case "Down":
                self.head_pos.y += 1
            case "Left":
                self.head_pos.x -= 1
            case "Right":
                self.head_pos.x += 1

        if self.head_pos in self.parts or not self.head_pos.is_valid():
            self.dead = True
            return

        self.parts.append(Position(self.head_pos.x, self.head_pos.y, self.color))

        global apple
        if self.head_pos == apple:
            apple = random_position()
            apple.color = (255, 0, 0)
            self.max_length += 1

        if len(self.parts) > self.max_length:
            self.parts.pop(0)

    def render(self):
        for part in self.parts:
            part.render()


def key_listener() -> Optional[Direction]:
    direction = None

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        direction = "Up"
    if keys[pygame.K_s]:
        direction = "Down"
    if keys[pygame.K_a]:
        direction = "Left"
    if keys[pygame.K_d]:
        direction = "Right"

    return direction


# Position vom Apfel
apple = random_position()
apple.color = (255, 0, 0)  # Rot

snake = Snake(3)


def render():
    apple.render()
    snake.render()

    surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    color = pygame.Color(100, 100, 100, 50)
    #                     r    g    b   alpha wert
    # Die Gridlinien zeichnen
    for x in range(BLOCK_SIZE[0], SCREEN[0], BLOCK_SIZE[0]):
        pygame.draw.line(surface, color, (x, 0), (x, SCREEN[0]))
    for y in range(BLOCK_SIZE[1], SCREEN[1], BLOCK_SIZE[1]):
        pygame.draw.line(surface, color, (0, y), (SCREEN[1], y))
    screen.blit(surface, (0, 0))


def draw_text(
    text: str,
    position: Union[
        Tuple[int, int],
        Tuple[Literal["CenteredX", "CenteredY"], int],
        Literal["Centered"],
    ],
    color: Tuple[int, int, int] = (255, 255, 255),
    size: float = 1,
    on_click: Optional[Callable] = None,
):
    text_surface = font.render(text, True, color)
    text_surface = pygame.transform.scale(
        text_surface, [scl * size for scl in text_surface.get_size()]
    )
    result_position: Union[Tuple[int, int], RectType] = (0, 0)
    if position is not Tuple[int, int]:
        center = screen.get_rect().center
        text_rect = text_surface.get_rect(center=center)
        if position == "Centered":
            result_position = text_rect
        else:
            if position[0] == "CenteredX":
                result_position = (text_rect.x, position[1])
            else:
                result_position = (position[1], text_rect.y)
    else:
        result_position = position

    screen.blit(text_surface, result_position)

    if on_click:
        rect = text_surface.get_rect(center=result_position)
        button_checks.append(
            (rect.x, rect.y, rect.x + rect.size[0], rect.y + rect.size[1], on_click)
        )


last_snake_move: Optional[int] = None


def start_game():
    global mode, apple, snake
    print("Starte Spiel")
    mode = "game"

    # Position vom Apfel
    apple = random_position()
    apple.color = (255, 0, 0)  # Rot

    snake = Snake(3)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            for button in button_checks:
                print(f"Mouse: {mouse}\nButton: {button}")
                if (
                    button[0] <= mouse[0] <= button[2]
                    and button[1] <= mouse[1] <= button[3]
                ):
                    button[4]()
            button_checks = []

    match mode:
        case "titlescreen":
            draw_text("PySnake!", ("CenteredX", 100))
            draw_text("Start Game", ("CenteredX", 400), on_click=start_game)

            if titlescreen_growing:
                titlescreen_size += 0.001
                if titlescreen_size > TITLESCREEN_SIZE_MAX:
                    titlescreen_growing = False
            else:
                titlescreen_size -= 0.001
                if titlescreen_size < TITLESCREEN_SIZE_MIN:
                    titlescreen_growing = True

        case "game":
            if (
                not last_snake_move
                or pygame.time.get_ticks() - last_snake_move
                > 1000 / SNAKE_MOVES_PER_SECOND
            ):
                snake.move()
                last_snake_move = pygame.time.get_ticks()

            snake.check_direction()
            render()

            if snake.dead:
                print("Schlange tot :(")
                mode = "titlescreen"

    pygame.display.flip()
    screen.fill((30))
