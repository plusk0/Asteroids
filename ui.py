import pygame
import constants
import math
import asyncio
import random


class Colors:
    PRIMARY = (100, 200, 255)
    SECONDARY = (200, 100, 255)
    ACCENT = (255, 200, 100)
    SUCCESS = (100, 255, 100)
    DANGER = (255, 100, 100)
    WARNING = (255, 200, 100)
    INFO = (100, 200, 255)
    
    BACKGROUND = (10, 15, 25)
    SURFACE = (25, 35, 50)
    SURFACE_HOVER = (40, 55, 75)
    SURFACE_ACTIVE = (60, 80, 100)
    
    TEXT = (240, 240, 240)
    TEXT_MUTED = (150, 160, 170)
    TEXTBRIGHT = (255, 255, 255)


class UIManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_regular = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.transition_alpha = 0
        self.animation_speed = 8
        
    def draw_rounded_rect(self, screen, color, rect, radius=15, width=0):
        """Draw a rounded rectangle"""
        if width == 0:
            pygame.draw.rect(screen, color, rect, width=0, border_radius=radius)
        else:
            pygame.draw.rect(screen, color, rect, width=width, border_radius=radius)
    
    def draw_glow_rect(self, screen, color, rect, radius=15, glow_size=5):
        """Draw a glowing rectangle"""
        for i in range(glow_size, 0, -1):
            alpha = 50 * (i / glow_size)
            glow_color = (*color, alpha)
            glow_rect = rect.inflate(i * 2, i * 2)
            s = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, glow_color, s.get_rect(), width=0, border_radius=radius + i)
            screen.blit(s, glow_rect.topleft)
        pygame.draw.rect(screen, color, rect, width=0, border_radius=radius)
    
    def draw_button(self, screen, text, rect, action=None, selected=False, disabled=False):
        """Draw a modern button with hover effects"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_over = rect.collidepoint(mouse_pos)
        
        # Determine button state
        if disabled:
            base_color = Colors.SURFACE
            text_color = Colors.TEXT_MUTED
            glow = False
        elif selected:
            base_color = Colors.SURFACE_ACTIVE
            text_color = Colors.TEXTBRIGHT
            glow = True
        elif mouse_over:
            base_color = Colors.SURFACE_HOVER
            text_color = Colors.TEXTBRIGHT
            glow = True
        else:
            base_color = Colors.SURFACE
            text_color = Colors.TEXT
            glow = False
        
        # Draw glow if needed
        if glow:
            self.draw_glow_rect(screen, Colors.PRIMARY, rect, radius=12, glow_size=3)
        else:
            pygame.draw.rect(screen, base_color, rect, width=0, border_radius=12)
            pygame.draw.rect(screen, Colors.PRIMARY, rect, width=2, border_radius=12)
        
        # Draw text
        font = self.font_regular
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
        
        return mouse_over
    
    def draw_card(self, screen, title, description, rect, icon=None, selected=False, rarity="common"):
        """Draw a card for upgrades/items"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_over = rect.collidepoint(mouse_pos)
        
        # Determine colors based on rarity and state
        rarity_colors = {
            "common": {"border": Colors.TEXT_MUTED, "glow": Colors.TEXT_MUTED},
            "uncommon": {"border": Colors.INFO, "glow": Colors.INFO},
            "rare": {"border": Colors.WARNING, "glow": Colors.WARNING},
            "epic": {"border": Colors.SECONDARY, "glow": Colors.SECONDARY},
            "weapon": {"border": Colors.DANGER, "glow": Colors.DANGER},
        }
        colors = rarity_colors.get(rarity, rarity_colors["common"])
        
        # Draw background
        bg_color = Colors.SURFACE
        if selected:
            bg_color = Colors.SURFACE_ACTIVE
        elif mouse_over:
            bg_color = Colors.SURFACE_HOVER
            
        pygame.draw.rect(screen, bg_color, rect, width=0, border_radius=15)
        
        # Draw border with glow if selected or hovered
        if selected or mouse_over:
            self.draw_glow_rect(screen, colors["glow"], rect, radius=15, glow_size=4)
        else:
            pygame.draw.rect(screen, colors["border"], rect, width=2, border_radius=15)
        
        # Draw icon if provided
        if icon:
            icon_rect = pygame.Rect(rect.x + 20, rect.y + 20, 40, 40)
            pygame.draw.circle(screen, colors["border"], icon_rect.center, icon_rect.width // 2)
            # Draw icon symbol
            if icon == "multishot":
                # Draw multiple bullets
                for i in range(3):
                    offset = pygame.Vector2(-10 + i * 10, 0)
                    pygame.draw.circle(screen, Colors.TEXTBRIGHT, 
                                      icon_rect.center + offset, 4)
            elif icon == "shield":
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, icon_rect.width // 2 - 8)
            elif icon == "heart":
                # Simple heart shape
                points = [
                    icon_rect.center + pygame.Vector2(0, -8),
                    icon_rect.center + pygame.Vector2(-7, 3),
                    icon_rect.center + pygame.Vector2(0, 8),
                    icon_rect.center + pygame.Vector2(7, 3)
                ]
                pygame.draw.polygon(screen, (255, 50, 100), points)
            elif icon == "piercing":
                pygame.draw.line(screen, Colors.TEXTBRIGHT,
                                icon_rect.center + pygame.Vector2(-10, 0),
                                icon_rect.center + pygame.Vector2(10, 0), 2)
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center + pygame.Vector2(10, 0), 3)
            elif icon == "rapid":
                for i in range(3):
                    pygame.draw.circle(screen, Colors.TEXTBRIGHT,
                                      icon_rect.center + pygame.Vector2(-10 + i * 10, -5 + i * 5), 3)
            elif icon == "bigger":
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, 6)
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, 12, 1)
            elif icon == "rotator":
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, 10, 2)
                for i in range(4):
                    angle = i * 90
                    pos = icon_rect.center + pygame.Vector2(0, -15).rotate(angle)
                    pygame.draw.circle(screen, Colors.TEXTBRIGHT, pos, 3)
            elif icon == "emp":
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, 12)
                pygame.draw.circle(screen, Colors.TEXTBRIGHT, icon_rect.center, 8, 1)
            elif icon == "laser":
                pygame.draw.line(screen, Colors.TEXTBRIGHT,
                                icon_rect.center + pygame.Vector2(-12, 0),
                                icon_rect.center + pygame.Vector2(12, 0), 3)
        
        # Draw title
        title_font = self.font_regular
        title_surf = title_font.render(title, True, Colors.TEXTBRIGHT)
        title_rect = title_surf.get_rect(midtop=(rect.centerx, rect.y + 20))
        if icon:
            title_rect.x = rect.x + 70
        screen.blit(title_surf, title_rect)
        
        # Draw description
        desc_font = self.font_small
        desc_surf = desc_font.render(description, True, Colors.TEXT_MUTED)
        desc_rect = desc_surf.get_rect(midtop=(rect.centerx, title_rect.bottom + 10))
        if icon:
            desc_rect.x = rect.x + 70
            desc_rect.y = title_rect.y + 35
        screen.blit(desc_surf, desc_rect)
        
        return mouse_over
    
    def draw_progress_bar(self, screen, value, max_value, rect, color=Colors.PRIMARY, bg_color=Colors.SURFACE):
        """Draw a progress bar"""
        # Background
        pygame.draw.rect(screen, bg_color, rect, width=0, border_radius=8)
        
        # Fill
        fill_width = int(rect.width * (value / max_value))
        fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
        pygame.draw.rect(screen, color, fill_rect, width=0, border_radius=8)
        
        # Border
        pygame.draw.rect(screen, Colors.PRIMARY, rect, width=2, border_radius=8)
        
        # Text
        percent = int((value / max_value) * 100)
        text = self.font_small.render(f"{percent}%", True, Colors.TEXTBRIGHT)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
    
    def draw_health_bar(self, screen, current, max_health, position, spacing=5):
        """Draw heart-based health display"""
        for i in range(max_health):
            x = position[0] + i * (25 + spacing)
            y = position[1]
            
            if i < current:
                # Full heart
                color = (255, 50, 100)
            else:
                # Empty heart
                color = (50, 50, 50)
            
            # Draw heart shape
            points = [
                (x, y - 10),
                (x - 8, y),
                (x, y + 8),
                (x + 8, y)
            ]
            pygame.draw.polygon(screen, color, points)
            
            # Add outline
            pygame.draw.polygon(screen, Colors.TEXTBRIGHT, points, 1)
    
    def draw_shield_icon(self, screen, count, position, spacing=5):
        """Draw shield icons"""
        for i in range(count):
            x = position[0] + i * (25 + spacing)
            y = position[1]
            
            # Draw shield
            pygame.draw.circle(screen, Colors.INFO, (x, y), 10)
            pygame.draw.circle(screen, Colors.TEXTBRIGHT, (x, y), 10, 1)
            # Shield symbol (smaller circle)
            pygame.draw.circle(screen, Colors.TEXTBRIGHT, (x, y), 6)
    
    def draw_exp_bar(self, screen, current_exp, exp_for_next_level, position, size=(200, 20)):
        """Draw experience bar with level indicator"""
        rect = pygame.Rect(position[0], position[1], size[0], size[1])
        
        # Background
        pygame.draw.rect(screen, Colors.SURFACE, rect, width=0, border_radius=10)
        
        # Fill
        fill_rect = pygame.Rect(rect.x, rect.y, 
                                int(rect.width * (current_exp / exp_for_next_level)), 
                                rect.height)
        pygame.draw.rect(screen, Colors.ACCENT, fill_rect, width=0, border_radius=10)
        
        # Border
        pygame.draw.rect(screen, Colors.PRIMARY, rect, width=2, border_radius=10)
        
        # Level text
        level = int((current_exp / exp_for_next_level) * 100)
        text = self.font_small.render(f"LVL {level}", True, Colors.TEXTBRIGHT)
        text_rect = text.get_rect(center=(rect.centerx, rect.y - 25))
        screen.blit(text, text_rect)
    
    def draw_stat(self, screen, label, value, position, icon=None):
        """Draw a stat display with optional icon"""
        x, y = position
        
        # Draw icon
        if icon == "score":
            pygame.draw.circle(screen, Colors.ACCENT, (x, y), 8)
            pygame.draw.circle(screen, Colors.TEXTBRIGHT, (x, y), 8, 1)
            x += 20
        elif icon == "level":
            # Star icon
            points = [
                (x, y - 8),
                (x + 5, y),
                (x, y + 8),
                (x - 5, y)
            ]
            pygame.draw.polygon(screen, Colors.ACCENT, points)
            pygame.draw.polygon(screen, Colors.TEXTBRIGHT, points, 1)
            x += 20
        
        # Draw label
        label_surf = self.font_small.render(f"{label}:", True, Colors.TEXT_MUTED)
        screen.blit(label_surf, (x, y - 10))
        
        # Draw value
        value_surf = self.font_regular.render(str(value), True, Colors.TEXTBRIGHT)
        value_rect = value_surf.get_rect(midleft=(x + label_surf.get_width() + 5, y))
        screen.blit(value_surf, value_rect)
    
    def draw_title(self, screen, text, y_offset=0, glow=True):
        """Draw main title with glow effect"""
        x = self.screen_width // 2
        y = self.screen_height // 4 + y_offset
        
        if glow:
            # Glow effect
            for i in range(10, 0, -2):
                alpha = 100 * (i / 10)
                glow_surf = self.font_large.render(text, True, (100, 200, 255, alpha))
                glow_rect = glow_surf.get_rect(center=(x, y))
                # Offset slightly
                offset = i // 2
                screen.blit(glow_surf, (glow_rect.x - offset, glow_rect.y - offset))
        
        # Main text
        text_surf = self.font_large.render(text, True, Colors.PRIMARY)
        text_rect = text_surf.get_rect(center=(x, y))
        screen.blit(text_surf, text_rect)
        
        # Secondary outline
        text_surf_outline = self.font_large.render(text, True, Colors.TEXTBRIGHT)
        screen.blit(text_surf_outline, (text_rect.x - 2, text_rect.y - 2))
        
        return text_rect
    
    def draw_particle_effect(self, screen, center, count=20, max_distance=100):
        """Draw particle effect for selections/transitions"""
        for i in range(count):
            angle = i * (360 / count)
            distance = random.randint(0, max_distance)
            offset = pygame.Vector2(0, -distance).rotate(angle)
            pos = center + offset
            
            # Random size and color
            size = random.randint(2, 6)
            color = Colors.PRIMARY
            
            pygame.draw.circle(screen, color, pos, size)
    
    async def animate_transition(self, screen, duration=0.5):
        """Animate a smooth transition"""
        start_time = pygame.time.get_ticks()
        end_time = start_time + duration * 1000
        
        while pygame.time.get_ticks() < end_time:
            elapsed = pygame.time.get_ticks() - start_time
            progress = elapsed / (end_time - start_time)
            
            # Fade effect
            alpha = int(255 * (1 - progress))
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
            
            pygame.display.flip()
            await asyncio.sleep(0.01)
    
    def create_main_menu(self, screen, game_version):
        """Create and return main menu elements"""
        menu_items = []
        
        center_x = self.screen_width // 2
        start_y = self.screen_height // 2
        
        # Title
        title_rect = pygame.Rect(0, 0, 400, 80)
        title_rect.center = (center_x, start_y - 150)
        
        # Buttons
        button_width = 300
        button_height = 60
        button_spacing = 20
        
        play_rect = pygame.Rect(0, 0, button_width, button_height)
        play_rect.center = (center_x, start_y - 50)
        
        settings_rect = pygame.Rect(0, 0, button_width, button_height)
        settings_rect.center = (center_x, start_y + 20)
        
        quit_rect = pygame.Rect(0, 0, button_width, button_height)
        quit_rect.center = (center_x, start_y + 90)
        
        # Version text
        version_rect = pygame.Rect(0, 0, 200, 30)
        version_rect.bottomright = (self.screen_width - 20, self.screen_height - 20)
        
        menu_items = {
            "title": title_rect,
            "play": play_rect,
            "settings": settings_rect,
            "quit": quit_rect,
            "version": version_rect,
            "version_text": f"v{game_version}"
        }
        
        return menu_items
    
    def draw_main_menu(self, screen, menu_items, selected_item=None):
        """Draw the main menu"""
        screen.fill(Colors.BACKGROUND)
        
        # Draw stars in background
        self.draw_starry_background(screen)
        
        # Draw title
        self.draw_title(screen, "ASTEROIDS", -50)
        
        # Draw buttons
        play_selected = (selected_item == "play")
        settings_selected = (selected_item == "settings")
        quit_selected = (selected_item == "quit")
        
        self.draw_button(screen, "PLAY", menu_items["play"], selected=play_selected)
        self.draw_button(screen, "SETTINGS", menu_items["settings"], selected=settings_selected)
        self.draw_button(screen, "QUIT", menu_items["quit"], selected=quit_selected)
        
        # Draw version
        version_text = self.font_tiny.render(menu_items["version_text"], True, Colors.TEXT_MUTED)
        screen.blit(version_text, menu_items["version"])
        
        return screen
    
    def draw_starry_background(self, screen, density=0.0005):
        """Draw a starry background"""
        import random
        for x in range(0, self.screen_width, 10):
            for y in range(0, self.screen_height, 10):
                if random.random() < density:
                    brightness = random.randint(50, 200)
                    size = random.randint(1, 3)
                    color = (brightness, brightness, brightness + 50)
                    pygame.draw.circle(screen, color, (x, y), size)
    
    def create_difficulty_menu(self, screen):
        """Create difficulty selection menu"""
        difficulties = [
            {"id": 0, "name": "EASY", "desc": "Relaxed gameplay", "color": Colors.SUCCESS},
            {"id": 1, "name": "MEDIUM", "desc": "Balanced challenge", "color": Colors.WARNING},
            {"id": 2, "name": "NIGHTMARE", "desc": "For the brave", "color": Colors.DANGER},
        ]
        
        center_x = self.screen_width // 2
        start_y = self.screen_height // 2 - 50
        
        rects = []
        for i, diff in enumerate(difficulties):
            card_width = 250
            card_height = 150
            card_rect = pygame.Rect(0, 0, card_width, card_height)
            card_rect.center = (center_x + (i - 1) * 300, start_y)
            rects.append((card_rect, diff))
        
        # Back button
        back_rect = pygame.Rect(0, 0, 150, 50)
        back_rect.center = (center_x, self.screen_height - 80)
        
        return {"cards": rects, "back": back_rect, "difficulties": difficulties}
    
    def draw_difficulty_menu(self, screen, menu_data, selected_index=None):
        """Draw difficulty selection menu"""
        screen.fill(Colors.BACKGROUND)
        self.draw_starry_background(screen)
        
        # Draw title
        title = self.font_large.render("SELECT DIFFICULTY", True, Colors.PRIMARY)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
        screen.blit(title, title_rect)
        
        # Draw difficulty cards
        for i, (card_rect, diff) in enumerate(menu_data["cards"]):
            is_selected = (selected_index == i)
            # Draw card with custom colors
            mouse_pos = pygame.mouse.get_pos()
            mouse_over = card_rect.collidepoint(mouse_pos)
            
            bg_color = Colors.SURFACE
            if is_selected:
                bg_color = Colors.SURFACE_ACTIVE
            elif mouse_over:
                bg_color = Colors.SURFACE_HOVER
            
            pygame.draw.rect(screen, bg_color, card_rect, width=0, border_radius=15)
            
            if is_selected or mouse_over:
                self.draw_glow_rect(screen, diff["color"], card_rect, radius=15, glow_size=5)
            else:
                pygame.draw.rect(screen, diff["color"], card_rect, width=3, border_radius=15)
            
            # Draw difficulty name
            name_surf = self.font_medium.render(diff["name"], True, Colors.TEXTBRIGHT)
            name_rect = name_surf.get_rect(center=(card_rect.centerx, card_rect.y + 40))
            screen.blit(name_surf, name_rect)
            
            # Draw description
            desc_surf = self.font_small.render(diff["desc"], True, Colors.TEXT_MUTED)
            desc_rect = desc_surf.get_rect(center=(card_rect.centerx, card_rect.y + 90))
            screen.blit(desc_surf, desc_rect)
            
            # Draw hotkey
            hotkey_surf = self.font_small.render(f"Press {i + 1}", True, Colors.TEXT_MUTED)
            hotkey_rect = hotkey_surf.get_rect(center=(card_rect.centerx, card_rect.bottom - 20))
            screen.blit(hotkey_surf, hotkey_rect)
        
        # Draw back button
        self.draw_button(screen, "BACK", menu_data["back"], selected=(selected_index == "back"))
        
        return screen
    
    def create_upgrade_menu(self, screen, upgrade_options, player):
        """Create upgrade selection menu"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        card_width = 280
        card_height = 200
        card_spacing = 300
        start_x = center_x - (len(upgrade_options) - 1) * card_spacing // 2
        
        rects = []
        for i, upgrade in enumerate(upgrade_options):
            card_rect = pygame.Rect(start_x + i * card_spacing, center_y - 100, card_width, card_height)
            
            # Determine upgrade type and icon
            icon = self.get_upgrade_icon(upgrade)
            description = self.get_upgrade_description(upgrade)
            
            # Determine rarity
            if upgrade in constants.WEAPONS:
                rarity = "weapon"
            elif upgrade in ["Shield", "Extra Life"]:
                rarity = "rare"
            elif upgrade in ["Multi Shot", "Rapid Fire"]:
                rarity = "uncommon"
            else:
                rarity = "common"
            
            rects.append((card_rect, upgrade, icon, description, rarity))
        
        return {"cards": rects}
    
    def get_upgrade_icon(self, upgrade):
        """Get icon name for upgrade"""
        icons = {
            "Multi Shot": "multishot",
            "Shield": "shield",
            "Extra Life": "heart",
            "Piercing Bullets": "piercing",
            "Bigger Bullets": "bigger",
            "Rapid Fire": "rapid",
            "Rotator": "rotator",
            "EMP": "emp",
            "Laser": "laser"
        }
        return icons.get(upgrade, "bigger")
    
    def get_upgrade_description(self, upgrade):
        """Get description for upgrade"""
        descriptions = {
            "Multi Shot": "Fire additional projectiles",
            "Shield": "Absorbs hits without losing health",
            "Extra Life": "Increases maximum health",
            "Piercing Bullets": "Bullets pass through enemies",
            "Bigger Bullets": "Larger hitbox for bullets",
            "Rapid Fire": "Decreases cooldown between shots",
            "Rotator": "Orbital weapons that rotate",
            "EMP": "Area of effect explosion",
            "Laser": "Powerful laser weapon"
        }
        return descriptions.get(upgrade, "Unknown upgrade")
    
    def draw_upgrade_menu(self, screen, menu_data, player):
        """Draw upgrade selection menu"""
        # Dim background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw title
        title = self.font_medium.render("LEVEL UP! CHOOSE AN UPGRADE", True, Colors.ACCENT)
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 150))
        screen.blit(title, title_rect)
        
        # Draw level info
        level_info = self.font_small.render(f"Level {player.level}", True, Colors.TEXT_MUTED)
        level_rect = level_info.get_rect(center=(self.screen_width // 2, title_rect.bottom + 20))
        screen.blit(level_info, level_rect)
        
        # Draw upgrade cards
        for card_rect, upgrade, icon, description, rarity in menu_data["cards"]:
            mouse_pos = pygame.mouse.get_pos()
            mouse_over = card_rect.collidepoint(mouse_pos)
            
            # Draw card
            self.draw_card(screen, upgrade, description, card_rect, 
                          icon=icon, selected=False, rarity=rarity)
        
        # Draw hotkey indicators
        for i, (card_rect, upgrade, icon, description, rarity) in enumerate(menu_data["cards"]):
            hotkey = self.font_small.render(f"{i + 1}", True, Colors.TEXTBRIGHT)
            hotkey_rect = hotkey.get_rect(bottomright=(card_rect.right - 10, card_rect.bottom - 10))
            # Draw hotkey background
            pygame.draw.rect(screen, Colors.SURFACE, hotkey_rect.inflate(10, 5), width=0, border_radius=5)
            pygame.draw.rect(screen, Colors.PRIMARY, hotkey_rect.inflate(10, 5), width=1, border_radius=5)
            screen.blit(hotkey, hotkey_rect)
        
        return screen
    
    def draw_hud(self, screen, player):
        """Draw the in-game HUD"""
        # Health
        self.draw_health_bar(screen, player.health, player.max_health, (20, 20))
        
        # Shield
        self.draw_shield_icon(screen, player.shield, (20, 60))
        
        # Score
        score_text = self.font_regular.render(f"{player.score}", True, Colors.TEXTBRIGHT)
        score_label = self.font_small.render("SCORE", True, Colors.TEXT_MUTED)
        screen.blit(score_label, (self.screen_width - 150, 20))
        screen.blit(score_text, (self.screen_width - 150, 45))
        
        # Level
        level_text = self.font_regular.render(f"LEVEL: {player.level}", True, Colors.ACCENT)
        level_rect = level_text.get_rect(topright=(self.screen_width - 20, 20))
        screen.blit(level_text, level_rect)
        
        # EXP Bar
        exp_needed = 10 * (player.level ** 2)
        if exp_needed > 0:
            exp_bar_rect = pygame.Rect(self.screen_width // 2 - 150, self.screen_height - 40, 300, 20)
            self.draw_progress_bar(screen, player.exp, exp_needed, exp_bar_rect, 
                                   color=Colors.ACCENT, bg_color=Colors.SURFACE)
        
        # Weapon indicators (if any active)
        if hasattr(player, 'weapon_manager') and player.weapon_manager.weapons:
            weapon_x = self.screen_width // 2 - 50
            weapon_y = self.screen_height - 80
            
            for i, weapon in enumerate(player.weapon_manager.weapons):
                if weapon.level > 0:
                    # Draw weapon icon
                    icon_size = 30
                    icon_rect = pygame.Rect(weapon_x + i * (icon_size + 15), weapon_y, icon_size, icon_size)
                    
                    weapon_name = weapon.__class__.__name__.lower()
                    if "rotator" in weapon_name:
                        pygame.draw.circle(screen, Colors.INFO, icon_rect.center, icon_size // 2, 2)
                        for j in range(3):
                            angle = j * 120
                            pos = icon_rect.center + pygame.Vector2(0, -icon_size // 2).rotate(angle)
                            pygame.draw.circle(screen, Colors.INFO, pos, 4)
                    elif "emp" in weapon_name:
                        pygame.draw.circle(screen, Colors.DANGER, icon_rect.center, icon_size // 2)
                        pygame.draw.circle(screen, Colors.DANGER, icon_rect.center, icon_size // 3, 1)
                    elif "laser" in weapon_name:
                        pygame.draw.line(screen, Colors.WARNING,
                                        icon_rect.center + pygame.Vector2(-icon_size // 2, 0),
                                        icon_rect.center + pygame.Vector2(icon_size // 2, 0), 3)
                    
                    # Draw level indicator
                    if weapon.level > 1:
                        level_indicator = self.font_tiny.render(str(weapon.level), True, Colors.TEXTBRIGHT)
                        level_rect = level_indicator.get_rect(bottomright=icon_rect.bottomright)
                        screen.blit(level_indicator, level_rect)
        
        return screen
    
    def create_game_over_menu(self, screen, player):
        """Create game over menu"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Main panel
        panel_width = 500
        panel_height = 400
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (center_x, center_y)
        
        # Buttons
        restart_rect = pygame.Rect(0, 0, 200, 60)
        restart_rect.center = (center_x, center_y + 100)
        
        menu_rect = pygame.Rect(0, 0, 200, 60)
        menu_rect.center = (center_x, center_y + 170)
        
        return {
            "panel": panel_rect,
            "restart": restart_rect,
            "menu": menu_rect,
            "player": player
        }
    
    def draw_game_over_menu(self, screen, menu_data):
        """Draw game over menu"""
        player = menu_data["player"]
        
        # Dim background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        panel = menu_data["panel"]
        pygame.draw.rect(screen, Colors.SURFACE, panel, width=0, border_radius=20)
        pygame.draw.rect(screen, Colors.DANGER, panel, width=3, border_radius=20)
        
        # Draw title
        title = self.font_large.render("GAME OVER", True, Colors.DANGER)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 50))
        screen.blit(title, title_rect)
        
        # Draw stats
        stats_y = panel.y + 120
        
        score = self.font_medium.render(f"Final Score: {player.score}", True, Colors.TEXTBRIGHT)
        score_rect = score.get_rect(center=(panel.centerx, stats_y))
        screen.blit(score, score_rect)
        
        level = self.font_medium.render(f"Level Reached: {player.level}", True, Colors.TEXTBRIGHT)
        level_rect = level.get_rect(center=(panel.centerx, stats_y + 40))
        screen.blit(level, level_rect)
        
        # Draw buttons
        self.draw_button(screen, "PLAY AGAIN", menu_data["restart"])
        self.draw_button(screen, "MAIN MENU", menu_data["menu"])
        
        return screen
    
    def create_pause_menu(self, screen):
        """Create pause menu"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        # Main panel
        panel_width = 400
        panel_height = 300
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (center_x, center_y)
        
        # Buttons
        resume_rect = pygame.Rect(0, 0, 200, 60)
        resume_rect.center = (center_x, center_y - 50)
        
        settings_rect = pygame.Rect(0, 0, 200, 60)
        settings_rect.center = (center_x, center_y + 20)
        
        quit_rect = pygame.Rect(0, 0, 200, 60)
        quit_rect.center = (center_x, center_y + 90)
        
        return {
            "panel": panel_rect,
            "resume": resume_rect,
            "settings": settings_rect,
            "quit": quit_rect
        }
    
    def draw_pause_menu(self, screen, menu_data):
        """Draw pause menu"""
        # Dim background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Draw panel
        panel = menu_data["panel"]
        pygame.draw.rect(screen, Colors.SURFACE, panel, width=0, border_radius=20)
        pygame.draw.rect(screen, Colors.PRIMARY, panel, width=3, border_radius=20)
        
        # Draw title
        title = self.font_large.render("PAUSED", True, Colors.PRIMARY)
        title_rect = title.get_rect(center=(panel.centerx, panel.y + 40))
        screen.blit(title, title_rect)
        
        # Draw buttons
        self.draw_button(screen, "RESUME", menu_data["resume"])
        self.draw_button(screen, "SETTINGS", menu_data["settings"])
        self.draw_button(screen, "QUIT", menu_data["quit"])
        
        return screen
    
    async def handle_menu_selection(self, menu_data, button_names):
        """Generic menu selection handler"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for name in button_names:
                        if name in menu_data and menu_data[name].collidepoint(mouse_pos):
                            return name
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "back"
                    # Check for number keys
                    for i, name in enumerate(button_names[:9]):  # First 9 buttons
                        if event.key == getattr(pygame, f"K_{i+1}"):
                            return name
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            await asyncio.sleep(0)
