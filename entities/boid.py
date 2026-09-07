from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
import random

class Boid:
    def __init__(self, x: float, y: float, max_speed: float = 350.0):
        self.transform = Transform(x, y)
        self.physics = Physics(max_speed=max_speed, mass=1.0)
        
        # Moderate initial velocity
        self.physics.velocity.x = random.uniform(-20, 20)
        self.physics.velocity.y = random.uniform(-20, 20)
            
        self.graphics = Graphics(color=(220, 220, 220), scale=3.0, sprite_ref="skeleton")
        self.collider = Collider(radius=3.0)
