import pygame
import constants
import math
import random
from weapon import Weapon
from shot import Shot


class ShockwaveEffect(Shot):
    """The visual effect of the shockwave.

    A line instantly appears from player center to end of screen.
    Vibrating animation lines are parallel to this main line.
    """

    def __init__(self, player, start_pos, direction, width, distance, damage):
        super().__init__(start_pos.x, start_pos.y, 1)
        self.player = player
        # Use the passed start_pos, not player.position, to capture the position at time of firing
        self.start_pos = start_pos.copy()
        self.direction = direction
        self.base_width = width
        self.max_distance = distance
        self.damage = damage
        self.age = 0
        self.lifetime = 0.5

        self.line_width = 2
        self.line_color = (220, 220, 220)

        # Calculate end position: straight line from start_pos in direction for the given distance
        self.end_pos = start_pos + direction * distance

        self.wave_interval = 0.1
        self.next_wave_time = self.wave_interval

        self.active_lines = []

        self.vibration_frequency = 15.0
        self.vibration_amplitude = 3.0

        self.spawn_wave()

    def update(self, dt):
        self.age += dt

        for line_pair in self.active_lines:
            line_pair["phase"] += dt * self.vibration_frequency

        if self.age < self.lifetime:
            self.next_wave_time -= dt
            if self.next_wave_time <= 0:
                self.spawn_wave()
                self.next_wave_time = self.wave_interval

        self.active_lines = [
            pair
            for pair in self.active_lines
            if pair["start_time"] + pair["duration"] > self.age
        ]

        if self.age >= self.lifetime:
            self.kill()

    def spawn_wave(self):
        wave_phase = random.uniform(0, 2 * math.pi)

        for i in range(2):
            line_pair = {
                "offset": (i - 0.5) * self.base_width,
                "phase": wave_phase,
                "start_time": self.age,
                "duration": self.lifetime - self.age,
            }
            self.active_lines.append(line_pair)

    def draw(self, screen):
        for line_pair in self.active_lines:
            if self.age < line_pair["start_time"]:
                continue

            progress = (self.age - line_pair["start_time"]) / line_pair["duration"]

            vibration = math.sin(line_pair["phase"]) * self.vibration_amplitude

            perp_offset = self.direction.rotate(90) * (line_pair["offset"] + vibration)

            start = self.start_pos + perp_offset
            end = self.end_pos + perp_offset

            alpha = int(255 * (1 - progress))
            if alpha > 0:
                color_with_alpha = (
                    self.line_color[0],
                    self.line_color[1],
                    self.line_color[2],
                    alpha,
                )
                pygame.draw.line(screen, color_with_alpha, start, end, self.line_width)

        # Draw the main central line (more opaque, constant)
        pygame.draw.line(screen, self.line_color, self.start_pos, self.end_pos, self.line_width + 1)

    def is_active(self):
        return self.age < self.lifetime

    def check_kill_dist(self, asteroid):
        if not hasattr(asteroid, "position"):
            return False

        start = self.start_pos
        end = self.end_pos
        center = asteroid.position

        line_vec = end - start
        line_len = line_vec.length()
        if line_len == 0:
            return False
        to_center = center - start

        # Project to_center onto line_vec, clamp to segment - same as laser
        t = max(0, min(1, to_center.dot(line_vec) / (line_len**2)))
        closest = start + line_vec * t

        dist = center.distance_to(closest)

        # Same as laser: dist < (width / 2 + radius)
        asteroid_radius = getattr(asteroid, "radius", 20)
        return dist < (self.base_width / 2 + asteroid_radius)


