import pygame
from rotator import Rotator

class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.weapons = []
        self.add_default_weapons()

    def add_default_weapons(self):
        Rotate = Rotator(self.player)
        self.weapons.append(Rotate)
        print("Default weapons added to WeaponManager")
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
        shots = []
        for weapon in self.weapons:
            if hasattr(weapon, "shots"):
                shots.extend(weapon.shots)
        return shots



