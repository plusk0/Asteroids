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
        self.start_pos = player.position.copy()
        self.direction = direction
        self.base_width = width
        self.max_distance = distance
        self.damage = damage
        self.age = 0
        self.lifetime = 0.5

        self.line_width = 2
        self.line_color = (220, 220, 220)

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
                line_length = start.distance_to(end)
                if line_length > 0:
                    s = pygame.Surface(
                        (int(line_length) + 2, self.line_width + 2), pygame.SRCALPHA
                    )
                    pygame.draw.line(
                        s,
                        color_with_alpha,
                        (0, self.line_width // 2),
                        (int(line_length), self.line_width // 2),
                        self.line_width,
                    )
                    angle = math.degrees(math.atan2(end.y - start.y, end.x - start.x))
                    rotated = pygame.transform.rotate(s, angle)
                    screen.blit(
                        rotated,
                        (
                            start.x - rotated.get_width() // 2,
                            start.y - rotated.get_height() // 2,
                        ),
                    )

    def is_active(self):
        return self.age < self.lifetime

    def check_kill_dist(self, asteroid):
        if not hasattr(asteroid, "position"):
            return False

        line_vec = self.end_pos - self.start_pos
        asteroid_vec = asteroid.position - self.start_pos

        if line_vec.length() == 0:
            return False

        t = max(0, min(1, asteroid_vec.dot(line_vec) / line_vec.length_squared()))
        closest_point = self.start_pos + line_vec * t

        distance = (asteroid.position - closest_point).length()
        return distance < (self.base_width / 2 + getattr(asteroid, "radius", 20))


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
        self.distance = 1000
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
        direction = pygame.Vector2(0, 1).rotate(-self.player.rotation)

        effect = ShockwaveEffect(
            self.player, start_pos, direction, self.width, self.distance, self.damage
        )

        self.active_effects.append(effect)

    def check_collision(self, asteroid):
        for effect in self.active_effects:
            if effect.check_kill_dist(asteroid):
                return True
        return False

    def get_shots(self):
        return self.active_effects if self.active_effects else None

    def is_active(self):
        return self.level > 0
