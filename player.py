from circleshape import *
from constants import *
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        self.rotation = 0
        self.x = x
        self.y = y
        
        super().__init__(x, y, PLAYER_RADIUS)
        self.exp = 0
        self.level = 1
        self.shield = PLAYER_SHIELD
        self.health = PLAYER_HEALTH

        self.shots = PLAYER_SHOT_NO
        self.piercing = PLAYER_SHOT_PIERCE
        self.shot_radius = SHOT_RADIUS
        self.shot_cooldown = PLAYER_SHOOT_COOLDOWN
        self.current_cooldown = self.shot_cooldown

        self.icon_shape = self._compute_icon_shape()

    def _compute_icon_shape(self):
        small_radius = 15
        forward = pygame.Vector2(0, 1)
        right = pygame.Vector2(0, 1).rotate(90) * small_radius / 1.5
        a = forward * small_radius
        b = -forward * small_radius - right
        c = -forward * small_radius + right
        return [a, b, c]
    
    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]


    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= 10 * (self.level ** 2):
            self.level_up()
    
    def level_up(self):
        self.exp = 0
        self.level += 1

    def apply_upgrade(self, upgrade):
        print(f"Upgrade applied: {upgrade} to player level {self.level}")
        match upgrade:
            case "Multi Shot":
                self.shots += 1
            case "Shield":
                self.shield += 1
            case "Extra Life":
                self.health += 1
            case "Piercing Bullets":
                self.piercing += 1
            case "Bigger Bullets":
                self.shot_radius = max(20, self.shot_radius + 5)
            case "Rapid Fire":
                self.shot_cooldown = max(0.01, self.shot_cooldown - (0.1 * self.shot_cooldown))
        return

    
    
    def draw (self, screen):
        pygame.draw.polygon(screen, [255,255,255], self.triangle(), 2)

        for i in range(self.health):
            corner_pos = pygame.Vector2(20 + (20*i), 20 + (20*i))
            points = [corner_pos + p for p in self.icon_shape]
            pygame.draw.polygon(screen, [255, 0, 0], points)

        for i in range(self.shield):
            corner_pos = pygame.Vector2(20 + (20*i), 50 + (20*i))
            points = [corner_pos + p for p in self.icon_shape]
            pygame.draw.polygon(screen, [0, 50, 255], points)


    def update(self, dt):
        keys = pygame.key.get_pressed()
        #print(self.rotation)
        if self.current_cooldown != 0:
            self.current_cooldown -= dt
        if self.current_cooldown < 0:
            self.current_cooldown = 0
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE] and self.current_cooldown == 0:
            self.shoot()

    def shoot(self):
        if self.shots == 1:
            bullet = Shot(self.position[0],self.position[1],self.shot_radius)
            bullet.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * SHOT_SPEED
            bullet.piercing = self.piercing
            self.current_cooldown = self.shot_cooldown
        else:
            for i in range(self.shots):
                angle_offset = (i - (self.shots - 1) / 2) * 10
                bullet = Shot(self.position[0], self.position[1], self.shot_radius)
                bullet.velocity = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset) * SHOT_SPEED
                bullet.piercing = self.piercing
                self.current_cooldown = self.shot_cooldown * (self.shots / 2)

    def rotate(self, dt):
        self.rotation += dt * PLAYER_TURN_SPEED

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        if (self.position.x + forward[0] * 5 < SCREEN_WIDTH 
            and self.position.x + (forward[1] * 5) > 0 
            and self.position.y + forward[0] * 5 < SCREEN_HEIGHT 
            and self.position.y + (forward[1] * 5) > 0):

            print(self.position)
            self.position += forward * PLAYER_SPEED * dt