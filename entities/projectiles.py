from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
from components.timers import LifespanTimer

class Projectile:
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float):
        self.transform = Transform(x, y)
        self.physics = Physics(max_speed=500.0, mass=0.1)
        self.physics.velocity.x = velocity_x
        self.physics.velocity.y = velocity_y
        self.graphics = Graphics(color=(255, 255, 100), scale=2.0)
        self.collider = Collider(radius=2.0, is_trigger=True)
        self.lifespan_timer = LifespanTimer(duration=2.0)
