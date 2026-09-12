import math
import random
from entities.enemies import Grunt, Boomer, LaserDrone
from entities.particles import TeleportParticle

class SpawnerSystem:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.spawn_timer = 0.0
        self.boomer_spawn_timer = 0.0
        self.drone_spawn_timer = 0.0

    def _get_grunt_spawn_rate(self, threat_level):
        """Returns the Grunt spawn rate (seconds)."""
        if threat_level == 1: return 2.0
        if threat_level < 10: return 1.0 # Level 2-9
        return 0.5 # Level 10

    def _get_boomer_spawn_rate(self, threat_level):
        if threat_level == 3: return 8.0
        if threat_level < 10: return 5.0
        return 3.0

    def _get_drone_spawn_rate(self, threat_level):
        if threat_level < 10: return 15.0
        return 8.0

    def update(self, entities, dt, threat_level=1):
        # --- Grunt Spawning (always active) ---
        grunt_rate = self._get_grunt_spawn_rate(threat_level)
        self.spawn_timer += dt
        if self.spawn_timer >= grunt_rate:
            self.spawn_timer = 0.0
            self.spawn_grunt(entities, threat_level)

        # --- Boomer Spawning (Threat Level 3+) ---
        if threat_level >= 3:
            boomer_rate = self._get_boomer_spawn_rate(threat_level)
            self.boomer_spawn_timer += dt
            if self.boomer_spawn_timer >= boomer_rate:
                self.boomer_spawn_timer = 0.0
                self.spawn_boomer(entities)

        # --- LaserDrone Spawning (Threat Level 5+) ---
        if threat_level >= 5:
            drone_rate = self._get_drone_spawn_rate(threat_level)
            self.drone_spawn_timer += dt
            if self.drone_spawn_timer >= drone_rate:
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

    def spawn_grunt(self, entities, threat_level):
        x, y = self._random_edge_position()
        
        # Level 8+: Cluster spawning
        spawn_count = random.randint(3, 5) if threat_level >= 8 else 1
        
        for _ in range(spawn_count):
            # Apply offset for cluster spawns so they don't exactly overlap
            ox = x + random.uniform(-20, 20) if spawn_count > 1 else x
            oy = y + random.uniform(-20, 20) if spawn_count > 1 else y
            
            grunt = Grunt(ox, oy)
            
            # Level 7+: Increased max_speed (data mutation, avoiding inheritance)
            if threat_level >= 7:
                grunt.physics.max_speed = 220.0
                
            entities.append(grunt)

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
        
        # Teleportation particle burst
        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100.0, 300.0)
            entities.append(TeleportParticle(x, y, speed, angle))
