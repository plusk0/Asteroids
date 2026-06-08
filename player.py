from circleshape import *
import constants
from weaponmanager import WeaponManager
from shot import Shot


class Player(CircleShape):
    def __init__(self, x, y):
        self.rotation = 0
        self.x = x
        self.y = y

        # self.player = player

        self.sprites = []
        try:
            self.sprites.append(
                pygame.image.load("sprites/sprite_0.png").convert_alpha()
            )
            self.sprites.append(
                pygame.image.load("sprites/sprite_1.png").convert_alpha()
            )
            self.sprites.append(
                pygame.image.load("sprites/sprite_2.png").convert_alpha()
            )
        except:
            # If sprites can't be loaded, create placeholder surfaces
            print("Warning: Could not load player sprites, using placeholder")
            placeholder = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(placeholder, (255, 255, 255), (20, 20), 20)
            self.sprites = [placeholder, placeholder, placeholder]
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
        self.laser = False

        self.screen = None  # for testing only

        self.icon_shape = self._compute_icon_shape()
        
        # Upgrade tracking for locking system
        self.owned_upgrades = set()  # Track which upgrades the player has
        self.locked_upgrades = set()  # Track which upgrades are currently locked
        
        # Shield regeneration properties
        self.shield_regen_unlocked = False  # Whether permanent shield regen is unlocked
        self.shield_regen_level = 0  # Level of shield regen cooldown upgrade (0-3)
        self.shield_regen_cooldown = constants.SHIELD_REGEN_COOLDOWN  # Current regen cooldown
        self.shield_last_used = 0  # Time when shield was last used
        self.shield_is_regenning = False  # Whether shield is currently on cooldown
        
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
        if self.exp >= 5 * (self.level**1.5):
            self.level_up()

    def gain_score(self):
        self.score += 100

    def level_up(self):
        self.exp = 0
        self.level += 1

    def apply_upgrade(self, upgrade):
        """Apply an upgrade to the player and handle locking/unlocking rules"""
        # Track that this upgrade is now owned
        self.owned_upgrades.add(upgrade)
        
        # Apply the upgrade effect
        is_final_upgrade = upgrade in constants.FINAL_UPGRADES.values()
        
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
                self.shot_radius = max(
                    (20 * constants.SCALE), self.shot_radius + (0.5 * constants.SCALE)
                )
            case "Rapid Fire":
                self.shot_cooldown = max(
                    0.01, self.shot_cooldown - (0.4 * self.shot_cooldown)
                )
            case "Wingman Formations":
                # One-time upgrade that unlocks formations
                if hasattr(self, 'weapon_manager') and hasattr(self.weapon_manager, 'wingmen'):
                    self.weapon_manager.wingmen.unlock_formations()
            case "Basic Fighter Maneuvers":
                # One-time upgrade that unlocks role distribution
                if hasattr(self, 'weapon_manager') and hasattr(self.weapon_manager, 'wingmen'):
                    self.weapon_manager.wingmen.unlock_maneuvers()
            case "Wingman Speed":
                # Upgrade wingmen speed
                if hasattr(self, 'weapon_manager') and hasattr(self.weapon_manager, 'wingmen'):
                    self.weapon_manager.wingmen.apply_speed_upgrade()
            case "Wingman Fire Rate":
                # Upgrade wingmen fire rate
                if hasattr(self, 'weapon_manager') and hasattr(self.weapon_manager, 'wingmen'):
                    self.weapon_manager.wingmen.apply_fire_rate_upgrade()
            case "Wingman Intelligence":
                # Unlock wingmen intelligence (intercept mode)
                if hasattr(self, 'weapon_manager') and hasattr(self.weapon_manager, 'wingmen'):
                    self.weapon_manager.wingmen.apply_intelligence_upgrade()
            case "Shield Regeneration":
                # Unlock permanent shield regeneration
                # Check if player has at least 3 shields
                if self.shield >= constants.SHIELD_PERMANENT_UNLOCK_LEVEL:
                    self.shield_regen_unlocked = True
                    # Reset shield count to 1 and unlock regeneration
                    self.shield = 1
            case "Shield Regen Cooldown":
                # Reduce shield regen cooldown by 1 second (max 3 levels)
                if self.shield_regen_level < 3:
                    self.shield_regen_level += 1
                    self.shield_regen_cooldown = max(
                        constants.SHIELD_REGEN_MIN_COOLDOWN,
                        constants.SHIELD_REGEN_COOLDOWN - (self.shield_regen_level * constants.SHIELD_REGEN_UPGRADE_DECREMENT)
                    )
            case _ if upgrade in constants.WEAPONS or upgrade in constants.FINAL_UPGRADES.values():
                self.weapon_manager.apply_upgrade_by_name(upgrade)
        
        # Apply locking rules after upgrade is applied
        self._apply_upgrade_locks(upgrade)
        
        return
    
    def _apply_upgrade_locks(self, upgrade):
        """Apply locking and unlocking rules for the given upgrade"""
        # Get rules for this upgrade
        rules = constants.UPGRADE_RULES.get(upgrade, {})
        
        # Lock upgrades specified in rules
        for locked_upgrade in rules.get("locks", []):
            self.locked_upgrades.add(locked_upgrade)
        
        # Handle final upgrades
        if upgrade in constants.FINAL_UPGRADES.values():
            # This is a final upgrade (e.g., Shockwave)
            # Lock the base weapon
            for base_weapon, final_upgrade in constants.FINAL_UPGRADES.items():
                if upgrade == final_upgrade:
                    self.locked_upgrades.add(base_weapon)
                    break
        
        # Unlock upgrades specified in rules
        for unlocked_upgrade in rules.get("unlocks", []):
            if unlocked_upgrade in self.locked_upgrades:
                self.locked_upgrades.remove(unlocked_upgrade)

    def draw(self, screen):
        # Draw shield effects
        if self.shielded:
            pygame.draw.circle(screen, [180, 20, 20], self.position, self.radius * 2, 2)

        if self.shield > 0:
            pygame.draw.circle(
                screen, [20, 180, 180], self.position, self.radius * 2, 2
            )

        # Draw player sprite with animation
        if self.sprites and len(self.sprites) > 0:
            self.currentsprite += 0.2
            if self.currentsprite >= len(self.sprites):
                self.currentsprite = 0
            sprite_index = int(self.currentsprite)
            image = pygame.transform.rotate(
                self.sprites[sprite_index], -self.rotation + 180
            )

            screen.blit(
                image,
                self.position
                - pygame.Vector2(image.get_width() / 2, image.get_height() / 2),
            )
        else:
            # Fallback drawing if no sprites
            pygame.draw.circle(screen, [255, 255, 255], self.position, self.radius)
            # Draw triangle shape
            pygame.draw.polygon(screen, [255, 255, 255], self.triangle(), 2)

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
        
        # Handle shield regeneration
        if self.shield_regen_unlocked and self.shield > 0:
            current_time = pygame.time.get_ticks()
            # Check if shield was used and needs to regenerate
            if self.shield_is_regenning:
                if (current_time - self.shield_last_used) / 1000.0 >= self.shield_regen_cooldown:
                    # Regen cooldown passed, shield is back
                    self.shield_is_regenning = False

    def shoot(self):
        self.weapon_manager.shoot()

    def rotate(self, dt):
        self.rotation += dt * constants.PLAYER_TURN_SPEED

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        if (
            self.position.x + forward[0] * constants.PLAYER_SPEED * dt
            < constants.GAMEPLAY_WIDTH
            and self.position.x + (forward[0] * constants.PLAYER_SPEED * dt) > 0
            and self.position.y + (forward[1] * constants.PLAYER_SPEED * dt)
            < constants.GAMEPLAY_HEIGHT - self.radius / 2 * constants.SCALE
            and self.position.y + (forward[1] * constants.PLAYER_SPEED * dt) > 0
        ):
            self.position += forward * constants.PLAYER_SPEED * dt

