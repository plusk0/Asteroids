import pygame
import constants
import random
import asyncio


class Menu(pygame.sprite.Sprite):
    
    
    def __init__(self):
        self.fontsize = 32
        self.font = pygame.font.SysFont(None, self.fontsize)
        self.background_color = (0, 0, 0)

    @staticmethod  # I'm aware updating constants like this is some mad spaghetti code, but it mostly works for now
    def update_scale():
        width, height = pygame.display.Info().current_w, pygame.display.Info().current_h
        constants.SCREEN_HEIGHT = height
        constants.SCREEN_WIDTH = width

            

    def select_difficulty(self, screen): #WIP remove redundant functions (upgrade & difficulty)
        difficulty_options = [(0 , "easy"), (1 , "medium"),(2 , "nightmare")]
        rects = []
        menu_width = constants.SCREEN_WIDTH / 1.5
        menu_height = constants.SCREEN_HEIGHT / 4
        start_x = (constants.SCREEN_WIDTH - menu_width) // 2
        start_y = (constants.SCREEN_HEIGHT - menu_height) // 2
        
        for i, difficulty in enumerate(difficulty_options):
            rect = pygame.Rect(start_x + i * (constants.SCREEN_WIDTH / 4), start_y, constants.SCREEN_WIDTH / 6, menu_height)
            rects.append(rect)
            pygame.draw.rect(screen, (20, 180, 180), rect)
            font1 = pygame.font.SysFont(None, self.fontsize * 2 // 3)
            font2 = pygame.font.SysFont(None, self.fontsize)

            text1 = font1.render(f"Press {i + 1}:", True, (255, 255, 255))
            text2 = font2.render(f"{difficulty}", True, (255, 255, 255))
            screen.blit(text1, (rect.x + 20, (rect.y + menu_height / 3) - self.fontsize / 2))
            screen.blit(text2, (rect.x + 20, (rect.y + menu_height / 3) + self.fontsize / 2))
        
        pygame.display.flip()
        return difficulty_options, rects
    
    async def handle_difficulty_selection(self, rects, difficulty_options):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            difficulty_options[i]
                            return True
                elif event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            return False
                        case pygame.K_1:
                            return difficulty_options[0]
                        case pygame.K_2:
                            return difficulty_options[1]
                        case pygame.K_3:
                            return difficulty_options[2]


                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            await asyncio.sleep(0)
    


    def show_upgrade_menu(self, screen):
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
            font1 = pygame.font.SysFont(None, self.fontsize * 2 // 3)
            font2 = pygame.font.SysFont(None, self.fontsize)

            text1 = font1.render(f"Press {i + 1}:", True, (255, 255, 255))
            text2 = font2.render(f"{upgrade}", True, (255, 255, 255))
            screen.blit(text1, (rect.x + 20, (rect.y + menu_height / 3) - self.fontsize / 2))
            screen.blit(text2, (rect.x + 20, (rect.y + menu_height / 3) + self.fontsize / 2))

        pygame.display.flip()
        return upgrade_options, rects

    async def handle_upgrade_selection(self, rects, upgrade_options, player):
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
                            return False
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
            await asyncio.sleep(0)  # Yield control to the browser
            

    def draw(self, screen, player):

        for i in range(player.max_health):
            corner_pos = pygame.Vector2((20 + (20*i)), (20 + (20*i)))
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [255, 200, 200], points)

        for i in range(player.health):
            corner_pos = pygame.Vector2((20 + (20*i)), (20 + (20*i)))
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [255, 0, 0], points)

        for i in range(player.shield):
            corner_pos = pygame.Vector2(((20  + (20*i))), ((50  + (20*i))))
            points = [corner_pos + p for p in player.icon_shape]
            pygame.draw.polygon(screen, [20, 180, 180], points)

        font = pygame.font.SysFont(None, 28)
        text = font.render(f"Score {player.score}", True, (255, 255, 255))
        screen.blit(text, (constants.SCREEN_WIDTH / 2, 10))

    def update(self, screen, player):
        self.draw(screen, player)

    @staticmethod
    async def show_game_over(screen):
        font = pygame.font.SysFont(None, 48)
        text = font.render("GAME OVER!", True, (255, 0, 0))
        screen.fill((0, 0, 0))
        screen.blit(text, (constants.SCREEN_WIDTH // 2 - text.get_width() // 2, constants.SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    return True
            
        
