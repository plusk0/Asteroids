import pygame
import constants
import random
import math
from circleshape import CircleShape
from shot import Shot
from weapon import Weapon


class WingmanShot(Shot):
    """Shot fired by wingmen"""

    def __init__(self, x, y, radius, wingman):
        super().__init__(x, y, radius)
        self.wingman = wingman
        self.color = (200, 255, 255)  # Cyan color
        self.piercing = 0
        self.lifetime = 2.0
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        pygame.draw.circle(screen, self.color, self.position, self.radius * 1.5, 1)

    def update(self, dt):
        self.position += dt * self.velocity
        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.spawn_time) / 1000.0
        if elapsed > self.lifetime:
            self.kill()
            return
        if (
            self.position.y < -constants.SCREEN_HEIGHT
            or self.position.y > constants.SCREEN_HEIGHT
            or self.position.x < -constants.SCREEN_WIDTH
            or self.position.x > constants.SCREEN_WIDTH
        ):
            self.kill()


class Wingman(CircleShape):
    """A wingman that follows the player and attacks nearby asteroids"""

    def __init__(
        self,
        x,
        y,
        wingmen_weapon,
        wingman_id=0,
        role=constants.WINGMEN_FORMATION_CLOSE_FOLLOW,
    ):
        # Set radius to 1/2 of player radius - use circular placeholders for debugging
        radius = constants.PLAYER_RADIUS / 2
        super().__init__(x, y, radius)
        self.wingmen_weapon = wingmen_weapon
        self.player = wingmen_weapon.player
        self.wingman_id = wingman_id
        self.radius = radius
        self.role = role  # Formation role: 0=Scouting, 1=Close Follow, 2=Radar Follow

        # Different colors for different roles
        role_colors = {
            constants.WINGMEN_FORMATION_SCOUTING: (255, 200, 100),  # Orange
            constants.WINGMEN_FORMATION_CLOSE_FOLLOW: (100, 200, 255),  # Light blue
            constants.WINGMEN_FORMATION_RADAR_FOLLOW: (200, 100, 200),  # Purple
        }
        self.color = role_colors.get(role, (200, 200, 255))

        self.speed = constants.WINGMEN_BASE_SPEED
        self.base_follow_distance = 40 + (wingman_id * 20)
        self.follow_distance = self.base_follow_distance

        self.fire_cooldown = constants.WINGMEN_BASE_FIRE_COOLDOWN

        # Formation-specific properties
        self.scout_points = []
        self.scout_point_index = 0
        self.scout_timer = 0

        # For proper rotation
        self.prev_position = pygame.Vector2(x, y)
        self.facing_angle = 0

        self.target = None
        self.current_fire_cooldown = 0

        # Intelligence mode (intercept vs follow-behind)
        self.intercept_mode = False

        self.position = pygame.Vector2(x, y)
        self.orbit_angle = random.uniform(0, 360)

        self.behind_position = None

        self.set_formation_behavior()

    def set_formation_behavior(self):
        """Set formation-specific behavior based on role"""
        if self.role == constants.WINGMEN_FORMATION_SCOUTING:
            self.generate_scout_points()
            self.follow_distance = self.base_follow_distance * 3
        elif self.role == constants.WINGMEN_FORMATION_CLOSE_FOLLOW:
            self.follow_distance = self.base_follow_distance
        elif self.role == constants.WINGMEN_FORMATION_RADAR_FOLLOW:
            self.follow_distance = constants.EMP_RADIUS * 2

    def generate_scout_points(self, count=4):
        """Generate random patrol points for Scouting formation"""
        self.scout_points = []
        for i in range(count):
            angle = i * (360 / count)
            distance = random.randint(100, 200)
            offset = pygame.Vector2(0, -distance).rotate(angle)
            # Will be relative to player position when used
            self.scout_points.append(offset)
        self.scout_point_index = 0
        self.scout_timer = random.uniform(1, 3)  # Change target every 2-5 seconds

    def update(self, dt):
        if not hasattr(self, "player") or self.player is None:
            return

        # Update cooldown
        if self.current_fire_cooldown > 0:
            self.current_fire_cooldown -= dt

        # Store previous position for rotation calculation
        self.prev_position = self.position.copy()

        # Find nearby asteroids
        self.find_target()

        # Movement behavior
        if self.target:
            self.attack_behavior(dt)
        else:
            self.follow_behavior(dt)

        # Update facing angle based on movement direction
        if self.position != self.prev_position:
            movement = self.position - self.prev_position
            if movement.length() > 0:
                forward = pygame.Vector2(0, 1)  # down
                self.facing_angle = forward.angle_to(movement)

    def find_target(self):
        """Find closest asteroid from wingman that is also within max distance from player.

        Wingmen will follow the closest asteroid from themselves that is:
        - Within max_player_distance from the player (formation-dependent)
        - Within 1.5x max_player_distance from the wingman for tracking
        - The asteroid is the closest valid one to the wingman
        """
        closest = None
        closest_dist = float("inf")

        # Get formation-dependent max distance from player for asteroid to be valid target
        max_player_distance = constants.WINGMEN_MAX_ATTACK_DISTANCE.get(self.role, 300)
        max_wingman_distance = max_player_distance * 1.5  # Can track up to 1.5x

        asteroids = self.get_asteroids()
        for asteroid in asteroids:
            if hasattr(asteroid, "alive") and not asteroid.alive():
                continue

            # Check distance from player to asteroid (formation-dependent) - asteroid must be within range of player
            if hasattr(self, "player") and self.player:
                player_to_asteroid = self.player.position.distance_to(asteroid.position)
                if player_to_asteroid > max_player_distance:
                    continue

            # Check distance from wingman to asteroid - can be up to 1.5x max distance for tracking
            wingman_to_asteroid = self.position.distance_to(asteroid.position)
            if (
                wingman_to_asteroid > max_wingman_distance
            ):  # Use formation-dependent max
                continue

            if wingman_to_asteroid < closest_dist:
                closest_dist = wingman_to_asteroid
                closest = asteroid

        self.target = closest

    def get_asteroids(self):
        """Get asteroids from weapon reference"""
        if hasattr(self.wingmen_weapon, "asteroids") and self.wingmen_weapon.asteroids:
            return list(self.wingmen_weapon.asteroids)
        return []

    def follow_behavior(self, dt):
        """Follow player based on formation type"""
        if self.role == constants.WINGMEN_FORMATION_SCOUTING:
            # Scouting: patrol between random points around player
            self.scout_behavior(dt)
        elif self.role == constants.WINGMEN_FORMATION_RADAR_FOLLOW:
            # Radar Follow: circle in large formation
            self.orbit_angle += dt * 20
            self.orbit_angle %= 360
            target_pos = self.player.position + pygame.Vector2(
                0, -self.follow_distance
            ).rotate(self.orbit_angle)
            direction = (target_pos - self.position).normalize()
            distance = self.position.distance_to(target_pos)
            if distance > 5:
                self.position += direction * self.speed * dt
        else:
            # Close Follow (default): tight orbit
            self.orbit_angle += dt * 30
            self.orbit_angle %= 360
            target_pos = self.player.position + pygame.Vector2(
                0, -self.follow_distance
            ).rotate(self.orbit_angle)
            direction = (target_pos - self.position).normalize()
            distance = self.position.distance_to(target_pos)
            if distance > 5:
                self.position += direction * self.speed * dt

    def scout_behavior(self, dt):
        """Patrol between random points around the player"""
        # Update scout timer
        self.scout_timer -= dt

        if self.scout_timer <= 0 or not self.scout_points:
            # Generate new points or reset timer
            self.generate_scout_points()
            self.scout_timer = random.uniform(2, 5)
            self.scout_point_index = 0

        # Get current target point (relative to player)
        target_offset = self.scout_points[self.scout_point_index]
        target_pos = self.player.position + target_offset

        # Move towards target
        direction = (target_pos - self.position).normalize()
        distance = self.position.distance_to(target_pos)

        if distance > 10:
            self.position += direction * self.speed * dt
        else:
            # Reached target, move to next point
            self.scout_point_index = (self.scout_point_index + 1) % len(
                self.scout_points
            )

    def attack_behavior(self, dt):
        """Follow asteroid and shoot - mode depends on intelligence"""
        if not self.target or (
            hasattr(self.target, "alive") and not self.target.alive()
        ):
            self.target = None
            self.behind_position = None
            return

        asteroid = self.target
        asteroid_radius = getattr(asteroid, "radius", 20)

        # Get formation-dependent max distance from player
        max_player_distance = constants.WINGMEN_MAX_ATTACK_DISTANCE.get(self.role, 200)
        distance_from_player = self.position.distance_to(self.player.position)

        # Keep following asteroid up to 1.5 times the max distance from player
        # At 1.5x distance, start flying back to waiting position
        if distance_from_player > max_player_distance * 1.5:
            self.return_to_player(dt)
            return

        if self.intercept_mode:
            # Intelligence mode: choose best position (front or back)
            self.smart_attack_behavior(dt, asteroid, asteroid_radius)
        else:
            # Normal mode: get behind asteroid, follow it, then shoot
            self.follow_behind_behavior(dt, asteroid, asteroid_radius)

    def return_to_player(self, dt):
        """Fly back to player formation instead of teleporting"""

        if self.role == constants.WINGMEN_FORMATION_SCOUTING:
            if self.scout_points and len(self.scout_points) > 0:
                target_offset = self.scout_points[self.scout_point_index]
                target_pos = self.player.position + target_offset
            else:
                # Fallback to orbit if no patrol points
                self.orbit_angle += dt * 30
                self.orbit_angle %= 360
                target_pos = self.player.position + pygame.Vector2(
                    0, -self.follow_distance
                ).rotate(self.orbit_angle)
        elif self.role == constants.WINGMEN_FORMATION_RADAR_FOLLOW:
            self.orbit_angle += dt * 20
            self.orbit_angle %= 360
            target_pos = self.player.position + pygame.Vector2(
                0, -self.follow_distance
            ).rotate(self.orbit_angle)
        else:
            # Close follow orbit position
            self.orbit_angle += dt * 30
            self.orbit_angle %= 360
            target_pos = self.player.position + pygame.Vector2(
                0, -self.follow_distance
            ).rotate(self.orbit_angle)

        max_player_distance = constants.WINGMEN_MAX_ATTACK_DISTANCE.get(self.role, 300)
        max_intercept_distance = max_player_distance * 1.5

        distance_from_player = self.position.distance_to(self.player.position)

        if distance_from_player > max_intercept_distance:
            direction = (target_pos - self.position).normalize()
            distance_to_target = self.position.distance_to(target_pos)

            if distance_to_target > 5:
                self.position += direction * self.speed * dt
        else:
            asteroids = self.get_asteroids()
            closest_asteroid = None
            closest_dist = float("inf")

            for asteroid in asteroids:
                if hasattr(asteroid, "alive") and not asteroid.alive():
                    continue

                player_to_asteroid = self.player.position.distance_to(asteroid.position)
                if player_to_asteroid <= max_player_distance:
                    wingman_to_asteroid = self.position.distance_to(asteroid.position)
                    if wingman_to_asteroid < closest_dist:
                        closest_dist = wingman_to_asteroid
                        closest_asteroid = asteroid

            if closest_asteroid and closest_dist < 300:
                self.target = closest_asteroid
                return

            direction = (target_pos - self.position).normalize()
            distance_to_target = self.position.distance_to(target_pos)

            if distance_to_target > 5:
                self.position += direction * self.speed * dt

    def smart_attack_behavior(self, dt, asteroid, asteroid_radius):
        """Intelligence mode: Only shoot from front if distance from front is smaller than from behind"""
        # Calculate distances for both front and back positions
        if hasattr(asteroid, "velocity") and asteroid.velocity.length() > 0:
            velocity_dir = asteroid.velocity.normalize()

            # Position behind asteroid
            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            behind_pos = asteroid.position - velocity_dir * distance_behind
            dist_to_behind = self.position.distance_to(behind_pos)

            # Position in front of asteroid
            distance_ahead = asteroid_radius * 2.5 + self.radius * 3
            front_pos = asteroid.position + velocity_dir * distance_ahead
            dist_to_front = self.position.distance_to(front_pos)

            if dist_to_front < dist_to_behind:
                direction = (front_pos - self.position).normalize()
                if dist_to_front > 20:
                    self.position += direction * self.speed * dt

                if dist_to_front < 60 and self.current_fire_cooldown <= 0:
                    shoot_dir = (asteroid.position - self.position).normalize()
                    self.shoot_with_direction(shoot_dir)
                    self.current_fire_cooldown = self.fire_cooldown
            else:
                direction = (behind_pos - self.position).normalize()
                if dist_to_behind > 20:
                    self.position += direction * self.speed * dt

                if dist_to_behind < 30 and self.current_fire_cooldown <= 0:
                    shoot_dir = (asteroid.position - self.position).normalize()
                    self.shoot_with_direction(shoot_dir)
                    self.current_fire_cooldown = self.fire_cooldown
        else:
            # Fallback for asteroid with no velocity - move to behind and shoot
            direction = (asteroid.position - self.position).normalize()
            distance = self.position.distance_to(asteroid.position)

            # Position behind at offset proportional to sizes
            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            self.behind_position = asteroid.position - direction * distance_behind
            self.position += (
                (self.behind_position - self.position).normalize() * self.speed * dt
            )

            if distance < 100 and self.current_fire_cooldown <= 0:
                self.shoot()
                self.current_fire_cooldown = self.fire_cooldown

    def follow_behind_behavior(self, dt, asteroid, asteroid_radius):
        """Get behind asteroid, follow it, then shoot (normal mode)"""
        if hasattr(asteroid, "velocity") and asteroid.velocity.length() > 0:
            velocity_dir = asteroid.velocity.normalize()

            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            self.behind_position = asteroid.position - velocity_dir * distance_behind

            direction = (self.behind_position - self.position).normalize()
            distance_to_behind = self.position.distance_to(self.behind_position)

            if distance_to_behind > 40:
                self.position += direction * self.speed * dt

            if distance_to_behind < 50 and self.current_fire_cooldown <= 0:
                # Shoot at the asteroid from behind
                shoot_dir = (asteroid.position - self.position).normalize()
                self.shoot_with_direction(shoot_dir)
                self.current_fire_cooldown = self.fire_cooldown
        else:
            # Fallback if asteroid has no velocity
            direction = (asteroid.position - self.position).normalize()
            distance = self.position.distance_to(asteroid.position)

            # Position behind at offset proportional to sizes
            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            self.behind_position = asteroid.position - direction * distance_behind
            self.position += (
                (self.behind_position - self.position).normalize() * self.speed * dt
            )

            if distance < 100 and self.current_fire_cooldown <= 0:
                self.shoot()
                self.current_fire_cooldown = self.fire_cooldown

    def intercept_behavior(self, dt, asteroid, asteroid_radius):
        """Intercept asteroid - move to front and shoot (intelligence mode)

        This allows wingmen to shoot from the front of an asteroid at an increased
        distance, as the asteroid can't outrun the shot.
        """
        if hasattr(asteroid, "velocity") and asteroid.velocity.length() > 0:
            # Get normalized velocity direction
            velocity_dir = asteroid.velocity.normalize()
            # Position in FRONT of asteroid (same direction as velocity)
            # Increased distance for intercept
            distance_ahead = asteroid_radius * 2.5 + self.radius * 3
            self.behind_position = asteroid.position + velocity_dir * distance_ahead

            # Move towards intercept position
            direction = (self.behind_position - self.position).normalize()
            distance_to_position = self.position.distance_to(self.behind_position)

            # Move towards intercept position
            if distance_to_position > 20:
                self.position += direction * self.speed * dt

            # If we're close enough, shoot at the asteroid from front
            if distance_to_position < 40 and self.current_fire_cooldown <= 0:
                # Shoot at the asteroid from front
                shoot_dir = (asteroid.position - self.position).normalize()
                self.shoot_with_direction(shoot_dir)
                self.current_fire_cooldown = self.fire_cooldown
        else:
            # Fallback if asteroid has no velocity - move to front
            direction = (asteroid.position - self.position).normalize()
            distance = self.position.distance_to(asteroid.position)

            # Position ahead at offset proportional to sizes
            distance_ahead = asteroid_radius * 2.5 + self.radius * 3
            self.behind_position = asteroid.position + direction * distance_ahead
            self.position += (
                (self.behind_position - self.position).normalize() * self.speed * dt
            )

            if distance < 120 and self.current_fire_cooldown <= 0:
                self.shoot()
                self.current_fire_cooldown = self.fire_cooldown

    def shoot(self):
        """Fire at target"""
        if not self.target:
            return

        direction = (self.target.position - self.position).normalize()
        self.shoot_with_direction(direction)

    def shoot_with_direction(self, direction):
        """Fire in a specific direction"""
        shot = WingmanShot(
            self.position.x, self.position.y, constants.SHOT_RADIUS * 0.5, self
        )
        shot.velocity = direction * constants.WINGMEN_SHOT_SPEED
        shot.piercing = self.wingmen_weapon.piercing

        if hasattr(Shot, "containers") and Shot.containers:
            shot.add(Shot.containers)

    def draw(self, screen):
        # Use player sprites at half size, rotated in flight direction
        if (
            hasattr(self.player, "sprites")
            and self.player.sprites
            and len(self.player.sprites) > 0
        ):
            try:
                # Calculate animation frame based on orbit angle
                sprite_index = int(self.orbit_angle / 10) % len(self.player.sprites)
                sprite = self.player.sprites[sprite_index]

                # Scale to 1/2 size of player
                scale_factor = 0.5
                scaled_sprite = pygame.transform.scale(
                    sprite,
                    (
                        int(sprite.get_width() * scale_factor),
                        int(sprite.get_height() * scale_factor),
                    ),
                )

                # Rotate to face flight direction (facing_angle)
                if self.facing_angle is not None:
                    rotated = pygame.transform.rotate(scaled_sprite, -self.facing_angle + 180)
                else:
                    rotated = scaled_sprite

                # Blit the sprite centered on position
                screen.blit(
                    rotated,
                    (
                        self.position.x - rotated.get_width() / 2,
                        self.position.y - rotated.get_height() / 2,
                    ),
                )

                # Draw role indicator (small circle with role color)
                if hasattr(self, "role"):
                    pygame.draw.circle(
                        screen,
                        self.color,
                        (self.position.x, self.position.y - self.radius - 10),
                        3,
                    )
            except Exception as e:
                # If there's any error with sprite drawing, fall back to circle
                print(f"Error drawing wingman sprite: {e}")
                pygame.draw.circle(screen, self.color, self.position, self.radius)
                pygame.draw.circle(
                    screen, (255, 255, 255), self.position, self.radius, 1
                )
                if self.facing_angle is not None:
                    direction_vec = pygame.Vector2(0, -1).rotate(self.facing_angle)
                    end_pos = self.position + direction_vec * self.radius
                    pygame.draw.line(screen, (255, 255, 255), self.position, end_pos, 2)
        else:
            # Fallback to circle if no sprites available
            pygame.draw.circle(screen, self.color, self.position, self.radius)
            pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius, 1)

            # Draw direction indicator for debugging
            if self.facing_angle is not None:
                direction_vec = pygame.Vector2(0, -1).rotate(self.facing_angle)
                end_pos = self.position + direction_vec * self.radius
                pygame.draw.line(screen, (255, 255, 255), self.position, end_pos, 2)


