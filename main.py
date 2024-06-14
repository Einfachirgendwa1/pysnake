import os
import random
from typing import Callable, List, Literal, Optional, Tuple, Union, cast

import pygame
from pygame.rect import RectType

# Size vom erstellten Fenster
WINDOW = 800, 1000
SCREEN = 800, 900
WINDOW_SCREEN_OFFSET = (0, 100)
GRID_SIZE = 25, 25

SNAKE_MOVES_PER_SECOND = 5
TITLESCREEN_SIZE_MAX = 55
TITLESCREEN_SIZE_MIN = 50
SNAKE_COLOR = (166, 227, 161)
APPLE_COLOR = (243, 139, 168)
BACKGROUND_COLOR = (30, 30, 46)
MAX_FPS = 169

BLOCK_SIZE = (SCREEN[0] // GRID_SIZE[0], SCREEN[1] // GRID_SIZE[1])

mode: Literal["titlescreen", "pausemenu", "game"] = "titlescreen"
titlescreen_size = TITLESCREEN_SIZE_MIN
titlescreen_growing = True
score = 0
fontsize = 36
pause_drawn = False
pause_pressed = False

button_checks: List["Button"] = []

pygame.init()
screen = pygame.display.set_mode(WINDOW)
pygame.display.set_caption("PySnake", "PySnake")
icon = pygame.image.load("PySnake_icon.png")
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

font = pygame.font.Font(None, fontsize)


def save_highscore():
    with open("highscore.txt", "w") as file:
        file.write(str(highscore))


def load_highscore() -> int:
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as file:
            val = file.read()
            if val.isdigit():
                return int(val)
    return 0


highscore = load_highscore()


def genfont():
    global font
    font = pygame.font.Font(None, fontsize)


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
        return (
            self.x * BLOCK_SIZE[0] + WINDOW_SCREEN_OFFSET[0],
            self.y * BLOCK_SIZE[1] + WINDOW_SCREEN_OFFSET[1],
        )

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
        self.color = SNAKE_COLOR
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

        global apple, score
        if self.head_pos == apple:
            apple = random_position()
            apple.color = self.color
            while apple in self.parts:
                apple = random_position()
                apple.color = self.color
            apple.color = APPLE_COLOR
            self.max_length += 1
            score += 1

        if len(self.parts) > self.max_length:
            self.parts.pop(0)

    def render(self):
        for part in self.parts:
            part.render()


class Coordinate:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_tuple(cls, data: tuple[float, float]):
        return cls(data[0], data[1])

    def inside(self, start: "Coordinate", end: "Coordinate"):
        return start.x <= self.x <= end.x and start.y <= self.y <= end.y


class Button:
    def __init__(
        self, start: Tuple[float, float], end: Tuple[float, float], callback: Callable
    ) -> None:
        self.start = Coordinate.from_tuple(start)
        self.end = Coordinate.from_tuple(end)
        self.callback = callback

    def is_clicked(self):
        mouse = Coordinate.from_tuple(pygame.mouse.get_pos())
        return mouse.inside(self.start, self.end)

    def handle(self):
        if self.is_clicked():
            self.callback()


def key_listener() -> Optional[Direction]:
    direction = None
    global mode, pause_drawn, pause_pressed

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        direction = "Up"
    if keys[pygame.K_s]:
        direction = "Down"
    if keys[pygame.K_a]:
        direction = "Left"
    if keys[pygame.K_d]:
        direction = "Right"

    if keys[pygame.K_ESCAPE] or keys[pygame.K_p]:
        if not pause_pressed:
            if mode != "pausemenu":
                mode = "pausemenu"
                pause_drawn = False
            else:
                mode = "game"
                pause_drawn = True
            pause_pressed = True
    else:
        pause_pressed = False

    return direction


# Position vom Apfel
apple = random_position()
apple.color = APPLE_COLOR

snake = Snake(3)


def render():
    apple.render()
    snake.render()

    surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    color = pygame.Color(100, 100, 100, 75)
    #                     r    g    b   alpha wert

    # Die Gridlinien zeichnen
    for x in range(BLOCK_SIZE[0], SCREEN[0], BLOCK_SIZE[0]):
        x += WINDOW_SCREEN_OFFSET[0]
        pygame.draw.line(
            surface,
            color,
            (x, WINDOW_SCREEN_OFFSET[1]),
            (x, WINDOW_SCREEN_OFFSET[1] + SCREEN[1]),
        )
    for y in range(BLOCK_SIZE[1], SCREEN[1], BLOCK_SIZE[1]):
        y += WINDOW_SCREEN_OFFSET[1]
        pygame.draw.line(
            surface,
            color,
            (WINDOW_SCREEN_OFFSET[0], y),
            (WINDOW_SCREEN_OFFSET[0] + SCREEN[0], y),
        )
    color = (147, 153, 178)
    pygame.draw.line(
        surface,
        color,
        WINDOW_SCREEN_OFFSET,
        (WINDOW_SCREEN_OFFSET[0] + SCREEN[0], WINDOW_SCREEN_OFFSET[1]),
    )
    pygame.draw.line(
        surface,
        color,
        WINDOW_SCREEN_OFFSET,
        (WINDOW_SCREEN_OFFSET[0], WINDOW_SCREEN_OFFSET[1] + SCREEN[1]),
    )
    pygame.draw.line(
        surface,
        color,
        (WINDOW_SCREEN_OFFSET[0] + SCREEN[0], WINDOW_SCREEN_OFFSET[1]),
        (WINDOW_SCREEN_OFFSET[0] + SCREEN[0], WINDOW_SCREEN_OFFSET[1] + SCREEN[1]),
    )
    pygame.draw.line(
        surface,
        color,
        (WINDOW_SCREEN_OFFSET[0], WINDOW_SCREEN_OFFSET[1] + SCREEN[1]),
        (WINDOW_SCREEN_OFFSET[0] + SCREEN[0], WINDOW_SCREEN_OFFSET[1] + SCREEN[1]),
    )
    screen.blit(surface, (0, 0))

    draw_text(f"Score: {score}", (10, 10))
    draw_text(f"Highscore: {highscore}", (10, 35))


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
    global fontsize
    fontsize_old = fontsize
    fontsize *= size
    fontsize = round(fontsize)
    genfont()
    text_surface = font.render(text, True, color)
    fontsize = fontsize_old
    genfont()
    result_position: Union[Tuple[int, int], RectType] = (0, 0)
    if isinstance(position, tuple) and isinstance(position[0], int):
        result_position = cast(Tuple[int, int], position)
    else:
        center = screen.get_rect().center
        text_rect = text_surface.get_rect(center=center)
        if position == "Centered":
            result_position = text_rect
        else:
            if position[0] == "CenteredX":
                result_position = (text_rect.x, position[1])
            else:
                result_position = (position[1], text_rect.y)

    screen.blit(text_surface, result_position)

    if on_click:
        rect = text_surface.get_rect(center=result_position)

        button_checks.append(
            Button(
                (rect.x + rect.size[0] * 0.5, rect.y + rect.size[1] * 0.5),
                (rect.x + rect.size[0] * 1.5, rect.y + rect.size[1] * 1.5),
                on_click,
            )
        )


last_snake_move: Optional[int] = None


def start_game():
    global mode, apple, snake
    global fontsize

    if mode == "game":
        return
    print("Starte Spiel")
    mode = "game"

    # Position vom Apfel
    apple = random_position()
    apple.color = APPLE_COLOR

    fontsize = 30
    genfont()

    snake = Snake(3)


def quit_game():
    global running
    running = False
    post_game_score_setting()
    save_highscore()


def post_game_score_setting():
    global score, highscore

    if score > highscore:
        highscore = score
        print("Highscore!")
        save_highscore()
    score = 0


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()
            for button in button_checks:
                button.handle()
            button_checks = []

    match mode:
        case "titlescreen":
            draw_text("PySnake!", ("CenteredX", 100), size=2)
            draw_text(f"Highscore: {highscore}", (10, 150), color=(137, 180, 250))
            draw_text("Start Game", ("CenteredX", 400), on_click=start_game)
            draw_text(
                "Quit Game", ("CenteredX", 450), on_click=quit_game, color=APPLE_COLOR
            )

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

            color = SNAKE_COLOR if score > highscore else (255, 255, 255)
            draw_text(f"Score: {score}", (10, 10), color=color)
            draw_text(f"Highscore: {highscore}", (10, 35))

            if snake.dead:
                print("Schlange tot :(")
                post_game_score_setting()
                mode = "titlescreen"
                fontsize = 36
                genfont()

        case "pausemenu":
            render()
            draw_text("Pause", "Centered")
            pygame.display.flip()
            key_listener()

    pygame.display.flip()
    screen.fill(BACKGROUND_COLOR)
    clock.tick(MAX_FPS)
