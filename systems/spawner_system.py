import random
from entities.enemies import Grunt

class SpawnerSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_timer = 0.0
        self.spawn_rate = 2.0 # Spawn a grunt every 2 seconds

    def update(self, entities, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0.0
            self.spawn_grunt(entities)

    def spawn_grunt(self, entities):
        # Spawn outside the screen edges
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.uniform(0, self.screen_width)
            y = -50
        elif side == 'bottom':
            x = random.uniform(0, self.screen_width)
            y = self.screen_height + 50
        elif side == 'left':
            x = -50
            y = random.uniform(0, self.screen_height)
        else:
            x = self.screen_width + 50
            y = random.uniform(0, self.screen_height)
            
        entities.append(Grunt(x, y))
