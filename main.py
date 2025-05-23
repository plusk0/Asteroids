import pygame
from constants import *
from player import player

def main():
    pygame.init()
    Clock = pygame.time.Clock()
    dt = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    spaceship = player(SCREEN_HEIGHT / 2, SCREEN_WIDTH / 2)
    print("Starting Asteroids!")
    print("Screen width:", SCREEN_WIDTH)
    print("Screen height:", SCREEN_HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


        spaceship.update(dt)
        screen.fill(0)
        spaceship.draw(screen)
        dt = Clock.tick(60) / 1000
        pygame.display.flip()

if __name__ == "__main__":
    main()