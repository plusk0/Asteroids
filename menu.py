import pygame
import constants
import random
import asyncio
from ui import UIManager, Colors


class Menu:
    def __init__(self):
        self.ui_manager = UIManager(constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT)
        self.fontsize = 32
        self.font = pygame.font.SysFont(None, self.fontsize)
        self.background_color = (0, 0, 0)

    def select_difficulty(self, game):
        """Show difficulty selection menu using new UI system"""
        screen = game.screen
        
        # Create difficulty menu data
        menu_data = self.ui_manager.create_difficulty_menu(screen)
        
        # Draw the menu
        self.ui_manager.draw_difficulty_menu(screen, menu_data)
        
        game.actual_screen.blit(
            pygame.transform.scale(game.screen, game.actual_screen.get_rect().size), 
            (0, 0)
        )
        pygame.display.flip()
        
        # Return the rects and difficulty options for handling selection
        # menu_data["cards"] contains tuples of (rect, diff_info)
        rects = []
        difficulty_options = []
        
        for rect, diff in menu_data["cards"]:
            rects.append(rect)
            difficulty_options.append(diff["id"])
        
        return difficulty_options, rects

    async def handle_difficulty_selection(self, rects, difficulty_options):
        """Handle difficulty selection with new UI"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Scale mouse position to match the game screen
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse_pos):
                            return difficulty_options[i], True
                    # Check for back button (if present)
                    return None, False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None, False
                    elif event.key == pygame.K_1:
                        return difficulty_options[0], True
                    elif event.key == pygame.K_2:
                        return difficulty_options[1], True
                    elif event.key == pygame.K_3:
                        return difficulty_options[2], True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            await asyncio.sleep(0)

    def show_upgrade_menu(self, game):
        """Show upgrade selection menu using new UI system"""
        screen = game.screen
        player = game.player if hasattr(game, 'player') else None
        
        # Get upgrade options
        upgrade_options = random.sample(constants.UPGRADES + constants.WEAPONS, 3)
        
        # Create upgrade menu data
        menu_data = self.ui_manager.create_upgrade_menu(screen, upgrade_options, player)
        
        # Draw the menu
        self.ui_manager.draw_upgrade_menu(screen, menu_data, player)
        
        game.actual_screen.blit(
            pygame.transform.scale(game.screen, game.actual_screen.get_rect().size), 
            (0, 0)
        )
        pygame.display.flip()
        
        # Return the rects for handling selection
        rects = []
        for card_data in menu_data["cards"]:
            card_rect = card_data[0]  # First element is the rect
            rects.append(card_rect)
        
        return upgrade_options, rects

    async def handle_upgrade_selection(self, rects, upgrade_options, player):
        """Handle upgrade selection with new UI"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse_pos):
                            player.apply_upgrade(upgrade_options[i])
                            return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_1:
                        player.apply_upgrade(upgrade_options[0])
                        return True
                    elif event.key == pygame.K_2:
                        player.apply_upgrade(upgrade_options[1])
                        return True
                    elif event.key == pygame.K_3:
                        player.apply_upgrade(upgrade_options[2])
                        return True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            await asyncio.sleep(0)

    async def show_game_over(self, game):
        """Show game over menu using new UI system"""
        screen = game.screen
        player = getattr(game, 'player', None)
        # Also check if player is stored in the menu instance
        if player is None and hasattr(self, 'player'):
            player = self.player
        
        # Create game over menu data
        menu_data = self.ui_manager.create_game_over_menu(screen, player)
        
        # Draw the menu
        self.ui_manager.draw_game_over_menu(screen, menu_data)
        
        game.actual_screen.blit(
            pygame.transform.scale(game.screen, game.actual_screen.get_rect().size), 
            (0, 0)
        )
        pygame.display.flip()
        
        # Handle menu selection
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = event.pos
                        # Scale mouse position to match the game screen
                        scale_x = game.screen.get_width() / game.actual_screen.get_width()
                        scale_y = game.screen.get_height() / game.actual_screen.get_height()
                        scaled_pos = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)
                        
                        if menu_data["restart"].collidepoint(scaled_pos):
                            return True
                        elif menu_data["menu"].collidepoint(scaled_pos):
                            return False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return False
                        elif event.key == pygame.K_r or event.key == pygame.K_SPACE:
                            return True
            await asyncio.sleep(0)

    def draw(self, screen, player):
        """Draw basic HUD elements - this is being replaced by new UI"""
        # This method is kept for backward compatibility but should use new UI
        self.ui_manager.draw_hud(screen, player)

    def update(self, screen, player):
        """Update and draw the HUD"""
        self.draw(screen, player)

    def draw_starry_background(self, screen):
        """Draw starry background helper"""
        self.ui_manager.draw_starry_background(screen)