from circleshape import *
import constants
from weaponmanager import WeaponManager
from shot import Shot



class Player(CircleShape):
    def __init__(self, x, y):
        self.rotation = 0
        self.x = x
        self.y = y

        self.sprites = []
        self.sprites.append(pygame.image.load("sprites/sprite_0.png").convert_alpha())
        self.sprites.append(pygame.image.load("sprites/sprite_1.png").convert_alpha())
        self.sprites.append(pygame.image.load("sprites/sprite_2.png").convert_alpha())
        self.currentsprite = 0
        
        super().__init__(x, y, constants.PLAYER_RADIUS)
        
        self.exp = 0
        self.score = 0
        self.level = 1
        self.shield = constants.PLAYER_SHIELD
        self.shielded = False
        self.max_health = constants.PLAYER_HEALTH
        self.health = self.max_health

        self.shot_no = constants.PLAYER_SHOT_NO
        self.piercing = constants.PLAYER_SHOT_PIERCE
        self.shot_radius = constants.SHOT_RADIUS
        self.shot_cooldown = constants.PLAYER_SHOOT_COOLDOWN
        self.shot_speed = constants.SHOT_SPEED
        self.current_cooldown = self.shot_cooldown

        self.icon_shape = self._compute_icon_shape()

        self.weapon_manager = WeaponManager(self)

    def _compute_icon_shape(self):
        small_radius = 15 * constants.SCALE
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

    def gain_exp(self):
        self.exp += 5
        if self.exp >= 10 * (self.level ** 2):
            self.level_up()
    
    def gain_score(self):
        self.score += 100
        
    def level_up(self):
        self.exp = 0
        self.level += 1

    def apply_upgrade(self, upgrade):
        match upgrade:
            case "Multi Shot":
                self.shot_no += 1
            case "Shield":
                self.shield += 1
            case "Extra Life":
                self.max_health += 1
                self.health = self.max_health
            case "Piercing Bullets":
                self.piercing += 1
            case "Bigger Bullets":
                self.shot_radius = max((20 * constants.SCALE), self.shot_radius + (0.5 * constants.SCALE))
            case "Rapid Fire":
                self.shot_cooldown = max(0.01, self.shot_cooldown - (0.4 * self.shot_cooldown))
            case _ if upgrade in constants.WEAPONS:
                self.weapon_manager.apply_upgrade_by_name(upgrade)
        return

    def draw (self, screen):
        if self.shielded == True:
            pygame.draw.circle(screen, [180, 20, 20], self.position, self.radius * 2)

        if self.shield > 0:
            pygame.draw.circle(screen, [20, 180, 180], self.position, self.radius * 2)

        self.currentsprite += 1
        if self.currentsprite >= len(self.sprites):
            self.currentsprite = 0
        image = pygame.transform.rotate(self.sprites[self.currentsprite], -self.rotation + 180)
        
        screen.blit(image, self.position - pygame.Vector2(image.get_width() / 2, image.get_height() / 2))
        #pygame.draw.polygon(screen, [255,255,255], self.triangle(), 2) # debugging triangle

    def update(self, dt):
        keys = pygame.key.get_pressed()
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
        if self.shot_no == 1:
            bullet = Shot(self.position[0],self.position[1],self.shot_radius)
            bullet.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * self.shot_speed
            bullet.piercing = self.piercing
            self.current_cooldown = self.shot_cooldown
        else:
            for i in range(self.shot_no):
                angle_offset = (i - (self.shot_no - 1) / 2) * 10
                bullet = Shot(self.position[0], self.position[1], self.shot_radius)
                bullet.velocity = pygame.Vector2(0, 1).rotate(self.rotation + angle_offset) * self.shot_speed
                bullet.piercing = self.piercing
                self.current_cooldown = self.shot_cooldown + 1 * (self.shot_no / 10)

    def rotate(self, dt):
        self.rotation += dt * constants.PLAYER_TURN_SPEED

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        if (self.position.x + forward[0] * constants.PLAYER_SPEED * dt < constants.SCREEN_WIDTH 
            and self.position.x + (forward[0] * constants.PLAYER_SPEED * dt) > 0 
            and self.position.y + (forward[1] * constants.PLAYER_SPEED * dt) < constants.SCREEN_HEIGHT - self.radius / 2 * constants.SCALE 
            and self.position.y + (forward[1] * constants.PLAYER_SPEED * dt) > 0):
            self.position += forward * constants.PLAYER_SPEED * dt