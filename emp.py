import constants
from circleshape import *
from shot import Shot
from weapon import Weapon

class Emp(Weapon):

    def __init__(self, player):
        super().__init__(player)
        self.player = player
        self.piercing = 3
        self.disabled_until = 0
        self.level = 0
        self.active = True
        
        self.max_radius = constants.EMP_RADIUS
        self.radius = 0
        self.shots = []
        self.shot = None
        self.forward = 0

    def get_shots(self):
        if self.shots and self.is_active():
            return self.shots
        return None
     
    def is_active(self):
        if self.active:
            return True
        if pygame.time.get_ticks() >= self.disabled_until:
            self.active = True
            if self.shot:
                self.shot.piercing = self.piercing
            return True
        return False
     
    def apply_upgrade(self, containers=None, upgrade_type=None):
        if self.level == 0:
            self.shot = Emp_Shot(self.player, self)
            self.shots.append(self.shot)
            # Add to sprite groups if containers are set
            if containers and hasattr(self.shot, 'add'):
                self.shot.add(containers)
            elif hasattr(Shot, 'containers') and Shot.containers:
                self.shot.add(Shot.containers)

        self.piercing = self.player.piercing
        self.level += 1
        self.max_radius *= 1.3
        self.piercing += 3
        if self.max_radius > 300:
            self.max_radius = 300

    def update(self, player, screen, dt):
        if self.shot is None:
            return
        
        if not self.active:
            if pygame.time.get_ticks() >= self.disabled_until:
                self.active = True
            else:
                return
        
        self.shot.position = player.position.copy()
        
        if self.radius < self.max_radius:
            self.radius = (self.radius + 400 * dt) 
            self.shot.radius = self.radius
            if self.radius >= self.max_radius:
                self.radius = 0
                self.active = False
                self.disabled_until = pygame.time.get_ticks() + (8000 * max(0.2, 1 - (self.level * 0.1)))
        
        # Draw the EMP blast effect
        pygame.draw.circle(screen, [20, 55, 55], self.shot.position, self.radius)
        # Draw the inner pulse
        inner_radius = self.radius * 0.7
        if inner_radius > 0:
            pygame.draw.circle(screen, [50, 150, 150], self.shot.position, inner_radius)

class Emp_Shot(Shot):
    def __init__(self, player, Emp):
        super().__init__(player.position.x, player.position.y, 1)  # Start with radius 1
        self.Emp = Emp
        self.piercing = 5
        self.disabled_until = 0
        self.level = Emp.level
        self.active = True
        self.position = player.position
        self.radius = 1

    def update(self, dt):
        # Radius is controlled by the EMP weapon
        self.radius = self.Emp.radius
        self.position = self.Emp.player.position.copy()

    def draw(self, screen):
        # Drawing is handled by the EMP weapon
        pass

    def kill(self):
        # Cannot be manually killed - controlled by EMP cooldown
        pass

    def is_active(self):
        return self.Emp.is_active()