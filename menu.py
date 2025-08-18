import pygame
from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import main
import random


def show_upgrade_menu(screen):
    # Randomly pick 3 upgrades
    options = random.sample(UPGRADES, 3)
    rects = []
    menu_width = 600
    menu_height = 200
    start_x = (SCREEN_WIDTH - menu_width) // 2
    start_y = (SCREEN_HEIGHT - menu_height) // 2

    # Draw 3 windows
    for i, upgrade in enumerate(options):
        rect = pygame.Rect(start_x + i * 200, start_y, 180, menu_height)
        rects.append(rect)
        pygame.draw.rect(screen, (50, 50, 50), rect)
        font = pygame.font.SysFont(None, 36)
        text = font.render(upgrade, True, (255, 255, 255))
        screen.blit(text, (rect.x + 20, rect.y + 80))

    pygame.display.flip()
    return options, rects

def handle_upgrade_selection(rects, options, player):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        player.apply_upgrade(options[i])
                        main.paused = False
                        print("selected")
                        return True  # Upgrade selected
            elif event.type == pygame.QUIT:
                print("quit")
                pygame.quit()
                exit()
        
            pygame.time.delay(10)



