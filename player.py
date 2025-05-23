from circleshape import *
from constants import PLAYER_RADIUS, PLAYER_TURN_SPEED

class player(CircleShape):
    def __init__(self, x, y):
        self.rotation = 0
        self.x = x
        self.y = y
        super().__init__(x, y, PLAYER_RADIUS)

    # in the player class
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw (self, screen):
        pygame.draw.polygon(screen, 255, self.triangle(), 2)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        #print(self.rotation)
        if keys[pygame.K_a]:
            self.rotation += dt * PLAYER_TURN_SPEED
        if keys[pygame.K_d]:
            self.rotation -= dt* PLAYER_TURN_SPEED