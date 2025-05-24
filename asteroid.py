from circleshape import *
from constants import *
import random

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x,y,radius)


    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)
    
    def update(self, dt):
        self.position += dt * self.velocity

    def hit(self):
        if self.radius > ASTEROID_MIN_RADIUS:
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            split1 = Asteroid(self.position[0], self.position[1], new_radius)
            split1.velocity = self.velocity.rotate(random.uniform(-50, -10)) * 1.2
            split2 = Asteroid(self.position[0], self.position[1], new_radius)
            split2.velocity = self.velocity.rotate(random.uniform(50, 10)) * 1.2
            self.kill()
        else:
            self.kill()

#add kill method