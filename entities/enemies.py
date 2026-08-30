from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
from components.timers import AimingTimer

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


class Boomer:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # Very slow, heavy sapper — easily kited but devastating on contact
        self.physics = Physics(max_speed=60.0, mass=3.0)
        # Stocky orange silhouette — visually distinct from the smaller Grunt
        self.graphics = Graphics(color=(200, 120, 40), scale=7.0)
        # is_trigger=True signals collision_system to run AoE logic, not 1-to-1 pop
        self.collider = Collider(radius=7.0, is_trigger=True)

        self.is_enemy = True
        self.enemy_type = 'boomer'
        # AoE blast radius in pixels — collision_system reads this exclusively
        self.blast_radius = 120.0
        # Guard flag: set True by collision_system after detonation to prevent re-triggering
        self.has_detonated = False


class LaserDrone:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # No Physics component — stationary by design; behavior_system tracking loop skips it
        # Bright gold wizard-tower appearance
        self.graphics = Graphics(color=(220, 220, 100), scale=8.0)
        # Telegraph timer controls the charge → fire → reset cycle; ticked by behavior_system
        self.aiming_timer = AimingTimer(charge_duration=2.5, fire_duration=0.5)

        self.is_enemy = True
        self.enemy_type = 'laser_drone'
        # Half-width of the laser beam band in pixels — collision_system reads this exclusively
        self.beam_width = 80.0

