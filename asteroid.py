from circleshape import *
import constants
import random


class Asteroid(CircleShape):
    def __init__(self, x, y, radius, tier=1):
        super().__init__(x, y, radius)
        self.tier = tier
        self.max_health = constants.ASTEROID_TIER_HEALTH_MULTIPLIERS.get(tier, 1)
        self.health = self.max_health
        self.color = constants.ASTEROID_TIER_COLORS.get(tier, (200, 200, 200))
    
    def draw(self, screen):
        # Draw asteroid with tier-specific color
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        # Add some visual detail based on tier
        if self.tier >= 2:
            # Draw inner circle for higher tiers
            inner_radius = self.radius * 0.6
            inner_color = (
                min(self.color[0] + 50, 255),
                min(self.color[1] + 50, 255), 
                min(self.color[2] + 50, 255)
            )
            pygame.draw.circle(screen, inner_color, self.position, inner_radius)
        
        if self.tier >= 3:
            # Draw outer ring for highest tier
            pygame.draw.circle(screen, self.color, self.position, self.radius, 2)
    
    def take_damage(self, damage=1):
        """Take damage and check if should be destroyed"""
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False
    
    def update(self, dt):
        self.position += dt * self.velocity
        if (self.position.y < 2 * -constants.GAMEPLAY_HEIGHT or 
        self.position.y > 2 * constants.GAMEPLAY_HEIGHT or 
        self.position.x < -2 * constants.GAMEPLAY_WIDTH or 
        self.position.x > 2 * constants.GAMEPLAY_WIDTH):
            self.kill()

    def kill(self):
        if self.radius <= constants.ASTEROID_MIN_RADIUS:
            super().kill()
            return
        left = Asteroid(self.position.x, self.position.y, self.radius / 2, self.tier)
        right = Asteroid(self.position.x, self.position.y, self.radius / 2, self.tier)
        left.velocity = self.velocity.rotate(random.randint(-40, 0))
        right.velocity = self.velocity.rotate(random.randint(0, 40))
        super().kill()