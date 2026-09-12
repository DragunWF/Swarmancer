import random
from components.transform import Transform
from components.graphics import Graphics
from components.timers import LifespanTimer
from components.tracking import TargetTracker

class SiphonParticle:
    def __init__(self, x: float, y: float, target):
        self.transform = Transform(x, y)
        # Randomize initial spread slightly
        self.transform.x += random.uniform(-10, 10)
        self.transform.y += random.uniform(-10, 10)
        
        # Color based on soul siphon theme
        self.graphics = Graphics(color=(150, 50, 255), scale=3.0, sprite_ref=None)
        
        # Short lifespan to ensure it reaches the target quickly
        self.lifespan_timer = LifespanTimer(duration=0.5)
        
        # Tracking the boid
        self.target_tracker = TargetTracker(target=target, speed=400.0, spiral_factor=200.0)
        
        self.marked_for_deletion = False
