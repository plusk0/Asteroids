import constants
import math

from circleshape import *
from shot import Shot
from weapon import Weapon


class Laser(Weapon):
    def __init__(self, player):
        super().__init__(player)
        self.player = player
        self.position = player.position
        self.forward = player.rotation
        self.max_width = constants.LASER_WIDTH
        self.width = self.max_width

        self.cooldown = 0
        self.shot = []
        self.effects = []

        self.aftereffect = 500

        self.level = 0
        self.piercing = 3

    def apply_upgrade(self):
        self.player.laser = True
        self.level += 1
        self.piercing += 3
        self.width += 10
        self.aftereffect *= 1.2

    def update(self, player, screen, dt):
        for effect in self.effects:
            effect.update()        
            effect.draw(screen)
        
    def apply_aftereffect(self, shot):
        aftereffect = Laser_effect(self.player, self, shot.position)
        self.effects.append(aftereffect)

class Laser_Shot(Shot):
    def __init__(self, player, Weapon):
        super().__init__(player.position.x, player.position.y, Weapon.max_width / 5)
        self.Weapon = Weapon
        self.piercing = Weapon.piercing
        self.player = player
        self.laser = True

    def draw(self, screen):
        pygame.draw.circle(screen, [5,5,5], self.position, self.radius)

    def update(self, dt):
        self.position += dt * self.velocity
        if (self.position.y < -constants.SCREEN_HEIGHT or 
        self.position.y > constants.SCREEN_HEIGHT or 
        self.position.x < -constants.SCREEN_WIDTH or 
        self.position.x > constants.SCREEN_WIDTH):
            self.kill()
            self.Weapon.apply_aftereffect(self)                     

class Laser_effect():
    def __init__(self, player, Weapon, dest):
        self.player = player
        self.Weapon = Weapon
        self.source = player.position.copy()
        self.dest = dest
        self.max_width = self.Weapon.width
        self.width = self.max_width
        self.shot_time = pygame.time.get_ticks()
        self.valid_until = self.shot_time + Weapon.aftereffect

    def draw(self, screen):
        if self.valid_until > pygame.time.get_ticks():
            pygame.draw.line(screen, "red", self.source, self.dest, int(self.width))
            

    def update(self):
        if self.valid_until > pygame.time.get_ticks():
            self.width = pygame.math.lerp(0, self.max_width, (self.valid_until - pygame.time.get_ticks()) / self.Weapon.aftereffect)
        else:
            if self in self.Weapon.effects:
                self.Weapon.effects.remove(self)

    def check_kill_dist(self, other):
        if self.valid_until < pygame.time.get_ticks():
            return False
        start = self.source
        end = self.dest
        center = other.position

        line_vec = end - start
        line_len = line_vec.length()
        if line_len == 0:
            return False 
        to_center = center - start

        # Project to_center onto line_vec, clamp to segment - 
        # AI generated calculation, dont ask me which kind of geometric dot magic is going on here
        t = max(0, min(1, to_center.dot(line_vec) / (line_len ** 2)))
        
        closest = start + line_vec * t

        dist = center.distance_to(closest)

        return dist < (self.width / 2 + other.radius)



