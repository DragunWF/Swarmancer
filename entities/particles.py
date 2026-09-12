import math
import random
from components.transform import Transform
from components.graphics import Graphics
from components.timers import LifespanTimer
from components.kinetics import ParticleKinetics

class Particle:
    def __init__(self, x: float, y: float, vx: float, vy: float, color: tuple, drag: float = 0.9, duration: float = 0.5, scale: float = None, fade: bool = True):
        self.transform = Transform(x, y)
        if scale is None:
            scale = random.uniform(2.0, 4.0)
        self.graphics = Graphics(color=color, scale=scale, sprite_ref=None)
        self.lifespan_timer = LifespanTimer(duration=duration)
        self.kinetics = ParticleKinetics(vx=vx, vy=vy, drag=drag)
        self.fade = fade
        self.is_particle = True
        self.marked_for_deletion = False
