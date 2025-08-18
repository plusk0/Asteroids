from circleshape import *
from constants import *


class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x,y,radius)
        self.piercing = 0

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)
    
    def update(self, dt):
        self.position += dt * self.velocity
        if self.position.y < -SCREEN_HEIGHT or self.position.y > SCREEN_HEIGHT or self.position.x < -SCREEN_WIDTH or self.position.x > SCREEN_WIDTH:
            self.kill()


