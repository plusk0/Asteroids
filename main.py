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

        pygame.display.set_caption(f"Space Game - Version 0.0.0.69")
        self.difficulty = 0

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

            player = Player(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)
            weapon_manager = player.weapon_manager
            asteroid_field = AsteroidField()

            # Set player screen reference
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

                        if player.shield > 0:
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

                for entity in drawable:
                    entity.draw(self.screen)

                gameMenu.update(self.screen, player)

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

                weapon_manager.update(player, self.screen, dt)
                # Update weapon references to game and asteroids for targeting
                for weapon in weapon_manager.weapons:
                    weapon.asteroids = asteroids
                    weapon.game = self

                # Calculate zoom scale based on player level (10% per level)
                # scale = 1 / (1 + 0.1 * (level - 1)) so level 1 = 100%, level 2 = ~90.9%, level 11 = 50%
                # zoom_scale = 1.0 / (1 + 0.1 * max(0, player.level - 1))
                # To be implemented for non-GUI parts of the game

                # Scale the screen with zoom effect
                # scaled_screen = pygame.transform.scale(
                #    self.screen,
                #    (
                #        int(self.screen.get_width() * zoom_scale),
                #        int(self.screen.get_height() * zoom_scale),
                #    ),
                # )

                # Center the scaled screen on the actual screen
                # offset_x = (
                #    self.actual_screen.get_width() - scaled_screen.get_width()
                # ) // 2
                # offset_y = (
                #    self.actual_screen.get_height() - scaled_screen.get_height()
                # ) // 2

                self.actual_screen.blit(
                    pygame.transform.scale(
                        self.screen, self.actual_screen.get_rect().size
                    ),
                    (0, 0),
                )

                # (scaled_screen, (offset_x, offset_y))
                dt = Clock.tick(120) / 1000
                await asyncio.sleep(0.001)

                pygame.display.flip()
            await asyncio.sleep(0.001)


if __name__ == "__main__":
    g = Game()
    asyncio.run(g.main())

