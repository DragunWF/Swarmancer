from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
from components.timers import LifespanTimer
from settings import GLOBAL_SPRITE_SCALE

class Projectile:
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float):
        self.transform = Transform(x, y)
        self.physics = Physics(max_speed=500.0, mass=0.1)
        self.physics.velocity.x = velocity_x
        self.physics.velocity.y = velocity_y
        self.graphics = Graphics(color=(255, 255, 100), scale=2.0 * GLOBAL_SPRITE_SCALE)
        self.collider = Collider(radius=2.0 * GLOBAL_SPRITE_SCALE, is_trigger=True)
        self.lifespan_timer = LifespanTimer(duration=2.0)


class SolarGoldBolt:
    """
    Linear projectile fired by the InquisitionMarksman.
    Travels at high speed toward the swarm and destroys a single minion on contact (1-to-1).
    Uses is_trigger=True so collision_system applies point-attrition logic rather than
    AoE, consistent with how the Boomer's contact trigger is handled.
    Solar-gold visual identity matches the Marksman's crusader aesthetic.
    """
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float):
        self.transform = Transform(x, y)
        # Fast linear travel; mass is negligible so Movement System applies it instantly
        self.physics = Physics(max_speed=600.0, mass=0.1)
        self.physics.velocity.x = velocity_x
        self.physics.velocity.y = velocity_y
        # Solar-gold bolt: distinct warm yellow-gold tint, slightly larger than standard Projectile
        self.graphics = Graphics(color=(255, 210, 60), scale=3.0 * GLOBAL_SPRITE_SCALE)
        # is_trigger=True → collision_system routes this to 1-to-1 minion attrition logic
        self.collider = Collider(radius=3.0 * GLOBAL_SPRITE_SCALE, is_trigger=True)
        # 3-second lifespan cleans up off-screen bolts before they accumulate
        self.lifespan_timer = LifespanTimer(duration=3.0)

        self.projectile_type = 'solar_gold_bolt'
        self.is_enemy = True
