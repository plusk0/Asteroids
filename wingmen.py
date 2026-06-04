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

    def __init__(self, x, y, wingmen_weapon, wingman_id=0, role=constants.WINGMEN_FORMATION_CLOSE_FOLLOW):
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

        # Movement properties - speed is half of base shot speed
        self.speed = constants.WINGMEN_SPEED  # Already set to 100 (half of 200)
        self.base_follow_distance = 40 + (wingman_id * 20)
        self.follow_distance = self.base_follow_distance
        
        # Formation-specific properties
        self.scout_points = []  # For Scouting formation - random patrol points
        self.scout_point_index = 0
        self.scout_timer = 0
        
        # For proper rotation - track previous position
        self.prev_position = pygame.Vector2(x, y)
        self.facing_angle = 0

        # Target tracking
        self.target = None
        self.fire_cooldown = 0

        # Initial position
        self.position = pygame.Vector2(x, y)
        self.orbit_angle = random.uniform(0, 360)
        
        # Attack state
        self.behind_position = None  # Target position behind asteroid
        
        # Set formation behavior
        self.set_formation_behavior()
    
    def set_formation_behavior(self):
        """Set formation-specific behavior based on role"""
        if self.role == constants.WINGMEN_FORMATION_SCOUTING:
            # Generate random patrol points around player
            self.generate_scout_points()
            self.follow_distance = self.base_follow_distance * 1.5  # Wider range for scouting
        elif self.role == constants.WINGMEN_FORMATION_CLOSE_FOLLOW:
            # Close follow - tight formation
            self.follow_distance = self.base_follow_distance * 0.7
        elif self.role == constants.WINGMEN_FORMATION_RADAR_FOLLOW:
            # Radar follow - large circle around player (50% more than EMP range)
            self.follow_distance = constants.EMP_RADIUS * 1.5
    
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
        self.scout_timer = random.uniform(2, 5)  # Change target every 2-5 seconds

    def update(self, dt):
        if not hasattr(self, "player") or self.player is None:
            return

        # Update cooldown
        if self.fire_cooldown > 0:
            self.fire_cooldown -= dt

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
                self.facing_angle = -math.degrees(math.atan2(movement.y, movement.x))

    def find_target(self):
        """Find closest asteroid"""
        closest = None
        closest_dist = float("inf")

        asteroids = self.get_asteroids()
        for asteroid in asteroids:
            if hasattr(asteroid, "alive") and not asteroid.alive():
                continue
            dist = self.position.distance_to(asteroid.position)
            if dist < 300 and dist < closest_dist:
                closest_dist = dist
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
            self.orbit_angle += dt * 20  # Slower rotation for large circle
            self.orbit_angle %= 360
            offset = pygame.Vector2(0, -self.follow_distance).rotate(self.orbit_angle)
            self.position = self.player.position + offset
        else:
            # Close Follow (default): tight orbit
            self.orbit_angle += dt * 30
            self.orbit_angle %= 360
            offset = pygame.Vector2(0, -self.follow_distance).rotate(self.orbit_angle)
            self.position = self.player.position + offset
    
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
            self.scout_point_index = (self.scout_point_index + 1) % len(self.scout_points)

    def attack_behavior(self, dt):
        """Get behind asteroid, follow it, then shoot"""
        if not self.target or (
            hasattr(self.target, "alive") and not self.target.alive()
        ):
            self.target = None
            self.behind_position = None
            return

        asteroid = self.target
        asteroid_radius = getattr(asteroid, 'radius', 20)
        
        # Calculate position behind asteroid (opposite direction from asteroid velocity)
        if hasattr(asteroid, "velocity") and asteroid.velocity.length() > 0:
            # Get normalized velocity direction
            velocity_dir = asteroid.velocity.normalize()
            # Position behind asteroid (opposite to velocity direction)
            # Distance behind should be proportional to asteroid size
            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            self.behind_position = asteroid.position - velocity_dir * distance_behind
            
            # Move towards behind position
            direction = (self.behind_position - self.position).normalize()
            distance_to_behind = self.position.distance_to(self.behind_position)

            # Move towards behind position
            self.position += direction * self.speed * dt

            # If we're close enough to the behind position, shoot at the asteroid
            if distance_to_behind < 20 and self.fire_cooldown <= 0:
                # Shoot at the asteroid from behind
                shoot_dir = (asteroid.position - self.position).normalize()
                self.shoot_with_direction(shoot_dir)
                self.fire_cooldown = constants.WINGMEN_FIRE_COOLDOWN
        else:
            # Fallback if asteroid has no velocity
            direction = (asteroid.position - self.position).normalize()
            distance = self.position.distance_to(asteroid.position)

            # Position behind at offset proportional to sizes
            distance_behind = asteroid_radius * 1.5 + self.radius * 2
            self.behind_position = asteroid.position - direction * distance_behind
            self.position += (self.behind_position - self.position).normalize() * self.speed * dt

            if distance < 100 and self.fire_cooldown <= 0:
                self.shoot()
                self.fire_cooldown = constants.WINGMEN_FIRE_COOLDOWN

        # Go back to follow if too far from player
        if self.position.distance_to(self.player.position) > 200:
            self.target = None
            self.behind_position = None

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

        # Add to sprite groups - THIS IS THE KEY
        if hasattr(Shot, "containers") and Shot.containers:
            shot.add(Shot.containers)

    def draw(self, screen):
        # Use circular placeholders for debugging (easier to see and debug)
        # Draw main circle
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        # Draw outline
        pygame.draw.circle(screen, (255, 255, 255), self.position, self.radius, 1)
        
        # Draw direction indicator (line pointing in facing direction)
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

    def apply_upgrade(self, containers=None):
        """Upgrade wingmen weapon"""
        self.level += 1

        # Level 1: 1 wingman
        if self.level == 1:
            self.wingmen_count = 1
        # Every 5 levels: add another wingman (up to max)
        elif self.level % 5 == 0:
            self.wingmen_count = min(6, self.wingmen_count + 1)

        self.spawn_wingmen()

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