class Wingmen(Weapon):
    """Weapon that manages wingmen fighters"""

    def __init__(self, player):
        super().__init__(player)
        self.player = player
        self.wingmen_list = []
        self.level = 0  # Start at level 0
        self.wingmen_count = 0
        self.piercing = 0
        self.formation = constants.WINGMEN_FORMATION_CLOSE_FOLLOW  # Default formation

        # Formation unlock state
        self.formations_unlocked = False
        self.maneuvers_unlocked = False

        # Wingman stat upgrades
        self.speed_upgrade_level = 0  # Level of Wingman Speed upgrade
        self.fire_rate_upgrade_level = 0  # Level of Wingman Fire Rate upgrade
        self.intelligence_unlocked = False  # Whether Wingman Intelligence is unlocked

        # Role distribution (for Basic Fighter Maneuvers)
        # Stores count of wingmen in each role
        self.role_counts = {
            constants.WINGMEN_FORMATION_SCOUTING: 0,
            constants.WINGMEN_FORMATION_CLOSE_FOLLOW: 0,
            constants.WINGMEN_FORMATION_RADAR_FOLLOW: 0,
        }

    def spawn_wingmen(self):
        """Spawn wingmen - similar to rotator weapon"""
        # Clear existing wingmen
        for w in self.wingmen_list:
            if hasattr(w, "kill"):
                w.kill()
        self.wingmen_list = []

        # Get containers from player class
        containers = getattr(self.player, "containers", None)

        # Spawn new wingmen with appropriate roles
        for i in range(self.wingmen_count):
            # Determine role based on distribution if maneuvers unlocked
            if self.maneuvers_unlocked:
                role = self.get_role_for_wingman(i)
            else:
                # Use default formation
                role = self.formation

            w = Wingman(self.player.position.x, self.player.position.y, self, i, role)
            self.wingmen_list.append(w)
            # Add to containers if available
            if containers and hasattr(w, "add"):
                w.add(containers)

    def get_role_for_wingman(self, wingman_index):
        """Get role for a wingman based on distribution"""
        # If formations unlocked, use the formation as base
        role = self.formation

        # If maneuvers unlocked, use role distribution
        if self.maneuvers_unlocked:
            # Distribute wingmen according to role_counts
            total = sum(self.role_counts.values())
            if total > 0:
                # Assign roles proportionally
                role_order = [
                    constants.WINGMEN_FORMATION_SCOUTING,
                    constants.WINGMEN_FORMATION_CLOSE_FOLLOW,
                    constants.WINGMEN_FORMATION_RADAR_FOLLOW,
                ]
                for role_id in role_order:
                    if self.role_counts[role_id] > 0:
                        return role_id
                return self.formation

        return role

    def set_formation(self, formation_id):
        """Set the default formation for all wingmen"""
        self.formation = formation_id
        self.spawn_wingmen()

    def increment_role_count(self, role_id):
        """Increment count for a specific role"""
        total_wingmen = self.wingmen_count
        if sum(self.role_counts.values()) < total_wingmen:
            self.role_counts[role_id] = self.role_counts.get(role_id, 0) + 1
            self.spawn_wingmen()

    def decrement_role_count(self, role_id):
        """Decrement count for a specific role"""
        if self.role_counts[role_id] > 0:
            self.role_counts[role_id] -= 1
            self.spawn_wingmen()

    def unlock_formations(self):
        """Unlock formation selection"""
        self.formations_unlocked = True

    def unlock_maneuvers(self):
        """Unlock Basic Fighter Maneuvers (role distribution)"""
        self.maneuvers_unlocked = True
        # Initialize role counts based on current wingmen count
        total = self.wingmen_count
        for role_id in self.role_counts:
            self.role_counts[role_id] = total // 3  # Distribute evenly initially
        # Add any remainder to first role
        self.role_counts[constants.WINGMEN_FORMATION_SCOUTING] += total % 3
        self.spawn_wingmen()

    def apply_upgrade(self, containers=None, upgrade_type=None):
        """Upgrade wingmen weapon"""
        # Handle specific wingman upgrade types
        if upgrade_type in [
            "Wingman Speed",
            "Wingman Fire Rate",
            "Wingman Intelligence",
        ]:
            if upgrade_type == "Wingman Speed":
                self.apply_speed_upgrade()
            elif upgrade_type == "Wingman Fire Rate":
                self.apply_fire_rate_upgrade()
            elif upgrade_type == "Wingman Intelligence":
                self.apply_intelligence_upgrade()
            return

        # Default: upgrade the wingmen weapon level
        self.level += 1

        # Level 1: 1 wingman
        if self.level == 1:
            self.wingmen_count = 1
        # Every 5 levels: add another wingman (up to max)
        elif self.level % 5 == 0:
            self.wingmen_count = min(6, self.wingmen_count + 1)

        self.spawn_wingmen()

    def apply_speed_upgrade(self):
        """Apply Wingman Speed upgrade"""
        self.speed_upgrade_level += 1
        # Update all wingmen with new speed
        for w in self.wingmen_list:
            w.speed = constants.WINGMEN_BASE_SPEED + (
                constants.WINGMEN_SPEED_INCREMENT * self.speed_upgrade_level
            )

    def apply_fire_rate_upgrade(self):
        """Apply Wingman Fire Rate upgrade"""
        self.fire_rate_upgrade_level += 1
        # Update all wingmen with new fire cooldown
        for w in self.wingmen_list:
            w.fire_cooldown = max(
                0.1,
                constants.WINGMEN_BASE_FIRE_COOLDOWN
                - (
                    constants.WINGMEN_FIRE_RATE_INCREMENT * self.fire_rate_upgrade_level
                ),
            )

    def apply_intelligence_upgrade(self):
        """Apply Wingman Intelligence upgrade (one-time)"""
        self.intelligence_unlocked = True
        # Update all wingmen to use intercept mode
        for w in self.wingmen_list:
            w.intercept_mode = True

    def update(self, player, screen, dt):
        """Update all wingmen"""
        self.player = player

        for w in self.wingmen_list[:]:
            w.update(dt)
            if hasattr(w, "alive") and not w.alive():
                if w in self.wingmen_list:
                    self.wingmen_list.remove(w)
            w.draw(screen)

    def get_shots(self):
        return None

    def kill(self):
        """Clean up wingmen"""
        for w in self.wingmen_list:
            if hasattr(w, "kill"):
                w.kill()
        self.wingmen_list = []
