import pygame
import constants
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from menu import *


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


def main():
    pygame.init()
    Clock = pygame.time.Clock()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    paused = False

    dt = 0
    update_scale(1)
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable)
    Shot.containers = (shots, updatable, drawable)


    player = Player(constants.SCREEN_WIDTH / 2, constants.SCREEN_HEIGHT / 2)
    level = player.level
    asteroid_field = AsteroidField()


    print("Starting Asteroids!")
    print("Screen width:", constants.SCREEN_WIDTH)
    print("Screen height:", constants.SCREEN_HEIGHT)
    
    while paused == False:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
        updatable.update(dt)
        for asteroid in asteroids:
            if asteroid.collide(player):
                if player.shield > 0:
                    player.shield -= 1
                    asteroid.kill()
                elif player.health > 1:
                    player.health -= 1
                    asteroid.kill()
                else:
                    print("GAME OVER!")
                    exit()

            for shot in shots:
                if asteroid.collide(shot):
                    asteroid.kill()
                    if shot.piercing > 0:
                        shot.piercing -= 1
                    else:
                        shot.kill()
                    player.gain_exp(10)
        screen.fill(0)
        for entity in drawable:
            entity.draw(screen)

        if player.level > level:
            level = player.level
            paused = True
            options, rects = show_upgrade_menu(screen)
            handle_upgrade_selection(rects, options, player)
            asteroid_field.modifier = 1 + (player.level / 10)
            paused = False
            Clock.tick()
        
        
        dt = Clock.tick(60) / 1000
        
        
        
        pygame.display.flip()

if __name__ == "__main__":
    main()