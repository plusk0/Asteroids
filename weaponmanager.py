import pygame
from rotator import Rotator
from emp import Emp

class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.weapons = []
        self.add_default_weapons()
        self.shots = []

    def add_default_weapons(self):
        Rotate = Rotator(self.player)
        boom = Emp(self.player)
        self.weapons.append(Rotate)
        self.weapons.append(boom)
        #Add other weapons here
        pass
    
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