class Shockwave(Weapon):
    """
    Final upgrade for Laser weapon - REPLACES the Laser.
    Fires a pulse in a line from player position in forward direction.
    """

    def __init__(self, player):
        super().__init__(player)
        self.player = player

        self.level = 0
        self.width = 5
        self.distance = constants.GAMEPLAY_HEIGHT  # Use screen height as max distance
        self.damage = 1
        self.cooldown = 0.8
        self.current_cooldown = 0
        self.piercing = 20

        self.color = (220, 220, 220)
        self.active_effects = []
        self.effects = self.active_effects

    def apply_upgrade(self, containers=None, upgrade_type=None):
        self.level += 1

        if self.level <= 3:
            self.width += 8
        elif self.level <= 6:
            self.distance += 100
            self.damage += 1
        else:
            self.cooldown = max(0.3, self.cooldown - 0.1)
            self.width += 5
            self.distance += 50

    def update(self, player, screen, dt):
        self.player = player

        if self.current_cooldown > 0:
            self.current_cooldown -= dt

        for effect in self.active_effects[:]:
            effect.update(dt)
            effect.draw(screen)
            if not effect.is_active():
                self.active_effects.remove(effect)

    def shoot(self):
        if self.current_cooldown > 0:
            return

        self.current_cooldown = self.cooldown

        start_pos = self.player.position.copy()
        # Use same forward direction calculation as player movement/rotation
        direction = pygame.Vector2(0, 1).rotate(self.player.rotation)

        # Calculate the maximum distance to the edge of the gameplay area
        # in the direction the player is facing
        max_distance = self.calculate_max_distance(start_pos, direction)

        effect = ShockwaveEffect(
            self.player, start_pos, direction, self.width, max_distance, self.damage
        )

        self.active_effects.append(effect)

    def check_collision(self, asteroid):
        for effect in self.active_effects:
            if effect.check_kill_dist(asteroid):
                return True
        return False

    def get_shots(self):
        return self.active_effects if self.active_effects else None

    def calculate_max_distance(self, start_pos, direction):
        """Calculate the maximum distance from start_pos in direction to the edge of gameplay area.

        This finds where the ray (start_pos -> direction) intersects the gameplay area boundary.
        """
        # Get the four edges of the gameplay area
        left = 0
        right = constants.GAMEPLAY_WIDTH
        top = 0
        bottom = constants.GAMEPLAY_HEIGHT

        # If direction has no length, return default distance
        if direction.length_squared() == 0:
            return self.distance

        # We need to find the intersection of the ray with the rectangle [left, right] x [top, bottom]
        # Ray equation: P = start_pos + t * direction, where t >= 0
        # We want the smallest t > 0 where P is on the boundary of the gameplay area

        # Instead of checking each edge separately, we can calculate t for x and y boundaries
        tx_min = float("inf")  # t where we hit left or right boundary
        ty_min = float("inf")  # t where we hit top or bottom boundary

        # Calculate t for left boundary (x = left)
        if direction.x != 0:
            t_left = (left - start_pos.x) / direction.x
            if t_left >= 0:
                # Check if y is within bounds at this t
                y = start_pos.y + t_left * direction.y
                if top <= y <= bottom:
                    tx_min = t_left

        # Calculate t for right boundary (x = right)
        if direction.x != 0:
            t_right = (right - start_pos.x) / direction.x
            if t_right >= 0:
                # Check if y is within bounds at this t
                y = start_pos.y + t_right * direction.y
                if top <= y <= bottom:
                    if t_right < tx_min:
                        tx_min = t_right

        # Calculate t for top boundary (y = top)
        if direction.y != 0:
            t_top = (top - start_pos.y) / direction.y
            if t_top >= 0:
                # Check if x is within bounds at this t
                x = start_pos.x + t_top * direction.x
                if left <= x <= right:
                    ty_min = t_top

        # Calculate t for bottom boundary (y = bottom)
        if direction.y != 0:
            t_bottom = (bottom - start_pos.y) / direction.y
            if t_bottom >= 0:
                # Check if x is within bounds at this t
                x = start_pos.x + t_bottom * direction.x
                if left <= x <= right:
                    if t_bottom < ty_min:
                        ty_min = t_bottom

        # Return the minimum t (closest intersection)
        return min(tx_min, ty_min)

    def is_active(self):
        return self.level > 0
