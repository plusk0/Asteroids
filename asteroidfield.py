import pygame
import random
from asteroid import Asteroid
import constants


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-constants.ASTEROID_MAX_RADIUS, y * constants.SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                constants.SCREEN_WIDTH + constants.ASTEROID_MAX_RADIUS, y * constants.SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * constants.SCREEN_WIDTH, -constants.ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT + constants.ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.modifier = 1
        self.difficulty = 0  # 0=Easy, 1=Medium, 2=Nightmare

    def set_difficulty(self, difficulty):
        """Set the difficulty level"""
        self.difficulty = difficulty
    
    def set_player_level(self, level):
        """Set the player level for tier calculation"""
        self._player_level = level

    def increase_difficulty(self, level, difficulty):
        """Increase difficulty based on player level and selected difficulty"""
        self.difficulty = difficulty
        # Base modifier increases with level
        level_modifier = 1 + (level / 20)
        # Apply difficulty multiplier
        difficulty_multiplier = constants.DIFFICULTY_SPAWN_MULTIPLIERS.get(difficulty, 1.0)
        self.modifier = level_modifier * difficulty_multiplier

    def spawn(self, radius, position, velocity, tier=1):
        """Spawn an asteroid with specified tier"""
        asteroid = Asteroid(position.x, position.y, radius, tier)
        asteroid.velocity = velocity * self.modifier

    def get_asteroid_tier(self, player_level=1):
        """Determine tier based on difficulty, player level and random chance"""
        # Higher difficulties have higher chance of spawning higher tier asteroids
        # Medium: No high level asteroids, but medium ones can spawn sometimes
        # Nightmare: Low chance of high level asteroids starting at player level 1
        tier_probabilities = {
            0: [0.85, 0.15, 0.0],     # Easy: 85% tier 1, 15% tier 2, 0% tier 3
            1: [0.7, 0.3, 0.0],        # Medium: 70% tier 1, 30% tier 2, 0% tier 3
            2: [0.55, 0.35, 0.1]      # Nightmare: 55% tier 1, 35% tier 2, 10% tier 3
        }
        
        # Adjust probabilities based on player level for nightmare difficulty
        if self.difficulty == 2 and player_level >= 1:
            # At nightmare, high level asteroids can spawn starting at level 1
            base_prob = tier_probabilities[2]
            # Increase chance of tier 3 as player level increases
            tier3_boost = min(0.3, (player_level - 1) * 0.05)  # Max 30% additional chance
            base_prob[2] += tier3_boost
            base_prob[0] = max(0.1, base_prob[0] - tier3_boost)  # Don't go below 10%
            probabilities = base_prob
        else:
            probabilities = tier_probabilities.get(self.difficulty, [0.85, 0.15, 0.0])
        
        rand_val = random.random()
        
        if rand_val < probabilities[0]:
            return 1
        elif rand_val < probabilities[0] + probabilities[1]:
            return 2
        else:
            return 3

    def update(self, dt):
        self.spawn_timer += dt
        
        # Get player level from the stored reference
        player_level = getattr(self, '_player_level', 1)
        
        # Calculate spawn rate based on difficulty
        spawn_rate = constants.ASTEROID_SPAWN_RATE / self.modifier
        
        if self.spawn_timer > spawn_rate:
            self.spawn_timer = 0
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            
            # Apply difficulty-based speed multiplier
            speed_multiplier = constants.DIFFICULTY_SPEED_MULTIPLIERS.get(self.difficulty, 1.0)
            velocity *= speed_multiplier
            
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, constants.ASTEROID_KINDS)
            
            # Determine asteroid tier based on difficulty and player level
            tier = self.get_asteroid_tier(player_level)
            
            # Apply difficulty-based size multiplier
            size_multiplier = constants.DIFFICULTY_SIZE_MULTIPLIERS.get(self.difficulty, 1.0)
            radius = constants.ASTEROID_MIN_RADIUS * kind * size_multiplier
            
            self.spawn(radius, position, velocity, tier)