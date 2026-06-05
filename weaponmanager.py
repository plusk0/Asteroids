import pygame
import constants

from rotator import Rotator
from emp import Emp
from laser import Laser, Laser_Shot
from shot import Shot
from wingmen import Wingmen
from magnetizer import Magnetizer
from shockwave import Shockwave

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
        self.wingmen = Wingmen(self.player)
        self.magnetizer = Magnetizer(self.player)
        
        self.weapons.append(self.rotate)
        self.weapons.append(self.boom)
        self.weapons.append(self.laser)
        self.weapons.append(self.wingmen)
        self.weapons.append(self.magnetizer)
        #Add other weapons here

    def update(self, player, screen, dt):
        for weapon in self.weapons:
            weapon.update(player, screen, dt)

    def apply_upgrade_by_name(self, weapon_name):
        # Check if this is a final upgrade
        for base_weapon_name, final_upgrade_name in constants.FINAL_UPGRADES.items():
            if weapon_name.lower() == final_upgrade_name.lower():
                return self.apply_final_upgrade(base_weapon_name, final_upgrade_name)
        
        # Normal weapon upgrade
        for weapon in self.weapons:
            if weapon.__class__.__name__.lower() == weapon_name.lower():
                if hasattr(weapon, 'apply_upgrade'):
                    # Pass player's containers and upgrade name if available
                    player_containers = getattr(self.player, 'containers', None)
                    weapon.apply_upgrade(player_containers, upgrade_type=weapon_name)
                return True
        return False
    
    def apply_final_upgrade(self, base_weapon_name, final_upgrade_name):
        """Apply a final upgrade to a base weapon - REPLACES the base weapon"""
        # Find the base weapon
        base_weapon = None
        base_index = -1
        for i, weapon in enumerate(self.weapons):
            if weapon.__class__.__name__.lower() == base_weapon_name.lower():
                base_weapon = weapon
                base_index = i
                break
        
        if not base_weapon:
            return False
        
        # Check if final weapon already exists
        final_weapon = None
        for weapon in self.weapons:
            if weapon.__class__.__name__.lower() == final_upgrade_name.lower():
                final_weapon = weapon
                break
        
        if not final_weapon:
            # Create new final weapon to REPLACE the base weapon
            if final_upgrade_name.lower() == "shockwave":
                final_weapon = Shockwave(self.player)
                # Transfer level from base weapon to final weapon
                final_weapon.level = base_weapon.level
                # Remove base weapon and add final weapon in its place
                self.weapons[base_index] = final_weapon
                # Update references
                if base_weapon_name.lower() == "laser":
                    self.laser = final_weapon
            else:
                return False
        else:
            # Final weapon already exists - just upgrade it
            player_containers = getattr(self.player, 'containers', None)
            final_weapon.apply_upgrade(player_containers)
            return True
        
        # Apply the first upgrade to the final weapon (since it replaces the base)
        player_containers = getattr(self.player, 'containers', None)
        final_weapon.apply_upgrade(player_containers)
        return True
    
    def check_final_upgrade_available(self, weapon_name):
        """Check if a final upgrade is available for a weapon"""
        if weapon_name not in constants.FINAL_UPGRADES:
            return False
        
        # Find the base weapon
        base_weapon = None
        for weapon in self.weapons:
            if weapon.__class__.__name__.lower() == weapon_name.lower():
                base_weapon = weapon
                break
        
        if not base_weapon:
            return False
        
        # Check if the weapon has reached the required level
        final_weapon_name = constants.FINAL_UPGRADES[weapon_name]
        condition = constants.FINAL_UPGRADE_CONDITIONS.get(weapon_name, {})
        
        if condition.get("type") == "weapon_level":
            return base_weapon.level >= condition.get("level", 3)
        
        # Add more condition types here as needed
        return False
    
    def get_available_upgrades(self, player=None):
        """Get list of available upgrades including final upgrades, excluding locked ones"""
        available = []
        
        # Get all possible upgrades
        all_upgrades = []
        all_upgrades.extend(constants.UPGRADES)
        all_upgrades.extend(constants.WEAPONS)
        all_upgrades.extend(constants.SPECIAL_UPGRADES)
        
        # Check for final upgrades
        for weapon_name, final_upgrade_name in constants.FINAL_UPGRADES.items():
            if self.check_final_upgrade_available(weapon_name):
                all_upgrades.append(final_upgrade_name)
        
        # Filter out locked upgrades
        locked_upgrades = set()
        if player and hasattr(player, 'locked_upgrades'):
            locked_upgrades = player.locked_upgrades
        
        for upgrade in all_upgrades:
            # Check if upgrade is locked
            if upgrade in locked_upgrades:
                continue
            
            # Check per-round unlock requirements
            if not self._check_upgrade_requirements(upgrade, player):
                continue
            
            available.append(upgrade)
        
        return available
    
    def _check_upgrade_requirements(self, upgrade, player):
        """Check if an upgrade meets its per-round requirements"""
        if player is None:
            return True
        
        rules = constants.UPGRADE_RULES.get(upgrade, {})
        requires = rules.get("requires", None)
        
        if requires is None:
            return True
        
        # Check requirement type
        req_type = requires.get("type")
        
        if req_type == "weapon_level":
            weapon_name = requires.get("weapon")
            required_level = requires.get("level", 1)
            
            # Find the weapon in weapon_manager
            for weapon in self.weapons:
                if weapon.__class__.__name__.lower() == weapon_name.lower():
                    return weapon.level >= required_level
            return False
        
        elif req_type == "upgrade_owned":
            required_upgrade = requires.get("upgrade")
            return required_upgrade in getattr(player, 'owned_upgrades', set())
        
        elif req_type == "stat_value":
            stat_name = requires.get("stat")
            required_value = requires.get("value")
            comparison = requires.get("comparison", ">=")
            
            stat_value = getattr(player, stat_name, 0)
            
            if comparison == ">=":
                return stat_value >= required_value
            elif comparison == "":
                return stat_value <= required_value
            elif comparison == "==":
                return stat_value == required_value
            elif comparison == "":
                return stat_value > required_value
            elif comparison == "<":
                return stat_value < required_value
        
        return True

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
        # Return effects from laser if it exists and has effects attribute
        if hasattr(self, 'laser') and self.laser and hasattr(self.laser, 'effects'):
            return self.laser.effects
        # Check for shockwave (which replaces laser)
        if hasattr(self, 'laser') and self.laser and hasattr(self.laser, 'active_effects'):
            # Shockwave uses active_effects instead of effects
            return self.laser.active_effects
        return []

    def shoot(self):
        """Handle player shooting - creates shots based on player's weapon setup"""
        # Check if we have a shockwave weapon (replaces laser)
        shockwave_weapon = None
        for weapon in self.weapons:
            if weapon.__class__.__name__.lower() == "shockwave":
                shockwave_weapon = weapon
                break
        
        if shockwave_weapon and shockwave_weapon.level > 0:
            # Use shockwave shooting mechanism
            if shockwave_weapon.current_cooldown <= 0:
                shockwave_weapon.shoot()
                shockwave_weapon.current_cooldown = shockwave_weapon.cooldown
            return
        elif self.player.laser:
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