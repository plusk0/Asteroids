import pygame
import constants
import random


class Menu(pygame.sprite.Sprite):

    @staticmethod
    def update_scale(x):
        if constants.SCALE == 1:
            width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
            constants.SCALE = width / constants.SCREEN_WIDTH

        constants.ASTEROID_MAX_RADIUS = constants.ASTEROID_MAX_RADIUS * constants.SCALE
        constants.ASTEROID_MIN_RADIUS = constants.ASTEROID_MIN_RADIUS * constants.SCALE
        constants.PLAYER_RADIUS = constants.PLAYER_RADIUS * constants.SCALE
        constants.SHOT_RADIUS = constants.SHOT_RADIUS * constants.SCALE

        constants.SCREEN_HEIGHT = height
        constants.SCREEN_WIDTH = width

        constants.PLAYER_SPEED = constants.PLAYER_SPEED * constants.SCALE
        constants.SHOT_SPEED = constants.PLAYER_SPEED * constants.SCALE

    

    def show_upgrade_menu(screen):
        upgrade_options = random.sample(constants.UPGRADES + constants.WEAPONS, 3)
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
                            return True
                elif event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return False  # Skip upgrade
                        case pygame.K_1:
                            player.apply_upgrade(upgrade_options[0])
                            return True
                        case pygame.K_2:
                            player.apply_upgrade(upgrade_options[1])
                            return True
                        case pygame.K_3:
                            player.apply_upgrade(upgrade_options[2])
                            return True

                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            
                pygame.time.delay(10)


    def draw(screen, player):

        for i in range(player.max_health):
            corner_pos = pygame.Vector2((20 + (20*i)) * constants.SCALE, (20 + (20*i)) * constants.SCALE)
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [255, 200, 200], points)

        for i in range(player.health):
            corner_pos = pygame.Vector2((20 + (20*i)) * constants.SCALE, (20 + (20*i)) * constants.SCALE)
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [255, 0, 0], points)

        for i in range(player.shield):
            corner_pos = pygame.Vector2(((20  + (20*i)) * constants.SCALE), ((50  + (20*i)) * constants.SCALE))
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [20, 180, 180], points)

        font = pygame.font.SysFont(None, 28 * int(constants.SCALE))
        text = font.render(f"Score {player.score}", True, (255, 255, 255))
        screen.blit(text, (constants.SCREEN_WIDTH / 2, 100))

    def update(screen, player):
        Menu.draw(screen, player)

    def level_up(screen, player):
        options, rects = Menu.show_upgrade_menu(screen)
        Menu.handle_upgrade_selection(rects, options, player)

    @staticmethod
    def show_game_over(screen, player):
        font = pygame.font.SysFont(None, 48 * int(constants.SCALE))
        text = font.render("GAME OVER!", True, (255, 0, 0))
        screen.fill((0, 0, 0))
        screen.blit(text, (constants.SCREEN_WIDTH // 2 - text.get_width() // 2, constants.SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
            pygame.time.delay(50)
        return True
