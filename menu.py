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
        screen = game.actual_screen  # Use actual screen for menu
        
        # Create difficulty menu data
        menu_data = self.ui_manager.create_difficulty_menu(screen)
        
        # Draw the menu
        self.ui_manager.draw_difficulty_menu(screen, menu_data)
        
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

    def show_upgrade_menu(self, game, player=None):
        """Show upgrade selection menu using new UI system"""
        screen = game.actual_screen  # Use actual screen for menu
        if player is None:
            player = game.player if hasattr(game, 'player') else None
        
        # Get available upgrades (including final upgrades), filtering locked ones
        if player and hasattr(player, 'weapon_manager'):
            available_upgrades = player.weapon_manager.get_available_upgrades(player)
        else:
            available_upgrades = constants.UPGRADES + constants.WEAPONS
        
        # Select 3 random upgrades
        upgrade_options = random.sample(available_upgrades, min(3, len(available_upgrades)))
        
        # Create upgrade menu data
        menu_data = self.ui_manager.create_upgrade_menu(screen, upgrade_options, player)
        
        # Draw the menu
        self.ui_manager.draw_upgrade_menu(screen, menu_data, player)
        
        pygame.display.flip()
        
        # Return the rects for handling selection
        rects = []
        for card_data in menu_data["cards"]:
            card_rect = card_data[0]  # First element is the rect
            rects.append(card_rect)
        
        # Also include formation rects if present
        if "formations" in menu_data and menu_data["formations"]:
            for formation_data in menu_data["formations"]:
                formation_rect = formation_data[0]
                rects.append(formation_rect)
        
        return upgrade_options, rects, menu_data.get("formations", [])

    async def handle_upgrade_selection(self, rects, upgrade_options, player, formations=None):
        """Handle upgrade selection with new UI"""
        if formations is None:
            formations = []
        
        # Calculate which rects are for upgrades vs formations
        upgrade_rect_count = len(upgrade_options)
        formation_rects = rects[upgrade_rect_count:]
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(mouse_pos):
                            if i < upgrade_rect_count:
                                # Regular upgrade
                                player.apply_upgrade(upgrade_options[i])
                                return True
                            else:
                                # Formation selection
                                formation_index = i - upgrade_rect_count
                                if formation_index < len(formations):
                                    formation_name = formations[formation_index][1]
                                    self.handle_formation_selection(player, formation_name)
                                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return False
                    elif event.key == pygame.K_1 and len(upgrade_options) >= 1:
                        player.apply_upgrade(upgrade_options[0])
                        return True
                    elif event.key == pygame.K_2 and len(upgrade_options) >= 2:
                        player.apply_upgrade(upgrade_options[1])
                        return True
                    elif event.key == pygame.K_3 and len(upgrade_options) >= 3:
                        player.apply_upgrade(upgrade_options[2])
                        return True
                    # Formation hotkeys (4,5,6)
                    elif event.key == pygame.K_4 and len(formations) >= 1:
                        self.handle_formation_selection(player, formations[0][1])
                        return True
                    elif event.key == pygame.K_5 and len(formations) >= 2:
                        self.handle_formation_selection(player, formations[1][1])
                        return True
                    elif event.key == pygame.K_6 and len(formations) >= 3:
                        self.handle_formation_selection(player, formations[2][1])
                        return True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            await asyncio.sleep(0)
    
    def handle_formation_selection(self, player, formation_name):
        """Handle formation selection for wingmen"""
        if not player or not hasattr(player, 'weapon_manager'):
            return
        
        wingmen = getattr(player.weapon_manager, 'wingmen', None)
        if not wingmen or not wingmen.formations_unlocked:
            return
        
        # Map formation names to IDs
        formation_map = {
            "Scouting": constants.WINGMEN_FORMATION_SCOUTING,
            "Close Follow": constants.WINGMEN_FORMATION_CLOSE_FOLLOW,
            "Radar Follow": constants.WINGMEN_FORMATION_RADAR_FOLLOW,
        }
        
        formation_id = formation_map.get(formation_name)
        if formation_id is not None:
            wingmen.set_formation(formation_id)

    async def show_game_over(self, game):
        """Show game over menu using new UI system"""
        screen = game.actual_screen  # Use actual screen for menu
        player = getattr(game, 'player', None)
        # Also check if player is stored in the menu instance
        if player is None and hasattr(self, 'player'):
            player = self.player
        
        # Create game over menu data
        menu_data = self.ui_manager.create_game_over_menu(screen, player)
        
        # Draw the menu
        self.ui_manager.draw_game_over_menu(screen, menu_data)
        
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
        # Update UI manager screen dimensions
        if screen.get_size() != (self.ui_manager.screen_width, self.ui_manager.screen_height):
            self.ui_manager.update_screen_dimensions(screen.get_width(), screen.get_height())
        self.draw(screen, player)

    def draw_starry_background(self, screen):
        """Draw starry background helper"""
        self.ui_manager.draw_starry_background(screen)