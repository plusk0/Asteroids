import pygame
import constants
import math
from weapon import Weapon
from shot import Shot


class ShockwaveEffect(Shot):
    """The visual effect of the shockwave that damages asteroids in a line"""

    def __init__(self, player, start_pos, direction, width, distance, damage):
        # Start with minimal radius, will grow
        super().__init__(start_pos.x, start_pos.y, 1)
        self.player = player
        self.start_pos = start_pos.copy()
        self.direction = direction
        self.base_width = width
        self.max_distance = distance
        self.damage = damage
        self.age = 0
        self.lifetime = 1.0  # Lasts 1 second
        self.max_width = width * 3  # Grows to 3x initial width
        self.color = (255, 80, 80)  # Red like magnetizer
        self.speed = constants.SHOT_SPEED * 2

    def draw(self, screen):
        # Calculate current extent
        current_distance = min(self.max_distance, self.speed * self.age)
        current_width = min(self.max_width, self.base_width * (1 + self.age * 2))

        end_pos = self.start_pos + self.direction * current_distance

        # Draw multiple lines for magnetizer-like effect
        for i in range(3):
            offset = self.direction.rotate(90) * (i - 1) * 5
            start = self.start_pos + offset
            end = end_pos + offset
            pygame.draw.line(
                screen, self.color, start, end, max(1, current_width - i * 2)
            )

    def update(self, dt):
        self.age += dt

        if self.age >= self.lifetime:
            self.kill()

    def is_active(self):
        return self.age < self.lifetime


class Shockwave(Weapon):
    """
    Final upgrade for Laser weapon - REPLACES the Laser.
    Fires a pulse that damages all asteroids in a line without stopping.
    The effect gets wider as time passes with multiple lines (like a red magnetizer).
    """

    def __init__(self, player):
        super().__init__(player)
        self.player = player

        # Properties - shockwave replaces laser
        self.level = 0
        self.width = 20  # Starting width
        self.distance = 1000  # Distance shockwave travels
        self.damage = 1  # Damage per hit
        self.cooldown = 0.8  # Seconds between shots
        self.current_cooldown = 0
        self.piercing = 10  # Very high piercing - doesn't stop

        # Visual properties - red like magnetizer
        self.color = (255, 50, 50)
        self.active_effects = []

    def apply_upgrade(self, containers=None):
        """Upgrade the shockwave weapon"""
        self.level += 1

        if self.level <= 3:
            self.width += 8  # Wider shockwave
        elif self.level <= 6:
            self.distance += 100  # Longer reach
            self.damage += 1  # More damage
        else:
            self.cooldown = max(0.3, self.cooldown - 0.1)  # Faster cooldown
            self.width += 5
            self.distance += 50

    def update(self, player, screen, dt):
        """Update shockwave effects and cooldown"""
        self.player = player

        # Update cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= dt

        # Update and draw active effects
        for effect in self.active_effects[:]:
            effect.update(dt)
            effect.draw(screen)
            if not effect.is_active():
                self.active_effects.remove(effect)

    def shoot(self):
        """Fire a shockwave pulse"""
        if self.current_cooldown > 0:
            return

        self.current_cooldown = self.cooldown

        # Create shockwave effect
        start_pos = self.player.position.copy()
        direction = pygame.Vector2(0, 1).rotate(self.player.rotation)

        effect = ShockwaveEffect(
            self.player, start_pos, direction, self.width, self.distance, self.damage
        )

        # Add to sprite groups
        if hasattr(Shot, "containers") and Shot.containers:
            effect.add(Shot.containers)

        self.active_effects.append(effect)

    def check_collision(self, asteroid):
        """Check if asteroid is hit by any active shockwave"""
        for effect in self.active_effects:
            if self.check_asteroid_collision(asteroid, effect):
                return True
        return False

    def check_asteroid_collision(self, asteroid, effect):
        """Check if asteroid collides with a shockwave effect"""
        if not hasattr(asteroid, "position"):
            return False

        # Calculate current extent
        current_distance = min(effect.max_distance, effect.speed * effect.age)
        current_width = min(effect.max_width, effect.base_width * (1 + effect.age * 2))

        start_pos = effect.start_pos
        end_pos = start_pos + effect.direction * current_distance

        # Calculate distance from asteroid to line
        line_vec = end_pos - start_pos
        asteroid_vec = asteroid.position - start_pos

        if line_vec.length() == 0:
            return False

        # Project asteroid position onto line
        t = max(0, min(1, asteroid_vec.dot(line_vec) / line_vec.length_squared()))
        closest_point = start_pos + line_vec * t

        # Check if within width/2 + asteroid radius
        distance = (asteroid.position - closest_point).length()
        return distance < (current_width / 2 + getattr(asteroid, "radius", 20))

    def get_shots(self):
        """Return active shockwave effects as shots"""
        return self.active_effects if self.active_effects else None

    def is_active(self):
        """Check if shockwave is active"""
        return self.level > 0

