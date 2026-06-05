import pygame
import constants
import math
import random
from weapon import Weapon


class Magnetizer(Weapon):
    """Supporting weapon that pushes asteroids away from the player"""
    
    def __init__(self, player):
        super().__init__(player)
        self.player = player
        
        # Upgradeable properties - start at level 0 (no effect)
        self.level = 0
        self.push_amount = 0  # Start with no effect at level 0
        self.push_range = 0  # No range at level 0
        self.max_asteroid_size = constants.MAGNETIZER_MAX_ASTEROID_SIZE
        
        # Visual properties - greyish color
        self.color = (150, 150, 150)  # Greyish color
        self.active = self.level > 0
        
        # Effect properties for rolling animation (EMP-like expanding circles)
        self.effect_circles = []  # List of active effect circles
        self.effect_timer = 0
        self.effect_spawn_interval = 0.3  # seconds between circles
        self.next_circle_time = 0

    def apply_upgrade(self, containers=None, upgrade_type=None):
        """Upgrade the magnetizer weapon"""
        self.level += 1
        
        # Only start working at level 1
        if self.level >= 1:
            self.active = True
        
        # Apply upgrades based on level
        # Push amount is adjusted so that level 5 can barely keep medium asteroids away
        # At level 5, push_amount * resistance should counteract asteroid speed
        # Asteroid speed ranges from 40-100 (base) * difficulty multiplier
        # For medium difficulty: 40-100 * 1.5 = 60-150
        # For tier 2 (medium) asteroids: resistance = 0.5
        # So at level 5: push_amount * 0.5 >= asteroid_speed (to keep them away)
        # If we want to keep medium asteroids away at medium difficulty: push_amount * 0.5 >= 100
        # So push_amount >= 200 at level 5
        if self.level == 1:
            # Level 1: base values
            self.push_amount = 20  # Increased from 15
            self.push_range = constants.MAGNETIZER_PUSH_RANGE
        elif self.level == 2:
            self.push_amount = 40
            self.push_range = constants.MAGNETIZER_PUSH_RANGE
        elif self.level == 3:
            self.push_amount = 80
            self.push_range = constants.MAGNETIZER_PUSH_RANGE * 1.1
        elif self.level == 4:
            self.push_amount = 140
            self.push_range = constants.MAGNETIZER_PUSH_RANGE * 1.2
        elif self.level >= 5:
            # At level 5, push_amount = 200, which with resistance 0.5 gives 100 force
            # This should barely keep medium asteroids (speed 100-150 at medium difficulty) away
            self.push_amount = 200 + (self.level - 5) * 40
            # Increase range as well
            self.push_range = constants.MAGNETIZER_PUSH_RANGE * (1.2 + (self.level - 5) * 0.1)

    def update(self, player, screen, dt):
        """Update magnetizer effect on nearby asteroids"""
        self.player = player
        
        # Only process if active (level > 0)
        if not self.active:
            return
        
        # Get all asteroids
        asteroids = self.get_asteroids()
        
        # Apply magnetic force to each asteroid
        for asteroid in asteroids:
            self.apply_magnetic_force(asteroid, dt)
        
        # Update effect timer for rolling animation
        self.effect_timer += dt
        # Spawn a new circle every interval, but only if we have active circles or it's time for the first one
        if len(self.effect_circles) == 0 or self.effect_timer >= self.effect_spawn_interval:
            if self.effect_timer >= self.effect_spawn_interval:
                self.effect_timer = 0
            # Add a new effect circle
            self.effect_circles.append({
                'radius': 0,
                'max_radius': self.push_range,
                'alpha': 200,
                'age': 0,
                'lifetime': 0.8  # 0.8 seconds
            })
        
        # Update existing effect circles
        for circle in self.effect_circles[:]:
            circle['age'] += dt
            # Fade out over lifetime
            circle['alpha'] = max(0, 200 * (1 - circle['age'] / circle['lifetime']))
            # Expand to full radius over lifetime
            circle['radius'] = circle['max_radius'] * (circle['age'] / circle['lifetime'])
            
            if circle['age'] >= circle['lifetime']:
                self.effect_circles.remove(circle)
        
        # Draw the magnetizer effect
        self.draw_effect(screen)

    def get_asteroids(self):
        """Get asteroids from the game"""
        # Try to get asteroids from the weapon instance
        if hasattr(self, 'asteroids') and self.asteroids:
            return list(self.asteroids)
        # Fallback: try to get asteroids from player's game
        elif hasattr(self.player, 'game') and hasattr(self.player.game, 'asteroids'):
            return list(self.player.game.asteroids)
        return []

    def apply_magnetic_force(self, asteroid, dt):
        """Apply magnetic repulsion force to an asteroid"""
        # Check if asteroid is within range
        distance = self.player.position.distance_to(asteroid.position)
        
        if distance > self.push_range:
            return
        
        # Check if asteroid is too large
        if hasattr(asteroid, 'radius') and asteroid.radius > self.max_asteroid_size:
            return
        
        # Get resistance multiplier based on asteroid tier
        tier = getattr(asteroid, 'tier', 1)
        resistance = constants.ASTEROID_TIER_MAGNETIZER_RESISTANCE.get(tier, 1.0)
        
        # Calculate push direction (away from player)
        direction = (asteroid.position - self.player.position).normalize()
        
        # Calculate push force based on distance (stronger when closer)
        distance_factor = 1 - (distance / self.push_range)
        push_force = self.push_amount * distance_factor * resistance
        
        # Apply force
        asteroid.position += direction * push_force * dt
        
        # Also affect velocity to prevent asteroids from coming back
        if hasattr(asteroid, 'velocity'):
            asteroid.velocity += direction * push_force * 0.1

    def draw_effect(self, screen):
        """Draw visual effect to show magnetizer rolling animation"""
        if not self.active:
            return
        
        # Draw rolling circles (EMP-like effect with grey color)
        for circle in self.effect_circles:
            alpha = circle['alpha']
            radius = circle['radius']
            
            # Create a surface for the circle
            circle_surface = pygame.Surface(
                (int(radius * 2) + 10, int(radius * 2) + 10), 
                pygame.SRCALPHA
            )
            
            # Draw the circle with alpha - use greyish color
            # Use multiple shades for a nicer effect
            color = (180, 180, 180, alpha)
            pygame.draw.circle(
                circle_surface, 
                color, 
                (int(radius) + 5, int(radius) + 5), 
                int(radius),
                2
            )
            
            # Draw inner circle for depth
            inner_alpha = int(alpha * 0.7)
            inner_color = (200, 200, 200, inner_alpha)
            inner_radius = int(radius * 0.8)
            if inner_radius > 0:
                pygame.draw.circle(
                    circle_surface,
                    inner_color,
                    (int(radius) + 5, int(radius) + 5),
                    inner_radius,
                    1
                )
            
            # Blit the circle surface onto the screen
            screen.blit(
                circle_surface, 
                (int(self.player.position.x - radius), 
                 int(self.player.position.y - radius))
            )

    def get_shots(self):
        """Magnetizer doesn't have traditional shots"""
        return None
    
    def is_active(self):
        """Check if magnetizer is active"""
        return self.active and self.level > 0
    
    def set_active(self, active):
        """Set magnetizer active state"""
        self.active = active and self.level > 0