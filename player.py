from circleshape import *
from constants import *
from shot import Shot

class Player(CircleShape):
    def __init__(self, x, y):
        self.rotation = 0
        self.x = x
        self.y = y
        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN
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
        if self.shot_cooldown != 0:
            self.shot_cooldown -= dt
        if self.shot_cooldown < 0:
            self.shot_cooldown = 0
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE] and self.shot_cooldown == 0:
            self.shoot()

    def shoot(self):
        bullet = Shot(self.position[0],self.position[1],SHOT_RADIUS)
        bullet.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * SHOT_SPEED
        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN

    def rotate(self, dt):
        self.rotation += dt * PLAYER_TURN_SPEED

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt