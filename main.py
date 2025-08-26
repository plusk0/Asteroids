import pygame, constants, asyncio

from menu import Menu
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from laser import Laser_effect

class Game():

    def __init__(self):
        pygame.init()
        self.actual_screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), pygame.RESIZABLE)
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

            Player.containers = (updatable, drawable)
            Asteroid.containers = (asteroids, updatable, drawable)
            AsteroidField.containers = (updatable)
            Shot.containers = (shots, updatable, drawable)
            Laser_effect.containers = (effects)

            dt = 0
            shielded_until = 0
            level = 1

            player = Player(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)
            weapon_manager = player.weapon_manager
            asteroid_field = AsteroidField()

            restart = False

            difficulty_options, rects =  gameMenu.select_difficulty(self)
            difficulty, foo = await gameMenu.handle_difficulty_selection(rects, difficulty_options)
            player.screen = self.screen
            # --- Main game loop ---
            while True:
                if restart == True:
                    break

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return

                updatable.update(dt)

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
                            player.gain_exp()
                            shielded_until = pygame.time.get_ticks() + constants.SHIELD_DURATION
                            player.shielded = True

                        elif player.health > 1:
                            player.health -= 1
                            asteroid.kill()

                        else:
                            restart = await gameMenu.show_game_over(self)

                    for shot in list(shots):
                        if hasattr(shot, "is_active") and not shot.is_active():
                            continue

                        if asteroid.collide(shot):
                            asteroid.kill()
                            player.gain_score()
                            if shot.piercing > 0:
                                shot.piercing -= 1
                            else:
                                if hasattr(shot, "laser"):
                                    weapon_manager.laser.apply_aftereffect(shot)
                                shot.kill()
                            player.gain_exp()

                    for effect in weapon_manager.get_effects():
                        if effect.check_kill_dist(asteroid):
                            asteroid.kill()
                            player.gain_score()


                self.screen.fill(0)
                self.actual_screen.fill(0)

                for entity in drawable:
                    entity.draw(self.screen)
                
                gameMenu.update(self.screen, player)

                if player.level > level:
                    level = player.level
                    options, rects = gameMenu.show_upgrade_menu(self)
                    await gameMenu.handle_upgrade_selection(rects, options, player)
                    asteroid_field.increase_difficulty(level, difficulty)
                    Clock.tick()

                weapon_manager.update(player, self.screen, dt)
                self.actual_screen.blit(pygame.transform.scale(self.screen, self.actual_screen.get_rect().size), (0, 0))
                dt = Clock.tick(120) / 1000
                await asyncio.sleep(0)

                pygame.display.flip()
            await asyncio.sleep(0)
            
        
if __name__=="__main__":
    g = Game()
    asyncio.run(g.main())          