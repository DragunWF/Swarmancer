import random
from entities.enemies import Grunt, Boomer, LaserDrone

# Grunt spawn rates (seconds between spawns) keyed by Threat Level tier
_GRUNT_SPAWN_RATES = {
    (1, 2): 2.0,
    (3, 4): 2.0,
    (5, 7): 1.5,
    (8, 10): 0.8,
}

class SpawnerSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Grunt: rate is adjusted dynamically per threat level
        self.spawn_timer = 0.0
        self.spawn_rate = 2.0

        # Boomer: one every 8 seconds, spawns off-screen edges
        self.boomer_spawn_timer = 0.0
        self.boomer_spawn_rate = 8.0

        # LaserDrone: one every 15 seconds, spawns in arena interior
        self.drone_spawn_timer = 0.0
        self.drone_spawn_rate = 15.0

    def _get_grunt_spawn_rate(self, threat_level):
        """Returns the correct Grunt spawn rate (seconds) for the given Threat Level."""
        for (low, high), rate in _GRUNT_SPAWN_RATES.items():
            if low <= threat_level <= high:
                return rate
        return 2.0

    def update(self, entities, dt, threat_level=1):
        # Dynamically update the grunt spawn rate based on current threat level
        self.spawn_rate = self._get_grunt_spawn_rate(threat_level)

        # --- Grunt Spawning (always active) ---
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0.0
            self.spawn_grunt(entities)

        # --- Boomer Spawning (Threat Level 3+) ---
        if threat_level >= 3:
            self.boomer_spawn_timer += dt
            if self.boomer_spawn_timer >= self.boomer_spawn_rate:
                self.boomer_spawn_timer = 0.0
                self.spawn_boomer(entities)

        # --- LaserDrone Spawning (Threat Level 5+) ---
        if threat_level >= 5:
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
