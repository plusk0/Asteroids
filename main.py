import pygame, constants, asyncio

from menu import Menu
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from laser import Laser_effect


class Game:
    def __init__(self):
        pygame.init()
        self.actual_screen = pygame.display.set_mode(
            (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE
        )
        self.screen = self.actual_screen.copy()

        pygame.display.set_caption("Space Game - Version 0.1")
        self.difficulty = 0

        # Gameplay scaling variables
        self.gameplay_size = (constants.GAMEPLAY_WIDTH, constants.GAMEPLAY_HEIGHT)
        self.screen_scale = 1.0
        self.screen_offset = (0, 0)

    def get_gameplay_scale(self, level):
        """Get the scale factor for gameplay based on player level.
        Returns a zoom-out factor of ~10% per level (0.9^level)"""
        return max(0.5, 1.0 - (level - 1) * 0.1)  # Max 50% zoom out

    def get_gameplay_offset(self, screen_size, gameplay_size):
        """Get the offset to center gameplay in the screen"""
        return (
            (screen_size[0] - gameplay_size[0]) // 2,
            (screen_size[1] - gameplay_size[1]) // 2,
        )

    def calculate_scaling(self):
        """Calculate scaling factors to fit gameplay area to screen while maintaining aspect ratio"""
        screen_size = self.actual_screen.get_size()
        gameplay_w, gameplay_h = self.gameplay_size
        screen_w, screen_h = screen_size

        # Calculate scale to fit while maintaining aspect ratio
        scale_w = screen_w / gameplay_w
        scale_h = screen_h / gameplay_h
        self.screen_scale = min(scale_w, scale_h)

        # Calculate offset to center the gameplay area
        scaled_w = int(gameplay_w * self.screen_scale)
        scaled_h = int(gameplay_h * self.screen_scale)
        self.screen_offset = ((screen_w - scaled_w) // 2, (screen_h - scaled_h) // 2)

        return self.screen_scale, self.screen_offset

    def screen_to_gameplay_coords(self, screen_pos):
        """Transform screen coordinates to gameplay coordinates"""
        if self.screen_scale <= 0:
            return screen_pos

        x, y = screen_pos
        offset_x, offset_y = self.screen_offset

        # Subtract offset and scale back to gameplay coordinates
        gameplay_x = (x - offset_x) / self.screen_scale
        gameplay_y = (y - offset_y) / self.screen_scale

        return (gameplay_x, gameplay_y)

    async def main(self):
        # Outer loop for restarting the game
        while True:
            Clock = pygame.time.Clock()
            gameMenu = Menu()

            updatable = pygame.sprite.Group()
            drawable = pygame.sprite.Group()

            asteroids = pygame.sprite.Group()
            shots = pygame.sprite.Group()

            effects = pygame.sprite.Group()

            # Set containers FIRST, before creating any objects
            Player.containers = (updatable, drawable)
            Asteroid.containers = (asteroids, updatable, drawable)
            AsteroidField.containers = updatable
            Shot.containers = (shots, updatable, drawable)
            Laser_effect.containers = effects

            dt = 0
            shielded_until = 0
            level = 1

            # Calculate initial scaling
            self.calculate_scaling()

            player = Player(constants.GAMEPLAY_WIDTH / 2, constants.GAMEPLAY_HEIGHT / 2)
            weapon_manager = player.weapon_manager
            asteroid_field = AsteroidField()

            # Set player screen reference - will be updated in the game loop
            player.screen = self.screen

            restart = False

            difficulty_options, rects = gameMenu.select_difficulty(self)
            result = await gameMenu.handle_difficulty_selection(
                rects, difficulty_options
            )

            if result is None or result[1] is False:  # User wants to go back/quit
                continue

            difficulty = result[0]

            # Set initial difficulty for asteroid field
            asteroid_field.set_difficulty(difficulty)
            asteroid_field.increase_difficulty(1, difficulty)  # Start with level 1

            player.shielded = False

            # --- Main game loop ---
            while True:
                if restart:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.VIDEORESIZE:
                        self.actual_screen = pygame.display.set_mode(
                            event.size, pygame.RESIZABLE
                        )
                        self.screen = self.actual_screen.copy()
                        # Recalculate scaling for new screen size
                        self.calculate_scaling()

                updatable.update(dt)

                if player.shielded and pygame.time.get_ticks() > shielded_until:
                    player.shielded = False

                for asteroid in asteroids:
                    if asteroid.collide(player):
                        # Handle asteroid collision with player
                        if player.shielded and pygame.time.get_ticks() < shielded_until:
                            # Shielded players can destroy asteroids on contact
                            if asteroid.take_damage(
                                asteroid.max_health
                            ):  # Instant kill
                                player.gain_exp()
                                player.gain_score()
                            continue

                        if player.shield > 0 and not player.shield_is_regenning:
                            if player.shield_regen_unlocked:
                                # Permanent shield: set cooldown but don't consume shield count
                                player.shield_is_regenning = True
                                player.shield_last_used = pygame.time.get_ticks()
                                # Don't decrement shield, just mark it as used
                            else:
                                # One-time shield: consume it
                                player.shield -= 1

                            if asteroid.take_damage(
                                asteroid.max_health
                            ):  # Instant kill
                                player.gain_exp()
                            shielded_until = (
                                pygame.time.get_ticks() + constants.SHIELD_DURATION
                            )
                            player.shielded = True

                        elif player.health > 1:
                            player.health -= 1
                            asteroid.kill()  # Player takes damage, asteroid is destroyed

                        else:
                            # Set game reference and player for game over menu
                            gameMenu.game = self
                            gameMenu.player = player
                            restart = await gameMenu.show_game_over(self)

                    for shot in list(shots):
                        if hasattr(shot, "is_active") and not shot.is_active():
                            continue

                        if asteroid.collide(shot):
                            if asteroid.take_damage(1):
                                player.gain_score()
                                if hasattr(shot, "laser"):
                                    weapon_manager.laser.apply_aftereffect(shot)

                            if shot.piercing > 0:
                                shot.piercing -= 1
                            else:
                                shot.kill()
                            player.gain_exp()

                    for effect in weapon_manager.get_effects():
                        if effect.check_kill_dist(asteroid):
                            asteroid.kill()
                            player.gain_score()
                            player.gain_exp()

                    # Check for Shockwave collisions
                    for weapon in weapon_manager.weapons:
                        if hasattr(
                            weapon, "check_collision"
                        ) and weapon.check_collision(asteroid):
                            if asteroid.take_damage(weapon.damage):
                                player.gain_score()
                            player.gain_exp()

                self.screen.fill(0)
                self.actual_screen.fill(0)

                # Use the pre-calculated scaling
                gameplay_w, gameplay_h = self.gameplay_size
                offset = self.screen_offset

                # Create a gameplay surface at the standard gameplay size
                gameplay_screen = pygame.Surface((gameplay_w, gameplay_h))
                gameplay_screen.fill(0)

                # Update player screen reference to gameplay surface
                player.screen = gameplay_screen

                # Draw gameplay elements to gameplay surface
                for entity in drawable:
                    entity.draw(gameplay_screen)

                # Draw weapon effects
                weapon_manager.update(player, gameplay_screen, dt)

                # Update weapon references to game and asteroids for targeting
                for weapon in weapon_manager.weapons:
                    weapon.asteroids = asteroids
                    weapon.game = self

                # Scale gameplay surface and blit to actual screen (centered)
                scaled_size = (
                    int(gameplay_w * self.screen_scale),
                    int(gameplay_h * self.screen_scale),
                )
                scaled_gameplay = pygame.transform.scale(gameplay_screen, scaled_size)
                self.actual_screen.blit(scaled_gameplay, offset)

                # Draw UI elements at native resolution (not scaled)
                gameMenu.update(self.actual_screen, player)

                if player.level > level:
                    level = player.level
                    result = gameMenu.show_upgrade_menu(self, player)
                    options = result[0]
                    rects = result[1]
                    formations = result[2] if len(result) > 2 else []
                    selected_upgrade = await gameMenu.handle_upgrade_selection(
                        rects, options, player, formations
                    )
                    if selected_upgrade:
                        asteroid_field.increase_difficulty(level, difficulty)
                        asteroid_field.set_player_level(level)
                    Clock.tick()

                # (scaled_screen, (offset_x, offset_y))
                dt = Clock.tick(120) / 1000
                await asyncio.sleep(0.001)

                pygame.display.flip()
            await asyncio.sleep(0.001)


if __name__ == "__main__":
    g = Game()
    asyncio.run(g.main())
