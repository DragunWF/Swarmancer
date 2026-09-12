import math
import random
from components.transform import Transform
from components.graphics import Graphics
from components.timers import LifespanTimer
from components.kinetics import ParticleKinetics

class ShatterParticle:
    def __init__(self, x: float, y: float, speed: float, angle: float):
        self.transform = Transform(x, y)
        
        # Varied, larger scale for more prominent pixels
        self.graphics = Graphics(color=(0, 255, 255), scale=random.uniform(3.0, 5.0), sprite_ref=None)
        
        # Slightly longer burst lifespan
        self.lifespan_timer = LifespanTimer(duration=random.uniform(0.4, 0.7))
        
        # Calculate initial velocity vectors
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # High drag value ensures it decelerates rapidly (multiplied per second)
        self.kinetics = ParticleKinetics(vx=vx, vy=vy, drag=0.01)
        self.marked_for_deletion = False
