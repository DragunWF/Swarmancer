from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider

class Grunt:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # Slower max_speed than Boid (350.0) so they can be kited.
        self.physics = Physics(max_speed=150.0, mass=1.5)
        # Red-ish color, slightly larger scale than boid
        self.graphics = Graphics(color=(220, 50, 50), scale=4.0)
        self.collider = Collider(radius=4.0)
        
        self.is_enemy = True
        self.enemy_type = 'grunt'
