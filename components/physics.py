from pygame.math import Vector2

class Physics:
    def __init__(self, max_speed: float, mass: float = 1.0):
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.max_speed = max_speed
        self.mass = mass
