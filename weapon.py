import pygame

class Weapon(pygame.sprite.Sprite):

    def __init__(self, player):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.player = player
        self.level = 1
        self.damage = 1
        self.shots = []