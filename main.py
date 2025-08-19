import pygame, constants, asyncio

from menu import Menu
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


async def main():
    pygame.init()
    Clock = pygame.time.Clock()

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    weapons = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)

    paused = False
    dt = 0
    Menu.update_scale(1)
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

    player = Player(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)
    shielded_until = 0
    weapon_manager = player.weapon_manager

    level = player.level
    asteroid_field = AsteroidField()
    
    pygame.time.wait(1000) # Initial delay to ensure loading with less weird lag

    while paused == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
        updatable.update(dt)
        weapon_manager.update(player, screen, dt)

        if player.shielded and pygame.time.get_ticks() > shielded_until:
            player.shielded = False

        for asteroid in asteroids:
            if asteroid.collide(player):
                if player.shielded and pygame.time.get_ticks() < shielded_until:
                    asteroid.kill()
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
                    print("GAME OVER!")
                    exit()

            for shot in list(shots) + weapon_manager.get_all_shots():
                if hasattr(shot, "is_active") and not shot.is_active():
                    continue

                if asteroid.collide(shot):
                    asteroid.kill()
                    player.score += 100
                    if shot.piercing > 0:
                        shot.piercing -= 1
                    else:
                        shot.kill()
                    player.gain_exp(10)
        screen.fill(0)

        for entity in drawable:
            entity.draw(screen)
        
        Menu.update(screen, player)

        for weapon in weapons:
            weapon.update(player, screen, dt)

        if player.level > level:
            level = player.level
            paused = True
            Menu.level_up(screen, player)
            asteroid_field.modifier = 1 + (player.level / 10)
            paused = False
            Clock.tick()
        
        dt = Clock.tick(120) / 1000
        await asyncio.sleep(0)

        pygame.display.flip()

        pygame.display.set_caption(f"Score: {player.score} | Level: {player.level} | Health: {player.health} | Shield: {player.shield}")



asyncio.run(main())