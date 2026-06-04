import pygame
import constants

from rotator import Rotator
from emp import Emp
from laser import Laser, Laser_Shot
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
        """Get all active shots from all weapons"""
        all_shots = []
        for weapon in self.weapons:
            weapon_shots = weapon.get_shots()
            if weapon_shots:
                all_shots.extend(weapon_shots)
        return all_shots

    def get_effects(self):
        """Get all active effects from weapons"""
        return self.laser.effects

    def shoot(self):
        """Handle player shooting - creates shots based on player's weapon setup"""
        if self.player.laser:
            # Use laser weapon for shooting
            for i in range(self.player.shot_no):
                angle_offset = (i - (self.player.shot_no - 1) / 2) * 10
                bullet = Laser_Shot(self.player, self.laser)
                bullet.velocity = pygame.Vector2(0, 1).rotate(self.player.rotation + angle_offset) * self.player.shot_speed * constants.LASER_SPEED_MULT
                bullet.piercing = self.player.piercing
                self.player.current_cooldown = self.player.shot_cooldown + 1 * (self.player.shot_no / 10)
                self.player.current_cooldown *= 2
                # Add laser shot to the sprite groups if containers are set
                if hasattr(bullet, 'add') and hasattr(Shot, 'containers') and Shot.containers:
                    bullet.add(Shot.containers)
        else:
            # Use regular shots
            for i in range(self.player.shot_no):
                angle_offset = (i - (self.player.shot_no - 1) / 2) * 10
                bullet = Shot(self.player.position.x, self.player.position.y, self.player.shot_radius)
                bullet.velocity = pygame.Vector2(0, 1).rotate(self.player.rotation + angle_offset) * self.player.shot_speed
                bullet.piercing = self.player.piercing
                self.player.current_cooldown = self.player.shot_cooldown + 1 * (self.player.shot_no / 10)