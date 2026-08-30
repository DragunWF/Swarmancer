from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
from components.timers import AimingTimer, FuseTimer, LifespanTimer

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
    def __init__(self, x: float, y: float, blast_radius: float = 120.0):
        self.transform = Transform(x, y)
        # Very slow, heavy sapper — easily kited but devastating on contact
        self.physics = Physics(max_speed=60.0, mass=3.0)
        # Stocky orange silhouette — visually distinct from the smaller Grunt
        self.graphics = Graphics(color=(200, 120, 40), scale=7.0)
        # is_trigger=True signals collision_system to run AoE logic, not 1-to-1 pop
        self.collider = Collider(radius=7.0, is_trigger=True)
        # Fuse: self-detonates after 5s regardless of contact; ticked by behavior_system
        self.fuse_timer = FuseTimer(duration=5.0)

        self.is_enemy = True
        self.enemy_type = 'boomer'
        # AoE blast radius — caller supplies a random value; collision_system reads exclusively
        self.blast_radius = blast_radius
        # Guard flag: set True by collision_system after detonation to prevent re-triggering
        self.has_detonated = False
        # Set True by behavior_system when fuse expires; collision_system reads this
        self.fuse_expired = False
        # Fuse only begins ticking once the Boomer enters this pixel radius of the player cursor
        self.fuse_proximity_radius = 200.0


class LaserDrone:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # No Physics component — stationary by design; behavior_system tracking loop skips it
        # Bright gold wizard-tower appearance
        self.graphics = Graphics(color=(220, 220, 100), scale=8.0)
        # Telegraph timer controls the charge → fire → reset cycle; ticked by behavior_system
        self.aiming_timer = AimingTimer(charge_duration=2.5, fire_duration=0.5)
        # Destroys the drone after a set time so they don't accumulate forever
        self.lifespan_timer = LifespanTimer(duration=15.0)

        self.is_enemy = True
        self.enemy_type = 'laser_drone'
        # Half-width of the laser beam band in pixels — collision_system reads this exclusively
        # Reduced from 80 to 50 (100px total band) for a tighter, fairer punishment window
        self.beam_width = 50.0

