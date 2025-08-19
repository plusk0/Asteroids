from circleshape import *
import constants


class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x,y,radius)
        self.piercing = 0

    def draw(self, screen):
        pygame.draw.circle(screen, [210,255,255], self.position, self.radius)
    
    def update(self, dt):
        self.position += dt * self.velocity
        if (self.position.y < -constants.SCREEN_HEIGHT or 
        self.position.y > constants.SCREEN_HEIGHT or 
        self.position.x < -constants.SCREEN_WIDTH or 
        self.position.x > constants.SCREEN_WIDTH):
            self.kill()


