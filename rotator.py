import constants
from circleshape import *
from shot import Shot
from weapon import Weapon

from shot import Shot

class RotatorShot(Shot):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.piercing = 0
        self.disabled_until = 0

    def kill(self):
        self.disabled_until = pygame.time.get_ticks() + 2000

    def is_active(self):
        return pygame.time.get_ticks() >= self.disabled_until
    
    def draw(self, screen):
        if self.is_active():
            super().draw(screen)
        else:
            pass


class Rotator(Weapon):
    def __init__(self, player):

        self.player = player
        self.rotation = 0
        self.radius = constants.ROTATOR_RADIUS * (constants.SCALE / 5 )
        self.distance = constants.ROTATOR_RADIUS * (constants.SCALE / 2)

        self.level = 0
        self.count = 0

        self.shots = []

        self.apply_upgrade()

    def apply_upgrade(self):
        self.count += 1
        self.level += 1

        self.shots.clear()

        if self.count > 10:
            self.count = 10
        print(f"Rotator upgraded to level {self.level} with {self.count} shots")

        for i in range(self.count): 
            shot = RotatorShot(self.player.position.x, self.player.position.y, self.radius)
            shot.piercing = self.player.piercing
            self.shots.append(shot)
            print(len(self.shots), "shots created")

    def rotate(self, angle):
        self.rotation += angle
        self.rotation %= 360

    def update(self, player, screen, dt):

        if len(self.shots) == 0:
            return
        
        self.rotate(dt * constants.ROTATOR_SPEED * (self.level * 0.33))
        self.position = player.position.copy()
        for shot in self.shots:
            shot.position = player.position + pygame.Vector2(0, -self.radius).rotate(self.rotation / len(self.shots)) * self.distance
            if shot.is_active():
                shot.draw(screen)