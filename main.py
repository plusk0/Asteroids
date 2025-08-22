import pygame, constants, asyncio

from menu import Menu
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot

class Game():
    
    def __init__(self):
        pygame.init()
        self.actual_screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
        Menu.update_scale()
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
            weapons = pygame.sprite.Group()

            Player.containers = (updatable, drawable)
            Asteroid.containers = (asteroids, updatable, drawable)
            AsteroidField.containers = (updatable)
            Shot.containers = (shots, updatable, drawable)

        dt = 0
        shielded_until = 0
        level = 1

        player = Player(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)
        weapon_manager = player.weapon_manager
        asteroid_field = AsteroidField()

            restart = False

            difficulty_options, rects =  gameMenu.select_difficulty(self)
            difficulty, other = await gameMenu.handle_difficulty_selection(rects, difficulty_options)
            

            # --- Main game loop ---
            while True:
                if restart == True:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                updatable.update(dt)
                weapon_manager.update(player, self.screen, dt)

                if player.shielded and pygame.time.get_ticks() > shielded_until:
                    player.shielded = False

                for asteroid in asteroids:
                    
                    if asteroid.collide(player):
                        if player.shielded and pygame.time.get_ticks() < shielded_until:
                            asteroid.kill()
                            player.gain_exp()
                            player.gain_score()
                            continue

                        if player.shield > 0:
                            player.shield -= 1
                            asteroid.kill()
                            shielded_until = pygame.time.get_ticks() + constants.SHIELD_DURATION
                            player.shielded = True

                        elif player.health > 1:
                            player.health -= 1
                            asteroid.kill()
                        else:
                            restart = await gameMenu.show_game_over(self.screen)
                            if restart == True:
                                break  # Break inner loop to restart
                            else:
                                return 

                    for shot in list(shots) + weapon_manager.get_all_shots():
                        if hasattr(shot, "is_active") and not shot.is_active():
                            continue

                        if asteroid.collide(shot):
                            asteroid.kill()
                            player.gain_score()
                            if shot.piercing > 0:
                                shot.piercing -= 1
                            else:
                                shot.kill()
                            player.gain_exp()
                self.screen.fill(0)

                for entity in drawable:
                    entity.draw(self.screen)
                
                gameMenu.update(self.screen, player)

                for weapon in weapons:
                    weapon.update(player, self.screen, dt)

                if player.level > level:
                    level = player.level
                    options, rects = gameMenu.show_upgrade_menu(self)
                    await gameMenu.handle_upgrade_selection(rects, options, player)

                    asteroid_field.modifier = (1 + (player.level / 10)) * (difficulty + 1)

                    Clock.tick()
                
                self.actual_screen.blit(pygame.transform.scale(self.screen, self.screen.get_rect().size), (0, 0))
                dt = Clock.tick(120) / 1000
                await asyncio.sleep(0)

                pygame.display.flip()
            

asyncio.run(Game.main(Game()))