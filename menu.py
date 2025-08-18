import pygame
import constants
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
import main
import random


def show_upgrade_menu(screen):
    print(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
    upgrade_options = random.sample(constants.UPGRADES, 3)
    rects = []
    menu_width = constants.SCREEN_WIDTH / 1.5
    menu_height = constants.SCREEN_HEIGHT / 4
    start_x = (constants.SCREEN_WIDTH - menu_width) // 2
    start_y = (constants.SCREEN_HEIGHT - menu_height) // 2

    for i, upgrade in enumerate(upgrade_options):
        rect = pygame.Rect(start_x + i * (constants.SCREEN_WIDTH / 4), start_y, constants.SCREEN_WIDTH / 6, menu_height)
        rects.append(rect)
        pygame.draw.rect(screen, (20, 180, 180), rect)
        font = pygame.font.SysFont(None, 28 * int(constants.SCALE))
        text = font.render(upgrade, True, (255, 255, 255))
        screen.blit(text, (rect.x + 20 * constants.SCALE, rect.y + menu_height / 2))

    pygame.display.flip()
    return upgrade_options, rects

def handle_upgrade_selection(rects, upgrade_options, player):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        player.apply_upgrade(upgrade_options[i])
                        main.paused = False
                        print("selected")
                        return True  # Upgrade selected
            elif event.type == pygame.QUIT:
                print("quit")
                pygame.quit()
                exit()
        
            pygame.time.delay(10)



