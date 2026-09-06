import random
from entities.enemies import Grunt, Boomer, LaserDrone

class SpawnerSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Grunt: one every 2 seconds, spawns off-screen edges
        self.spawn_timer = 0.0
        self.spawn_rate = 2.0

        # Boomer: one every 8 seconds, spawns off-screen edges
        self.boomer_spawn_timer = 0.0
        self.boomer_spawn_rate = 8.0

        # LaserDrone: one every 15 seconds, spawns in arena interior
        self.drone_spawn_timer = 0.0
        self.drone_spawn_rate = 15.0

    def update(self, entities, dt):
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0.0
            self.spawn_grunt(entities)

        self.boomer_spawn_timer += dt
        if self.boomer_spawn_timer >= self.boomer_spawn_rate:
            self.boomer_spawn_timer = 0.0
            self.spawn_boomer(entities)

        self.drone_spawn_timer += dt
        if self.drone_spawn_timer >= self.drone_spawn_rate:
            self.drone_spawn_timer = 0.0
            self.spawn_laser_drone(entities)

    def _random_edge_position(self):
        """Returns a random (x, y) just outside one of the four screen edges."""
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.uniform(0, self.screen_width), -50
        elif side == 'bottom':
            return random.uniform(0, self.screen_width), self.screen_height + 50
        elif side == 'left':
            return -50, random.uniform(0, self.screen_height)
        else:
            return self.screen_width + 50, random.uniform(0, self.screen_height)

    def spawn_grunt(self, entities):
        x, y = self._random_edge_position()
        entities.append(Grunt(x, y))

    def spawn_boomer(self, entities):
        x, y = self._random_edge_position()
        # Each Boomer gets a unique blast radius to keep encounters unpredictable
        blast_radius = random.uniform(80.0, 150.0)
        entities.append(Boomer(x, y, blast_radius=blast_radius))

    def spawn_laser_drone(self, entities):
        # Interior spawn with 100px margin so the drone body and beam are fully visible
        margin = 100
        x = random.uniform(margin, self.screen_width - margin)
        y = random.uniform(margin, self.screen_height - margin)
        entities.append(LaserDrone(x, y))
