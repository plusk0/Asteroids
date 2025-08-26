import constants
from circleshape import *
from shot import Shot
from weapon import Weapon

class Emp(Weapon):

    def __init__(self, player):
        super().__init__(player)
        self.piercing = 3
        self.disabled_until = 0
        self.level = 1
        self.active = True
        self.player = player

        self.max_radius = constants.EMP_RADIUS
        self.radius = 0
        self.shot = Emp_Shot(self.player, self)
        self.shots = []
        self.shots.append(self.shot)

        self.apply_upgrade()

    def get_shots(self):
        if self.shots != None and self.is_active() == True:
            return self.shots
        else:
            return None
        
    def kill(self):
        self.active = False
        self.shot.piercing = self.piercing
        self.disabled_until = pygame.time.get_ticks() + (8000 * max(0.2, 1 - (self.level * 0.1)))

    def is_active(self):
        if self.active:
            return True
        if pygame.time.get_ticks() >= self.disabled_until:
            self.active = True
            self.shot.piercing = self.piercing
            return True
        return False
    
    def draw(self, screen):
        pass

    def apply_upgrade(self):
        self.piercing = self.player.piercing
        self.level += 1
        self.max_radius *= 1.3
        self.piercing += 3
        if self.max_radius > 300:
            self.max_radius = 300

    def update(self, player, screen, dt):
        if self.shot == None:
            return
        if self.active == False:
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
                self.kill()
        pygame.draw.circle(screen, [20,55,55], self.shot.position, self.radius)

class Emp_Shot(Shot):
    def __init__(self, player, Emp):
        super().__init__(player.position.x, player.position.y, Emp.radius)
        self.Emp = Emp
        self.piercing = 5
        self.disabled_until = 0
        self.level = Emp.level
        self.active = True
        self.position = player.position
        self.radius = 1

    def update(self, dt):
        self.radius = self.Emp.radius

    def draw(self, screen):
        pass

    def kill(self):
        pass
