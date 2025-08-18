from circleshape import *
import constants
import random


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x,y,radius)


    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius)
    
    def update(self, dt):
        self.position += dt * self.velocity
        if (self.position.y < 2 * -constants.SCREEN_HEIGHT or 
        self.position.y > 2 * constants.SCREEN_HEIGHT or 
        self.position.x < -2 * constants.SCREEN_WIDTH or 
        self.position.x > 2 * constants.SCREEN_WIDTH):
            self.kill()


    def kill(self):
        if self.radius <= constants.ASTEROID_MIN_RADIUS:
            super().kill()
            return
        left = Asteroid(self.position.x, self.position.y, self.radius / 2)
        right = Asteroid(self.position.x, self.position.y, self.radius / 2)
        left.velocity = self.velocity.rotate(random.randint(-40, 0))
        right.velocity = self.velocity.rotate(random.randint(0, 40))
        super().kill()