import pygame
import constants

from rotator import Rotator
from emp import Emp

from laser import Laser_Shot, Laser
from shot import Shot

class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.weapons = []
        self.add_default_weapons()
        self.shots = []

    def add_default_weapons(self):
        self.rotate = Rotator(self.player)
        self.boom = Emp(self.player)
        self.laser = Laser(self.player)
        self.weapons.append(self.rotate)
        self.weapons.append(self.boom)
        self.weapons.append(self.laser)
        #Add other weapons here
        
    
    def update(self, player, screen, dt):
        for weapon in self.weapons:
            weapon.update(player, screen, dt)

    def apply_upgrade_by_name(self, weapon_name):
        for weapon in self.weapons:
            if weapon.__class__.__name__.lower() == weapon_name.lower():
                weapon.apply_upgrade()
                return True
        return False

    def get_all_shots(self):
        for weapon in self.weapons:
            weapon_shots = weapon.get_shots()
            if weapon_shots != None:
                self.shots.extend(weapon_shots)        
        return self.shots
    
    def get_effects(self):
        return self.laser.effects

    def shoot(self):
            for i in range(self.player.shot_no):
                angle_offset = (i - (self.player.shot_no - 1) / 2) * 10
                if self.player.laser == False:
                    bullet = Shot(self.player.position[0], self.player.position[1], self.player.shot_radius)
                    bullet.velocity = pygame.Vector2(0, 1).rotate(self.player.rotation + angle_offset) * self.player.shot_speed
                else:
                    bullet = Laser_Shot(self.player, self.laser)
                    bullet.velocity = pygame.Vector2(0, 1).rotate(self.player.rotation + angle_offset) * self.player.shot_speed * constants.LASER_SPEED_MULT
                bullet.piercing = self.player.piercing
                self.player.current_cooldown = self.player.shot_cooldown + 1 * (self.player.shot_no / 10)
                if self.player.laser == True:
                    self.player.current_cooldown *= 2






