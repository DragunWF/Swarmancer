from components.transform import Transform
from components.physics import Physics
from components.graphics import Graphics
from components.collider import Collider
from components.timers import AimingTimer, FuseTimer, LifespanTimer
from settings import GLOBAL_SPRITE_SCALE

# Marksman optimal-distance halt threshold (pixels).
# The Marksman stops advancing when it is within this radius of the swarm centroid/cursor.
# Must never be smaller than the typical melee engagement range so the Marksman
# never accidentally charges into the swarm and triggers a 1-to-1 pop on itself.
MARKSMAN_NEAR_DISTANCE = 180.0

class Grunt:
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # Slower max_speed than Boid (350.0) so they can be kited.
        self.physics = Physics(max_speed=150.0, mass=1.5)
        # Red-ish color, slightly larger scale than boid
        self.graphics = Graphics(sprite_ref="grunt", color=(220, 50, 50), scale=4.0 * GLOBAL_SPRITE_SCALE)
        self.collider = Collider(radius=4.0 * GLOBAL_SPRITE_SCALE)
        
        self.is_enemy = True
        self.enemy_type = 'grunt'


class Boomer:
    def __init__(self, x: float, y: float, blast_radius: float = 120.0):
        self.transform = Transform(x, y)
        # Very slow, heavy sapper — easily kited but devastating on contact
        self.physics = Physics(max_speed=60.0, mass=3.0)
        # Stocky orange silhouette — visually distinct from the smaller Grunt
        self.graphics = Graphics(sprite_ref="dwarf_sapper", color=(200, 120, 40), scale=7.0 * GLOBAL_SPRITE_SCALE)
        # is_trigger=True signals collision_system to run AoE logic, not 1-to-1 pop
        self.collider = Collider(radius=7.0 * GLOBAL_SPRITE_SCALE, is_trigger=True)
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
        self.graphics = Graphics(sprite_ref="sun_wizard", color=(220, 220, 100), scale=8.0 * GLOBAL_SPRITE_SCALE)
        # Telegraph timer controls the charge → fire → reset cycle; ticked by behavior_system
        self.aiming_timer = AimingTimer(charge_duration=2.5, fire_duration=0.5)
        # Destroys the drone after a set time so they don't accumulate forever
        self.lifespan_timer = LifespanTimer(duration=15.0)

        self.is_enemy = True
        self.enemy_type = 'laser_drone'
        # Half-width of the laser beam band in pixels — collision_system reads this exclusively
        # Reduced from 80 to 50 (100px total band) for a tighter, fairer punishment window
        self.beam_width = 50.0


class InquisitionMarksman:
    """
    Advanced ranged crusader.
    Movement: Tracks the swarm centroid/cursor at moderate speed, then halts completely
              once within MARKSMAN_NEAR_DISTANCE pixels to avoid melee range.
    Firing:   Once stationary, AimingTimer increments each frame. On charge_duration peak
              the behavior_system instantiates a SolarGoldBolt and resets the timer.
    Attrition: Standard 1-to-1 Collider (is_trigger=False) — any minion that contacts the
              Marksman directly destroys both entities, identical to Grunt behaviour.
    """
    def __init__(self, x: float, y: float):
        self.transform = Transform(x, y)
        # Moderate speed — fast enough to close distance but slow enough to kite.
        # Intentionally slower than the Grunt (150.0) to compensate for ranged threat.
        self.physics = Physics(max_speed=110.0, mass=1.8)
        # Crusader silhouette — silver-blue holy knight aesthetic
        self.graphics = Graphics(sprite_ref="marksman", color=(180, 210, 255), scale=5.0 * GLOBAL_SPRITE_SCALE)
        # Standard 1-to-1 collider — minion contact destroys both (no AoE trigger)
        self.collider = Collider(radius=5.0 * GLOBAL_SPRITE_SCALE)
        # Telegraph timer: 3s charge → fire → 0.1s flash → reset
        self.aiming_timer = AimingTimer(charge_duration=3.0, fire_duration=0.1)

        self.is_enemy = True
        self.enemy_type = 'marksman'
        # Pre-computed squared halt threshold — avoids sqrt in the behavior system hot loop
        self.near_distance_sq = MARKSMAN_NEAR_DISTANCE * MARKSMAN_NEAR_DISTANCE
        # Set True by behavior_system when the Marksman is within halt range; read externally
        self.is_halted = False

