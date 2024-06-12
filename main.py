# pyright:strict
import pygame

WIDTH, HEIGHT = 800, 800

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type is pygame.QUIT:
            running = False
