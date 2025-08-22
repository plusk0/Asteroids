import constants
from circleshape import *
from shot import Shot
from weapon import Weapon
from shot import Shot

class RotatorShot(Shot):
    def __init__(self, x, y, radius, level, rotator):
        super().__init__(x, y, radius)
        self.piercing = 0
        self.disabled_until = 0
        self.level = level
        self.active = True
        self.rotator = rotator

    def kill(self):
        self.active = False
        self.disabled_until = pygame.time.get_ticks() + (2000 * max(0.2, 1 - (self.level * 0.1)))

    def is_active(self):
        if self.active:
            return True
        if pygame.time.get_ticks() >= self.disabled_until:
            self.active = True
            self.piercing = self.rotator.piercing
            return True
        return False
    
    def draw(self, screen):
        if self.is_active():
            super().draw(screen)
        else:
            pass


class Rotator(Weapon):
    def __init__(self, player):

        self.player = player
        self.rotation = 0
        self.radius = constants.ROTATOR_RADIUS / 5
        self.distance = constants.ROTATOR_RADIUS * 0.7

        self.level = 0
        self.count = 0
        self.piercing = self.player.piercing

        self.shots = []

        self.apply_upgrade()

    def apply_upgrade(self):
        self.piercing = self.player.piercing

        self.count += 1
        self.level += 1

        shot = RotatorShot(self.player.position.x, self.player.position.y, self.radius, self.level, self)
        self.shots.append(shot)

        if self.count > 10:
            self.count = 10


    def rotate(self, angle):
        self.rotation += angle
        self.rotation %= 360

    def update(self, player, screen, dt):

        if len(self.shots) == 0:
            return
        
        speed = constants.ROTATOR_SPEED * (self.level * 0.33)
        self.rotate(dt * speed)
        self.position = player.position.copy()
        for i, shot in enumerate(self.shots):
            angle = self.rotation + (360 * i / len(self.shots))
            shot.position = player.position + pygame.Vector2(0, -self.radius).rotate(angle) * self.distance
            if shot.is_active():
                shot.draw(screen)